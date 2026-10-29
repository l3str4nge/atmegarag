from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from config import GOLDEN_PATH


class Source(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section: str
    pages: list[int] = Field(min_length=1)


class GoldenCase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str
    question: str
    expected_answer: str
    answerable: bool
    sources: list[Source]
    eval_method: Literal["contains", "llm_judge"]
    must_contain: list[str] = []
    judge_rubric: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def check_consistency(self) -> "GoldenCase":
        if self.eval_method == "contains" and not self.must_contain:
            raise ValueError("eval_method 'contains' requires must_contain")
        if self.eval_method == "llm_judge" and not self.judge_rubric:
            raise ValueError("eval_method 'llm_judge' requires judge_rubric")
        if self.answerable and not self.sources:
            raise ValueError("answerable case requires at least one source")
        return self


def load_golden(path: Path = GOLDEN_PATH) -> list[GoldenCase]:
    raw = yaml.safe_load(path.read_text()) or []
    cases = TypeAdapter(list[GoldenCase]).validate_python(raw)

    seen: set[str] = set()
    for case in cases:
        if case.id in seen:
            raise ValueError(f"Duplicate id: {case.id}")
        seen.add(case.id)

    return cases


if __name__ == "__main__":
    cases = load_golden() # maybe lazy in sometime??
    print(f"Loaded {len(cases)} cases from {GOLDEN_PATH}")
