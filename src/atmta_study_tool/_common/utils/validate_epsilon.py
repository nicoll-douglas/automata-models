from atmta_study_tool.language import Word


def validate_epsilon(word: Word):
    """Validate the given word is equalt to the empty word epsilon."""
    if word != Word.EPSILON:
        raise ValueError(f"Expected a word equal to epsilon. Got {word!r}.")
