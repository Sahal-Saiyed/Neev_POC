import re
from simpleeval import simple_eval


CONCRETE_GRADE_VALUES = {
    "M20": 20,
    "M25": 25,
    "M30": 30,
    "M35": 35,
    "M40": 40
}


STEEL_GRADE_VALUES = {
    "Fe415": 415,
    "Fe500": 500
}


LD_MULTIPLIER = {
    ("M20", "Fe415"): 47,
    ("M20", "Fe500"): 50,
    ("M25", "Fe415"): 44,
    ("M25", "Fe500"): 47,
    ("M30", "Fe415"): 40,
    ("M30", "Fe500"): 44,
    ("M35", "Fe415"): 38,
    ("M35", "Fe500"): 42,
    ("M40", "Fe415"): 36,
    ("M40", "Fe500"): 40
}


def parse_bar_dia(bar_dia: str):
    """
    Example:
    2-T12   -> BR = 2, D = 12
    4-T20   -> BR = 4, D = 20
    3-T12EF -> BR = 3, D = 12
    """

    match = re.search(r"(\d+)-T(\d+)", bar_dia)

    if not match:
        return 0, 0

    bar = int(match.group(1))
    dia = int(match.group(2))

    return bar, dia


def calculate_ld(grade_of_concrete: str, grade_of_steel: str, dia: int):
    multiplier = LD_MULTIPLIER.get(
        (grade_of_concrete, grade_of_steel),
        45
    )

    return multiplier * dia


def calculate_shape_outputs(shape, variables):
    outputs = []

    for output in shape.get("outputs", []):
        formula = output.get("formula")

        try:
            value_in_mm = simple_eval(
                formula,
                names=variables,
                functions={
                    "max": max,
                    "min": min
                }
            )

            value_in_meter = value_in_mm / 1000

            outputs.append({
                "output_name": output.get("output_name"),
                "value": round(value_in_meter, 3),
                "unit": output.get("unit", "m"),
                "formula_used": formula,
                "formula_source": output.get("formula_source", "global")
            })

        except Exception as e:
            outputs.append({
                "output_name": output.get("output_name"),
                "value": None,
                "unit": output.get("unit", "m"),
                "formula_used": formula,
                "formula_source": output.get("formula_source", "global"),
                "error": str(e)
            })

    return outputs