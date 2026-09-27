"""
Classifies violations and complaints into safety categories
using the complaint category codes and keywords in violation text.
"""

FIRE_CODES = {"44", "52", "56", "57", "58", "37", "38", "39", "2C", "2D"}
ELEVATOR_CODES = {"13", "62", "63", "64", "80", "81", "6M", "6S"}
STRUCTURAL_SHED_CODES = {
    "3", "10", "14", "16", "21", "22", "23", "24", "28", "29", "30",
    "40", "41", "43", "54", "84", "88", "93", "2K", "2L", "5C", "5D",
    "1E", "1G", "1F", "67", "68", "69",
}

FIRE_KEYWORDS = ["BOILER", "FIRE", "SPRINKLER", "SMOKE", "EGRESS"]
ELEVATOR_KEYWORDS = ["ELEVATOR"]
STRUCTURAL_SHED_KEYWORDS = [
    "SHED", "SCAFFOLD", "FACADE", "STRUCTURAL", "UNSAFE", "SWARMP", "CRANE",
]


def classify_complaint(category_code) -> str:
    code = str(category_code).strip()
    if code in FIRE_CODES:
        return "fire"
    if code in ELEVATOR_CODES:
        return "elevator"
    if code in STRUCTURAL_SHED_CODES:
        return "structural"
    return "other"


def classify_violation(description) -> str:
    text = str(description).upper()
    if any(k in text for k in FIRE_KEYWORDS):
        return "fire"
    if any(k in text for k in ELEVATOR_KEYWORDS):
        return "elevator"
    if any(k in text for k in STRUCTURAL_SHED_KEYWORDS):
        return "structural"
    return "other"