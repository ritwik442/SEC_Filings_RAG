from dataclasses import dataclass, asdict
from typing import Optional
import json

VALID_CATEGORIES = {"exact_figure", "synthesis", "cross_company", "unanswerable"}


@dataclass
class EvalItem:
    id: str
    question: str
    ground_truth: str
    category: str
    company: Optional[str]
    filing_type: Optional[str]
    expected_source_substring: Optional[str]
    source: str = "handwritten"         

    def validate(self):
        assert self.id and self.question.strip() and self.ground_truth.strip()
        assert self.category in VALID_CATEGORIES, f"bad category: {self.category}"
        if self.category == "unanswerable":
            assert self.expected_source_substring is None
        if self.category == "cross_company":
            assert self.company is None
        assert self.source in {"handwritten", "generated"}
        return True


def load_dataset(path="eval/dataset.json") -> list[EvalItem]:
    with open(path) as f:
        items = [EvalItem(**d) for d in json.load(f)]
    for it in items:
        it.validate()                     
    return items


def save_dataset(items: list[EvalItem], path="eval/dataset.json"):
    for it in items:
        it.validate()
    with open(path, "w") as f:
        json.dump([asdict(i) for i in items], f, indent=2)