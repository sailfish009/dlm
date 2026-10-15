"""Dataset domain knowledge -- the GIVEN vocabulary for the model's search.

The *library* acquisition (``knowledge.py``) learns what a symbol means.  That is
still not enough to say what a program *recognizes*: the code instantiates
``datasets.MNIST``, but the meaning of that dataset -- "a database of handwritten
digits" -- is neither in the code nor in a symbol's own definition.  The model
SEARCHES for it (Wikipedia primary, Stack Exchange fallback) and reduces the
prose to a domain ENTITY.

As with ``knowledge.py``, the subject lives in the MODEL (:mod:`dlm.acquire`);
this module supplies only the GIVEN vocabulary -- the cue lexicon, the
dataset-looking hints, and the readable phrase map -- plus the compatibility
surface the experiments already call.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from dlm.acquire import EntityVocabulary
from dlm.acquire import acquire_domain_entities, domain_facts
from dlm.acquire import dataset_candidates as _dataset_candidates
from dlm.search import reduce_text

__all__ = [
    "DOMAIN_VERSION", "DATASET_HINTS", "DATASET_CUES", "ENTITY_PHRASES",
    "DOMAIN_VOCAB", "dataset_candidates", "reduce_entity", "acquire_domain",
    "domain_facts",
]

DOMAIN_VERSION = 2

# A reduction heuristic ("what to ASK about"), not knowledge: dataset-looking
# constructors.  A symbol is a dataset candidate if its label mentions "dataset"
# or one of the well-known vision dataset names.
DATASET_HINTS: Tuple[str, ...] = (
    "mnist", "fashion", "cifar", "kmnist", "imagenet", "coco", "voc",
    "caltech", "svhn", "stl", "omniglot", "usps", "emnist",
)

# Free-text cues (definitions / Q&A titles) -> the domain ENTITY a dataset
# records.  Order is disambiguation priority: specific before generic.
DATASET_CUES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("handwritten_digit", ("handwritten digit", "hand-written digit", "hand written digit",
                           "digit recognition", "digits 0-9", "digits and",
                           "digits are", "handwritten number")),
    ("clothing_item", ("fashion", "clothing", "garment", "apparel")),
    ("character", ("character recognition", "characters", "letters")),
    ("object_category", ("object categor", "object class", "categories of object",
                         "object recognition", "image classification",
                         "different classes", "classes represent", "100 classes",
                         "10 classes")),
    ("natural_image", ("natural image", "photograph", "color image")),
)

# entity slug -> a readable phrase for the realizer (untrusted gloss vocabulary).
ENTITY_PHRASES: Dict[str, str] = {
    "handwritten_digit": "handwritten digits",
    "clothing_item": "clothing items",
    "character": "characters",
    "object_category": "object categories",
    "natural_image": "natural images",
}

# The GIVEN vocabulary handed to the model's acquisition subject.
DOMAIN_VOCAB = EntityVocabulary(
    entity_cues=DATASET_CUES,
    dataset_hints=DATASET_HINTS,
    dataset_word="dataset",
    entity_phrases=ENTITY_PHRASES,
    search_site="stackoverflow",
    search_prefix="pytorch",
    record_name="domain_knowledge.json",
)


# -- compatibility shims over the model layers ------------------------------
def dataset_candidates(facts: List[tuple], labels: Dict[str, str]) -> Dict[str, str]:
    """Dataset-looking instances the code creates: ``{slug: label}``.

    A reduction for the *question* only -- it never says what the dataset is.
    """
    return _dataset_candidates(facts, labels, DATASET_HINTS, "dataset")


def reduce_entity(text: str) -> Optional[str]:
    return reduce_text(text, DATASET_CUES)


def acquire_domain(candidates: Dict[str, str], cache_dir: str,
                   offline: bool = False, search: bool = True) -> dict:
    """Search for what each dataset candidate contains; cache reduced records.

    Delegates to the model's acquisition subject; this function only supplies the
    GIVEN vocabulary.
    """
    return acquire_domain_entities(candidates, cache_dir, DOMAIN_VOCAB,
                                   version=DOMAIN_VERSION, offline=offline,
                                   search=search)