from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import json
from datetime import datetime

app = FastAPI(
    title="TataramonTech API",
    description="English to Central Bikol Translation API using Apertium RBMT",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_DIR = os.path.expanduser("~/ony-eng-bcl")
FEEDBACK_FILE = os.path.expanduser("~/ony-eng-bcl/feedback.json")


class FeedbackRequest(BaseModel):
    input_text: str
    translated_text: str
    direction: str
    rating: int
    comment: str = ""


def run_apertium(text, direction):
    result = subprocess.run(
        ["apertium", "-d", PROJECT_DIR, "-n", direction],
        input=text, capture_output=True, text=True
    )
    return result.stdout.strip()


def run_morph(text, direction):
    bin_file = os.path.join(PROJECT_DIR,
        "eng-bcl.automorf.bin" if direction == "eng-bcl" else "bcl-eng.automorf.bin")
    result = subprocess.run(
        ["lt-proc", bin_file],
        input=text, capture_output=True, text=True
    )
    return result.stdout.strip()


def parse_pos(morph_output):
    tokens = []
    for token in morph_output.split("$"):
        token = token.strip().lstrip("^")
        if not token:
            continue
        if "/" in token:
            surface, analyses = token.split("/", 1)
            first = analyses.split("/")[0]
            tags = [t.strip("<>") for t in first.split("<") if t.strip("<>")]
            pos = tags[0] if tags else "unknown"
            tokens.append({"word": surface, "pos": pos, "tags": tags})
    return tokens


@app.get("/")
def root():
    return {"message": "TataramonTech API is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/pairs")
def pairs():
    return {
        "pairs": [
            {"from": "eng", "to": "bcl", "direction": "eng-bcl", "label": "English to Central Bikol"},
            {"from": "bcl", "to": "eng", "direction": "bcl-eng", "label": "Central Bikol to English"}
        ]
    }


@app.get("/translate")
def translate(text: str, direction: str = "eng-bcl"):
    if direction not in ["eng-bcl", "bcl-eng"]:
        raise HTTPException(status_code=400, detail="direction must be eng-bcl or bcl-eng")
    try:
        output = run_apertium(text, direction)
        return {"input": text, "output": output, "direction": direction, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/translate/pos")
def translate_with_pos(text: str, direction: str = "eng-bcl"):
    if direction not in ["eng-bcl", "bcl-eng"]:
        raise HTTPException(status_code=400, detail="direction must be eng-bcl or bcl-eng")
    try:
        output = run_apertium(text, direction)
        morph = run_morph(text, direction)
        pos_tags = parse_pos(morph)
        return {
            "input": text,
            "output": output,
            "direction": direction,
            "pos_tags": pos_tags,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phrasebook")
def phrasebook(category: str = "all"):
    phrases = {
        "greetings": [
            {"english": "Good morning", "bikol": "Maogmang aga"},
            {"english": "Good afternoon", "bikol": "Maogmang hapon"},
            {"english": "How are you", "bikol": "Kumusta ka"},
        ],
        "common": [
            {"english": "house", "bikol": "harong"},
            {"english": "fish", "bikol": "sira"},
            {"english": "water", "bikol": "tubig"},
        ],
        "verbs": [
            {"english": "walk", "bikol": "lakaw"},
            {"english": "eat", "bikol": "kaon"},
            {"english": "run", "bikol": "dalagan"},
        ]
    }
    if category == "all":
        return {"phrases": phrases}
    if category not in phrases:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"category": category, "phrases": phrases[category]}


@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    if not 1 <= feedback.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": feedback.input_text,
        "translation": feedback.translated_text,
        "direction": feedback.direction,
        "rating": feedback.rating,
        "comment": feedback.comment
    }
    existing = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            existing = json.load(f)
    existing.append(entry)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(existing, f, indent=2)
    return {"status": "success", "message": "Feedback saved. Salamat!"}


@app.get("/feedback")
def get_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        return {"feedback": [], "total": 0}
    with open(FEEDBACK_FILE, "r") as f:
        data = json.load(f)
    return {"feedback": data, "total": len(data)}
