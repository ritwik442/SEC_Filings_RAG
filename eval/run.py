import json
from eval.dataset import load_dataset
from eval.metrics import retrieval_hit, score_unanswerable, aggregate
from eval.judge import judge
from vectorstore import VectorStore
from rag import answer_question


def run_eval(dataset_path="eval/dataset.json", out="eval/results.json"):
    items = load_dataset(dataset_path)
    store = VectorStore.load()
    results = []

    for item in items:
        answer, hits = answer_question(
            item.question, store, k=6, company=item.company)
        chunks = [rec["text"] for rec, _ in hits]

        # Score retrieval independently of generation
        hit = retrieval_hit(item.expected_source_substring, chunks)

        correct = judge(item.question, item.ground_truth, answer, item.category)

        results.append({
            "id": item.id,
            "category": item.category,
            "question": item.question,
            "answer": answer,
            "ground_truth": item.ground_truth,
            "correct": correct,
            "retrieval_hit": hit,
        })
        print(f"{'✓' if correct else '✗'} [{item.category}] {item.id}")

    report = aggregate(results)
    with open(out, "w") as f:
        json.dump({"report": report, "results": results}, f, indent=2)
    print("\n" + json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    run_eval()