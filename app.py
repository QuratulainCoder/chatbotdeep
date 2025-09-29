from flask import Flask, render_template, request, jsonify
import json
import random
import re
from difflib import SequenceMatcher, get_close_matches

app = Flask(__name__)

# --- Load intents ---
with open("intents.json", "r", encoding="utf-8") as f:
    intents = json.load(f).get("intents", [])


# --- Utilities ---
def normalize_text(text):
    """Lowercase, remove punctuation, normalize whitespace"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # remove punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text


def similar(a, b):
    """Return similarity ratio between two strings"""
    return SequenceMatcher(None, a, b).ratio()


# small mapping of roman-urdu synonyms -> english keywords to help matching
SYNONYMS = {
    "program": [
        "program", "programs", "programme", "programmes", "programs?",
        "programs"
    ],
    "apply":
    ["apply", "apply?", "applying", "darakhast", "apply kar", "apply kro"],
    "admission": ["admission", "admissions", "dakhla", "dakhla?"],
    "deadline": [
        "deadline", "last date", "lastdate", "last-date", "akhir tareekh",
        "last"
    ],
    "scholarship": ["scholarship", "scholarships"],
    "which": ["which", "kon", "kaun", "kis"],
    "do": ["do", "kya", "krna", "karta", "karein", "karo"],
    "you": ["you", "aap", "tum"],
}

KEYWORD_TO_ROOT = {}
for root, words in SYNONYMS.items():
    for w in words:
        KEYWORD_TO_ROOT[w] = root

# Known program names (used to fill {program_name})
KNOWN_PROGRAMS = [
    "software engineering",
    "computer science",
    "business administration",
    "bs software engineering",
    "bs computer science",
    "bs business administration",
    # add more program names you support...
]


def detect_program_name(user_text_norm):
    """Try to find a known program in user input; return normalized program string or None."""
    for prog in KNOWN_PROGRAMS:
        if prog in user_text_norm:
            # title-case nicely for reply
            return " ".join([w.capitalize() for w in prog.split()])
    # fallback heuristics
    if "software" in user_text_norm and "engineering" in user_text_norm:
        return "Software Engineering"
    if "computer" in user_text_norm and "science" in user_text_norm:
        return "Computer Science"
    # try single-word program detection
    for prog in KNOWN_PROGRAMS:
        tokens = prog.split()
        if any(t in user_text_norm for t in tokens):
            return " ".join([w.capitalize() for w in prog.split()])
    return None


# --- Intent matching ---
def get_intent_response(user_text):
    user_norm = normalize_text(user_text)

    # 1) Exact normalized substring match
    for intent in intents:
        for pattern in intent.get("patterns", []):
            pattern_norm = normalize_text(pattern)
            if pattern_norm and pattern_norm in user_norm:
                return random.choice(intent.get("responses", []))

    # 2) Token overlap (keyword-based)
    user_tokens = set(user_norm.split())
    for intent in intents:
        for pattern in intent.get("patterns", []):
            pattern_norm = normalize_text(pattern)
            pattern_tokens = set(pattern_norm.split())
            overlap = len(user_tokens & pattern_tokens)
            if overlap >= 1:
                return random.choice(intent.get("responses", []))

    # 3) Fuzzy similarity between whole strings
    best = (None, 0.0, None)  # (intent, score, pattern)
    for intent in intents:
        for pattern in intent.get("patterns", []):
            pattern_norm = normalize_text(pattern)
            if not pattern_norm:
                continue
            score = similar(user_norm, pattern_norm)
            if score > best[1]:
                best = (intent, score, pattern_norm)
    if best[1] >= 0.55 and best[0] is not None:  # threshold
        return random.choice(best[0]["responses"])

    # 4) Close word matches using difflib
    for intent in intents:
        for pattern in intent.get("patterns", []):
            pattern_norm = normalize_text(pattern)
            pattern_words = pattern_norm.split()
            for pw in pattern_words:
                close = get_close_matches(pw,
                                          list(user_tokens),
                                          n=1,
                                          cutoff=0.75)
                if close:
                    return random.choice(intent.get("responses", []))

    # fallback
    return "Sorry, I did not understand that. Can you rephrase?"


# --- Format response ---
def format_response(user_text, bot_response):
    """
    Always return English responses (user requested).
    Fill placeholders like {program_name} from user text when possible.
    """
    user_norm = normalize_text(user_text)
    program_name = detect_program_name(user_norm)
    if "{program_name}" in bot_response:
        if program_name:
            bot_response = bot_response.replace("{program_name}", program_name)
        else:
            bot_response = bot_response.replace("{program_name}",
                                                "this program")
    return bot_response


# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    # Use request.get_json to avoid AttributeError when request.json is None
    data = request.get_json(silent=True) or {}
    user_input = data.get("message", "") or ""
    user_input = str(user_input).strip()[:1000]  # safety truncation
    response = get_intent_response(user_input)
    response = format_response(user_input, response)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
