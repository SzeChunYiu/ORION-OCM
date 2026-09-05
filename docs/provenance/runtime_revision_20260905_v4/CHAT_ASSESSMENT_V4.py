"""Generated spelling development assessment. No independent or ChatGPT comparison.

Uses all eligible curated LOCATED_IN questions, transforms subjects by four
declared edit operations, and counts every generated case including abstention.
Do not overwrite outputs or tune the generator against its measured outcomes.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ocm.chat.session import ChatSession


def run():
    with TemporaryDirectory() as root:
        session = ChatSession(Path(root))
        manifest = json.loads(session.manifest.read_text())
        cases = []
        for fact in manifest["facts"]:
            subject, obj = fact["subject"], fact["object"]
            if (fact["relation"] != "LOCATED_IN" or not fact.get("verified_by")
                    or not subject.isalpha() or len(subject) < 4):
                continue
            variants = {"transpose": subject[1] + subject[0] + subject[2:],
                        "delete": subject[:-1], "insert": subject + subject[-1],
                        "substitute": subject[:-1] + ("z" if subject[-1] != "z" else "q")}
            for kind, wrong in variants.items():
                if wrong == subject:
                    continue
                original = f"is {subject} in {obj}"
                question = f"is {wrong} in {obj}"
                clean = session.say(original)
                response = session.say(question)
                trace = session.last_trace()
                interpreted = trace["interpretation"].get("input", {}).get("interpreted")
                correct = interpreted == original and "Yes." in response
                clarification = response.startswith("Did you mean")
                wrong_answer = "Yes." in response and not correct
                cases.append({"fact": fact["fact_id"], "kind": kind, "question": question,
                    "target": original, "clean_answer": clean, "answer": response,
                    "correct_conditional_answer": correct, "clarification": clarification,
                    "wrong_asserted_answer": wrong_answer})
        transcript = []
        for question in ("hello", "what can you learn", "remember: mira is a botanist",
                         "is mira a botanist", "learn method next-square: inc square",
                         "run next-square on 3", "list skills"):
            answer = session.say(question)
            transcript.append({"user": question, "ocm": answer})
        restarted = ChatSession(Path(root))
        for question in ("run next-square on 4", "is mira a botanist"):
            transcript.append({"restart": True, "user": question, "ocm": restarted.say(question)})
        return {"scope": "ENGINEERING_DEVELOPMENT_ONLY", "external_model_calls": 0,
                "matched_ChatGPT_comparison": "NOT_RUN", "independent_human_rating": "NOT_RUN",
                "cases": cases, "transcript": transcript, "counts": {
                    "generated": len(cases),
                    "conditional_correct": sum(c["correct_conditional_answer"] for c in cases),
                    "clarifications": sum(c["clarification"] for c in cases),
                    "wrong_asserted_answers": sum(c["wrong_asserted_answer"] for c in cases),
                    "unhandled": sum(not any(c[k] for k in ("correct_conditional_answer", "clarification", "wrong_asserted_answer")) for c in cases)}}


if __name__ == "__main__":
    result = run()
    path = Path(__file__).with_name("CHAT_ASSESSMENT_V4.json")
    with path.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result["counts"]))
