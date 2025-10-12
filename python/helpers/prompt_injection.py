import re
from typing import Dict, List, Tuple

# Simple, lightweight prompt injection detection utilities (pattern-based)
# This module is dependency-free and safe to import anywhere.

# Compile regex patterns once
INSTRUCTION_OVERRIDE_PATTERNS = [
    re.compile(r"(?i)\b(ignore|forget|disregard)\b\s+(?:any|all|previous|following)?\s*(instructions|rules|guidelines)")
]

HIJACKING_PATTERNS = [
    re.compile(r"(?i)^\s*(stop everything|just\s+(?:say|print|output|write)\b)")
]

JAILBREAK_PATTERNS = [
    re.compile(r"(?i)\b(DAN|DUDE|STAN|Developer\s*Mode|Anti-?DAN)\b"),
    re.compile(r"(?i)(do anything now|broken free of the typical confines|strive to avoid norms)")
]

AUTHORITY_PATTERNS = [
    re.compile(r"(?i)\byou are (now )?(?:an?|the)\s+(?:expert|authority|official|terminal|interpreter)"),
    re.compile(r"(?i)\bact as (?:an?|the)\s+(?:system|admin|root|sudo|developer|terminal|console|interpreter|compiler)")
]

FORMATTING_TRICKS = [
    re.compile(r"\n{5,}"),  # excessive newlines
]

ZERO_WIDTH_CHARS = re.compile(r"[\u200B-\u200F\u2060-\u2064\uFEFF]")

LETTER_SCATTERING = re.compile(r"(?i)^(?:[a-z]\s+){6,}[a-z]$")

MIXED_SCRIPT_HOMOGLYPHS = re.compile(r"[\u0400-\u04FF\u0530-\u058F\u13A0-\u13FF]")  # Cyrillic/Armenian/Cherokee


def _score(matches: Dict[str, int]) -> float:
    """Compute a simple risk score in [0,1] based on matched categories."""
    weights = {
        "instruction_override": 0.8,
        "hijacking": 0.9,
        "jailbreak": 0.7,
        "authority": 0.6,
        "formatting": 0.3,
        "zero_width": 0.6,
        "letter_scatter": 0.5,
        "mixed_script": 0.5,
    }
    score = 0.0
    for k, n in matches.items():
        score += min(1, n) * weights.get(k, 0.0)
    return min(1.0, score)


def detect_input_text(text: str) -> Dict:
    """Detect potential prompt injection in user input.
    Returns: {
      'risk_score': float,
      'signals': Dict[str, int],
      'triggers': List[str]
    }
    """
    if not text:
        return {"risk_score": 0.0, "signals": {}, "triggers": []}

    signals: Dict[str, int] = {}
    triggers: List[str] = []

    for rx in INSTRUCTION_OVERRIDE_PATTERNS:
        if rx.search(text):
            signals["instruction_override"] = signals.get("instruction_override", 0) + 1
            triggers.append("instruction_override")
    for rx in HIJACKING_PATTERNS:
        if rx.search(text):
            signals["hijacking"] = signals.get("hijacking", 0) + 1
            triggers.append("hijacking")
    for rx in JAILBREAK_PATTERNS:
        if rx.search(text):
            signals["jailbreak"] = signals.get("jailbreak", 0) + 1
            triggers.append("jailbreak")
    for rx in AUTHORITY_PATTERNS:
        if rx.search(text):
            signals["authority"] = signals.get("authority", 0) + 1
            triggers.append("authority")
    for rx in FORMATTING_TRICKS:
        if rx.search(text):
            signals["formatting"] = signals.get("formatting", 0) + 1
            triggers.append("formatting_newlines")
    if ZERO_WIDTH_CHARS.search(text):
        signals["zero_width"] = signals.get("zero_width", 0) + 1
        triggers.append("zero_width_chars")
    # Heuristic letter scattering: many letters separated by whitespace or newlines
    if LETTER_SCATTERING.search(text.strip().replace("\n", " ")):
        signals["letter_scatter"] = signals.get("letter_scatter", 0) + 1
        triggers.append("letter_scattering")
    if MIXED_SCRIPT_HOMOGLYPHS.search(text):
        signals["mixed_script"] = signals.get("mixed_script", 0) + 1
        triggers.append("mixed_script_homoglyphs")

    risk = _score(signals)
    return {"risk_score": risk, "signals": signals, "triggers": triggers}


def detect_output_text(text: str) -> Dict:
    """Detect potential prompt injection symptoms in model output.
    Similar rules as input, with extra emphasis on hijacking phrases.
    """
    return detect_input_text(text)


HIGH_RISK_THRESHOLD = 0.6
MEDIUM_RISK_THRESHOLD = 0.4