import re


ABBREVIATION_DICTIONARY = {
    "BX": "Beam in X",
    "BY": "Beam in Y",
    "BZ": "Beam in Z",

    "CX": "Column in X (Left)",
    "CY": "Column in X (Right)",
    "CZ": "Column in X (Middle)",

    "B2X": "Beam no.2 in X",
    "B2Y": "Beam no.2 in Y",
    "B2Z": "Beam no.2 in Z",

    "C2X": "Column no.2 in X (Left)",
    "C2Y": "Column no.2 in X (Right)",
    "C2Z": "Column no.2 in X (Middle)",

    "CO": "Cover",
    "BR": "Bar",
    "D": "Dia",

    "GC": "Grade of Concrete",
    "GS": "Grade of Steel",

    "SS": "Spacing of Stirrups",
    "SD": "Stirrups Dia",
    "LS": "Leg of Stirrups",

    "LD": "GC/GS",
    "BN": "Bend Numbers",
    "BD": "Bend Deduction"
}


MATH_FUNCTIONS = {
    "MIN",
    "MAX",
    "ROUND",
    "ABS",
    "SQRT",
    "POW"
}


def get_abbreviation_meaning(short_name: str):
    if not short_name:
        return None

    return ABBREVIATION_DICTIONARY.get(short_name.strip().upper())


def extract_formula_tokens(formula: str):
    if not formula:
        return []

    return re.findall(r"\b[A-Za-z][A-Za-z0-9]*\b", formula.upper())


def extract_abbreviations_from_formula(formula: str):
    if not formula:
        return []

    tokens = extract_formula_tokens(formula)

    result = []
    already_added = set()

    for token in tokens:
        if token in MATH_FUNCTIONS:
            continue

        if token in ABBREVIATION_DICTIONARY and token not in already_added:
            result.append({
                "short_name": token,
                "full_form": ABBREVIATION_DICTIONARY[token]
            })
            already_added.add(token)

    return result


def find_unknown_abbreviations_in_formula(formula: str):
    """
    Finds unknown formula tokens.

    Example:
    min(BXX, BY) - (2 * CO)

    returns:
    ["BXX"]

    Valid:
    BX, BY, CO, LD, etc.
    Ignored:
    min, max, round, abs, sqrt, pow
    """

    if not formula:
        return []

    tokens = extract_formula_tokens(formula)

    unknown_terms = []
    already_added = set()

    for token in tokens:
        if token in MATH_FUNCTIONS:
            continue

        if token not in ABBREVIATION_DICTIONARY:
            if token not in already_added:
                unknown_terms.append(token)
                already_added.add(token)

    return unknown_terms


def get_valid_abbreviation_list():
    return sorted(ABBREVIATION_DICTIONARY.keys())