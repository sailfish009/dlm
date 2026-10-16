"""Append-only IR transition journal with validated snapshot replay."""
from __future__ import annotations

import json
import os
from pathlib import Path

from .ir import (Form, canonical_json, field, from_json, node_id, save,
                 validate_model_state, validate_transition)
from .learn import commit_transition


class Store:
    """The snapshot and journal contain IR only; index.json is disposable cache."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.snapshot = self.root / "snapshot.ir.json"
        self.journal = self.root / "experience.irlog"
        self.index = self.root / "index.json"

    def create(self, state: Form, *, overwrite: bool = False) -> None:
        validate_model_state(state)
        self.root.mkdir(parents=True, exist_ok=True)
        if self.snapshot.exists() and not overwrite:
            raise FileExistsError(self.snapshot)
        self._atomic_snapshot(state)
        if overwrite or not self.journal.exists():
            self.journal.write_text("")
        self._write_index(state, 0)

    def exists(self) -> bool:
        return self.snapshot.exists()

    def load(self) -> Form:
        if not self.snapshot.exists():
            raise FileNotFoundError(self.snapshot)
        state = from_json(self.snapshot.read_text())
        validate_model_state(state)
        count = 0
        if self.journal.exists():
            for number, line in enumerate(self.journal.read_text().splitlines(), 1):
                if not line.strip():
                    continue
                transition = from_json(line)
                try:
                    validate_transition(transition)
                    state = commit_transition(state, transition)
                except Exception as error:
                    raise ValueError(f"invalid journal transition at line {number}") from error
                count += 1
        self._write_index(state, count)
        return state

    def append(self, state: Form, transition: Form) -> Form:
        """Verify the disk tip and transition before making it durable."""
        self.root.mkdir(parents=True, exist_ok=True)
        if not self.snapshot.exists():
            self.create(state)
        elif self._tip_id() != node_id(state):
            raise ValueError("append state is not the current journal tip")
        after = commit_transition(state, transition)
        with self.journal.open("a", encoding="utf-8") as stream:
            stream.write(canonical_json(transition) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        count = sum(1 for line in self.journal.read_text().splitlines() if line.strip())
        self._write_index(after, count)
        return after

    def _tip_id(self) -> str:
        lines = [line for line in self.journal.read_text().splitlines() if line.strip()] \
            if self.journal.exists() else []
        if lines:
            last = from_json(lines[-1])
            validate_transition(last)
            return node_id(field(last, "after")[1])
        snapshot = from_json(self.snapshot.read_text())
        validate_model_state(snapshot)
        return node_id(snapshot)

    def checkpoint(self, state: Form) -> None:
        """Keep old journal as an immutable archive and begin a new segment."""
        validate_model_state(state)
        self.root.mkdir(parents=True, exist_ok=True)
        if self.snapshot.exists() and self._tip_id() != node_id(state):
            raise ValueError("checkpoint state is not the current journal tip")
        segment = 0
        while (self.root / f"experience.{segment}.irlog").exists():
            segment += 1
        if self.journal.exists() and self.journal.stat().st_size:
            self.journal.replace(self.root / f"experience.{segment}.irlog")
        self._atomic_snapshot(state)
        self.journal.write_text("")
        self._write_index(state, 0)

    def _atomic_snapshot(self, state: Form) -> None:
        temporary = self.root / "snapshot.ir.json.tmp"
        save(temporary, state)
        temporary.replace(self.snapshot)

    def _write_index(self, state: Form, transitions: int) -> None:
        theory = field(state, "theory")
        decision = field(state, "decision")
        memory = field(state, "memory")[1:]
        data = {
            "root": node_id(state),
            "round": field(state, "round")[1],
            "ground": len(field(theory, "ground")) - 1,
            "experience": len(field(theory, "experience")) - 1,
            "experience_records": len(memory),
            "retracted": sum(field(record, "status")[1] == "retracted" for record in memory),
            "decision_updates": field(decision, "updates")[1],
            "events": len(field(state, "events")) - 1,
            "journal_transitions": transitions,
        }
        temporary = self.root / "index.json.tmp"
        temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        temporary.replace(self.index)
