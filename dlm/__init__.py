"""DLM 0.0.65: typed IR-TREE is the one model and learning medium.

Persistent authority is one immutable model-state Form. Python objects are only
trusted-kernel projections; TreeLisp is a bounded controller that can request
transitions but cannot commit or assert facts or rules directly.
"""
from .ir import (Form, IRValidationError, canonical_json, dag_index, dump, field,
                 from_json, load, loads, node_id, save, validate_model_state,
                 validate_transition)
from .kernel import (Atom, Rule, atom_from_ir, atom_to_ir, closure, episode_ir,
                     prove, query, rule_from_ir, rule_to_ir, safe, state_prove,
                     verify_proof)
from .language import (default_language, execute_programs, program_origins,
                       update_program_stats, validate_language, validate_program)
from .learn import (GroundConflict, choice, commit_transition, evaluate,
                    learn_round, new_state, noul, observe, ordinal_score, rank,
                    stop_status, synthesize)
from .pyir import call_facts, lower_paths, source_hash, validate_pyir
from .speech import realize
from .store import Store
from .treelisp import EvalError, evaluate_expr, run

__version__ = "0.0.65"

__all__ = [
    "Form", "IRValidationError", "canonical_json", "dag_index", "dump", "field",
    "from_json", "load", "loads", "node_id", "save", "validate_model_state",
    "validate_transition",
    "Atom", "Rule", "atom_from_ir", "atom_to_ir", "closure", "episode_ir", "prove",
    "query", "rule_from_ir", "rule_to_ir", "safe", "state_prove", "verify_proof",
    "default_language", "execute_programs", "program_origins", "update_program_stats",
    "validate_language",
    "validate_program", "GroundConflict", "choice",
    "commit_transition", "evaluate", "learn_round", "new_state", "noul", "observe",
    "ordinal_score", "rank", "stop_status", "synthesize", "call_facts", "lower_paths",
    "source_hash", "validate_pyir", "realize", "Store", "EvalError", "evaluate_expr", "run",
]
