"""Deterministic intake ordering, completeness checks, and review fingerprints."""
from hashlib import sha256
import json

STATUSES = {"answered", "proposed"}
PLACEHOLDERS = {"", "tbd", "todo", "unknown", "recommend", "not sure", "?"}


def load_catalog(root):
    catalog = json.loads((root / "config/intake/questions.json").read_text())
    questions = [q for group in catalog["groups"] for q in group["questions"]]
    ids = [q["id"] for q in questions]
    if len(set(ids)) != len(ids) or catalog["max_batch_size"] not in (1, 2, 3):
        raise ValueError("Intake catalog has duplicate IDs or an invalid batch limit")
    seen = set()
    for q in questions:
        if "when" in q and q["when"]["question"] not in seen:
            raise ValueError("Intake conditions must reference an earlier question")
        seen.add(q["id"])
    return catalog


def new_state(brief):
    if not brief.strip():
        raise ValueError("Supply the user's initial business request")
    return {"version": 1, "business_prompt": brief, "answers": {}, "confirmed_fingerprint": None}


def question_map(catalog):
    return {q["id"]: q for g in catalog["groups"] for q in g["questions"]}


def validate_state(catalog, state):
    if (not isinstance(state, dict) or state.get("version") != 1
            or not isinstance(state.get("business_prompt"), str) or not state["business_prompt"].strip()
            or not isinstance(state.get("answers"), dict)):
        raise ValueError("Invalid intake state")
    questions = question_map(catalog)
    for key, answer in state["answers"].items():
        if key not in questions:
            raise ValueError("Unknown intake question: " + key)
        if not isinstance(answer, dict):
            raise ValueError("Invalid answer record")
        if answer.get("status") not in STATUSES or answer.get("source") not in {"user", "brief", "agent"}:
            raise ValueError("Invalid answer status or provenance")
        value = answer.get("value")
        if not isinstance(value, str) or value.strip().lower() in PLACEHOLDERS:
            raise ValueError("Supply a concrete answer or leave the question pending")
        if "choices" in questions[key] and value not in questions[key]["choices"]:
            raise ValueError("Answer must match a catalog choice")
        if answer["source"] == "agent" and answer["status"] != "proposed":
            raise ValueError("Agent recommendations must remain proposed until brief confirmation")


def active(question, answers):
    condition = question.get("when")
    return not condition or answers.get(condition["question"], {}).get("value") == condition["equals"]


def answer(catalog, state, question_id, value, *, status="answered", source="user"):
    if question_id not in question_map(catalog):
        raise ValueError("Unknown intake question: " + question_id)
    candidate = {**state, "answers": {**state["answers"], question_id: {
        "value": value.strip(), "status": status, "source": source}}, "confirmed_fingerprint": None}
    validate_state(catalog, candidate)
    return candidate


def fingerprint(catalog, state):
    payload = {"catalog": catalog, "business_prompt": state["business_prompt"], "answers": state["answers"]}
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def review(catalog, state):
    validate_state(catalog, state)
    missing, rows, deferred, conditional, inactive_answers = [], [], [], [], []
    for group in catalog["groups"]:
        for q in group["questions"]:
            if not active(q, state["answers"]):
                collection = deferred if q["when"]["question"] in state["answers"] else conditional
                collection.append(q["id"])
                if q["id"] in state["answers"]:
                    inactive_answers.append({"id": q["id"], "answer": state["answers"][q["id"]]})
                continue
            entry = state["answers"].get(q["id"])
            if entry is None:
                missing.append(q["id"])
            rows.append({"id": q["id"], "group": group["title"], "prompt": q["prompt"],
                         "answer": entry, "maps_to": q["maps_to"]})
    digest = fingerprint(catalog, state)
    return {"fingerprint": digest, "missing": missing, "deferred_by_scope": deferred,
            "conditional_pending": conditional, "inactive_answers": inactive_answers,
            "confirmed": not missing and state.get("confirmed_fingerprint") == digest,
            "invariants": catalog["invariants"], "business_prompt": state["business_prompt"], "answers": rows}


def next_batch(catalog, state):
    result = review(catalog, state)
    for group in catalog["groups"]:
        pending = [q for q in group["questions"] if q["id"] in result["missing"]]
        if pending:
            return {"stage": "questions", "group": group["title"],
                    "questions": pending[:catalog["max_batch_size"]]}
    return {"stage": "ready" if result["confirmed"] else "confirm_brief",
            "fingerprint": result["fingerprint"], "questions": []}


def confirm(catalog, state, expected_fingerprint):
    result = review(catalog, state)
    if result["missing"]:
        raise ValueError("Intake is incomplete: " + ", ".join(result["missing"]))
    if expected_fingerprint != result["fingerprint"]:
        raise ValueError("The brief changed; review and confirm its current fingerprint")
    return {**state, "confirmed_fingerprint": expected_fingerprint}


def require_ready(root, path):
    state = json.loads(path.read_text())
    result = review(load_catalog(root), state)
    if not result["confirmed"]:
        raise ValueError("Complete and confirm the intake brief before implementation")
    return result
