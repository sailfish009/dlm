"""DLM — Deductive Logic Model.

v0.0002 is a System-One decision engine: it answers `noul` / `choice` / `score`
questions by interpreting options to logical atoms and deciding by deduction,
replacing an LLM torso plus a learned head on closed, groundable views.

    LLM = Large   + Language + Model   (inductive statistics)
    VLM = Vision  + Language + Model
    DLM = Deductive + Logic  + Model   (induce rules, then deduce and decide)

Decision path: interpret options -> query KB -> proof-based scores -> tiny
calibration. No tokenizer, no LoRA, no LM head, no vision tower.
"""
from __future__ import annotations

from .decider import Decider, torch_decider
from .adapter import (
    FEATURE_NAMES,
    DlmTorso,
    SystemOneService,
    parse_request,
    response_to_dict,
)
from .decision import DecisionEngine, OptionScore, softmax
from .deduce import Engine, Proof, Solution
from .generalize import induce_rules, lgg_atoms
from .interpreter import (
    ChainInterpreter,
    GroundingInterpreter,
    Interpreter,
    ParseError,
    ParsedOption,
    SchemaInterpreter,
    parse_atom,
)
from .kb import KnowledgeBase
from .pipeline import Pipeline, PipelineResult, collect_training_data
from .retrieval import Candidate, Retriever, feature_vector
from .rules import Rule, fact, rule
from .schema import (
    Answer,
    ChoiceAnswer,
    ChoiceQuestion,
    NoulAnswer,
    NoulQuestion,
    Question,
    ScoreAnswer,
    ScoreQuestion,
    SystemOneRequest,
    SystemOneResponse,
    Usage,
    derive_confidence,
    derive_score_confidence,
)
from .grounding import ChainGrounder, GrammarGrounder, Grounder, Grounding, Pattern
from .byte_tokenizer import ByteTokenizer
from .tiny_encoder import TinyEncoder, TinyEncoderConfig, build_encoder
from .grounder_learn import (
    AtomIndex,
    CharNgramGrounder,
    DEFAULT_ENTITIES,
    LearnedGrounder,
    ProjectionHead,
    TrainReport,
    pattern_split,
    synthesize_pairs,
)
from .terms import Atom, Const, Subst, Term, Var, atom, substitute_atom, unify, unify_atom
from .dialogue import DialogueSession, Reply, Verbalizer

__version__ = "0.0.3"

__all__ = [
    "Atom", "Const", "Subst", "Term", "Var", "atom", "substitute_atom", "unify",
    "unify_atom", "Rule", "fact", "rule", "KnowledgeBase", "Engine", "Proof",
    "Solution", "induce_rules", "lgg_atoms", "Candidate", "Retriever",
    "feature_vector", "Decider", "torch_decider", "Pipeline", "PipelineResult",
    "collect_training_data", "Answer", "ChoiceAnswer", "ChoiceQuestion",
    "NoulAnswer", "NoulQuestion", "Question", "ScoreAnswer", "ScoreQuestion",
    "SystemOneRequest", "SystemOneResponse", "Usage", "derive_confidence",
    "derive_score_confidence", "DecisionEngine", "OptionScore", "softmax",
    "ChainInterpreter", "GroundingInterpreter", "Interpreter", "ParseError",
    "ParsedOption", "SchemaInterpreter", "parse_atom", "__version__",
    "DlmTorso", "SystemOneService", "parse_request", "response_to_dict",
    "FEATURE_NAMES", "GrammarGrounder", "ChainGrounder", "Grounder", "Grounding", "Pattern",
    "ByteTokenizer",
    "TinyEncoder", "TinyEncoderConfig", "build_encoder",
    "ProjectionHead", "AtomIndex", "LearnedGrounder", "CharNgramGrounder",
    "TrainReport", "synthesize_pairs", "pattern_split", "DEFAULT_ENTITIES",
    "DialogueSession", "Reply", "Verbalizer",
]