


def retrieval_hit(expected_substring, retrieved_chunks):

    if expected_substring is None:
        return None
    needle = expected_substring.lower()
    return any(needle in chunk.lower() for chunk in retrieved_chunks)


REFUSAL_MARKERS = [
    "couldn't find", "could not find", "not provided", "not disclosed",
    "does not provide", "does not disclose", "does not contain",
    "not in the filing", "no information", "not stated", "not mentioned",
    "not available", "cannot determine", "don't know", "do not know",
    "isn't in the", "is not in the",
]


def is_refusal(answer):

    a = answer.lower()
    return any(marker in a for marker in REFUSAL_MARKERS)


def score_unanswerable(answer):

    return is_refusal(answer)


def aggregate(results):
    from collections import defaultdict
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r)

    report = {}
    for cat, items in by_cat.items():
        n = len(items)
        correct = sum(1 for i in items if i["correct"])
        # Retrieval only scored where a hit is definable (skip unanswerable/None)
        scored_retrieval = [i for i in items if i["retrieval_hit"] is not None]
        hits = sum(1 for i in scored_retrieval if i["retrieval_hit"])

        entry = {
            "n": n,
            "answer_accuracy": round(correct / n, 3) if n else 0.0,
        }
        if scored_retrieval:
            entry["retrieval_hit_rate"] = round(hits / len(scored_retrieval), 3)
        if cat == "unanswerable":
            halluc = sum(1 for i in items if not i["correct"])
            entry["hallucination_rate"] = round(halluc / n, 3) if n else 0.0
        report[cat] = entry

    total = len(results)
    report["overall"] = {
        "n": total,
        "answer_accuracy": round(sum(1 for r in results if r["correct"]) / total, 3),
    }
    return report