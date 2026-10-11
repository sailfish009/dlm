from dlm.lexicon import PredicateLexicon, reducible_forms, third_person, verb_lemma


def test_verb_lemma_irregular():
    assert verb_lemma("is") == "be"
    assert verb_lemma("went") == "go"
    assert verb_lemma("saw") == "see"


def test_verb_lemma_regular():
    assert verb_lemma("calls") == "call"
    assert verb_lemma("watches") == "watch"
    assert verb_lemma("studies") == "study"


def test_lexicon_resolves_doubled_consonant_and_e_stem():
    # over-generating reductions are harmless: the declared form is what wins
    assert PredicateLexicon(["stop"]).lemma("stopped") == "stop"
    assert PredicateLexicon(["make"]).lemma("making") == "make"


def test_third_person():
    assert third_person("call") == "calls"
    assert third_person("watch") == "watches"
    assert third_person("study") == "studies"
    assert third_person("go") == "goes"
    assert third_person("be") == "is"


def test_lexicon_lemma_is_membership_gated():
    lex = PredicateLexicon(["call", "like", "happy"])
    assert lex.lemma("calls") == "call"
    assert lex.lemma("liked") == "like"
    assert lex.lemma("happy") == "happy"
    # not declared -> not a predicate (so it is an entity)
    assert lex.lemma("flies") is None
    assert lex.lemma("alice") is None
    assert lex.lemma("james") is None


def test_lexicon_e_suffix_prefers_membership():
    lex = PredicateLexicon(["like"])
    # "likes" reduces to "lik" first, then "like"; only the latter is declared
    assert lex.lemma("likes") == "like"


def test_lexicon_canonical_and_is_pred():
    lex = PredicateLexicon(["call"])
    assert lex.is_pred("calls") is True
    assert lex.is_pred("tokyo") is False
    assert lex.canonical("calls") == "call"
    assert lex.canonical("tokyo") == "tokyo"
    assert "calls" in lex and "tokyo" not in lex


def test_reducible_forms_nonempty_for_inflections():
    assert "call" in reducible_forms("calls")
    assert "study" in reducible_forms("studies")