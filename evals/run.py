import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from config import BASELINE_MODEL, EVAL_WORKERS, JUDGE_MODEL, RESULTS_DIR
from evals.parser import GoldenCase, load_golden
from llm import complete

JUDGE_SYSTEM = (
    "You are a strict evaluator. Grade the answer against the rubric and the expected answer. "
    "Reply with PASS or FAIL on the first line, then one short sentence explaining why."
)


class Score(BaseModel):
    passed: bool
    reason: str


class CaseResult(BaseModel):
    id: str
    eval_method: str
    answer: str
    passed: bool
    reason: str


class RunResult(BaseModel):
    name: str
    created_at: datetime
    model: str
    judge_model: str
    passed: int
    total: int
    cases: list[CaseResult]


def main(name: str) -> None:
    cases = load_golden()
    print(f"Loaded {len(cases)} golden cases")

    with ThreadPoolExecutor(max_workers=EVAL_WORKERS) as pool:
        results = list(pool.map(run_case, cases))

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.id} ({result.eval_method}): {result.reason}")

    run = RunResult(
        name=name,
        created_at=datetime.now(),
        model=BASELINE_MODEL,
        judge_model=JUDGE_MODEL,
        passed=sum(result.passed for result in results),
        total=len(results),
        cases=results,
    )
    path = save_results(run)
    print(f"\n{run.passed}/{run.total} passed, saved to {path}")


def run_case(case: GoldenCase) -> CaseResult:
    answer = complete(case.question, model=BASELINE_MODEL)
    result = score(case, answer)
    return CaseResult(
        id=case.id,
        eval_method=case.eval_method,
        answer=answer,
        passed=result.passed,
        reason=result.reason,
    )


def save_results(run: RunResult) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"{run.name}_{run.created_at:%Y-%m-%d_%H-%M-%S}.json"
    path.write_text(run.model_dump_json(indent=2))
    return path


def score(case: GoldenCase, answer: str) -> Score:
    if case.eval_method == "contains":
        return score_contains(case, answer)
    return score_llm_judge(case, answer)


def score_contains(case: GoldenCase, answer: str) -> Score:
    missing = [term for term in case.must_contain if term.lower() not in answer.lower()]
    if missing:
        return Score(passed=False, reason=f"missing: {', '.join(missing)}")
    return Score(passed=True, reason="all terms present")


def score_llm_judge(case: GoldenCase, answer: str) -> Score:
    prompt = (
        f"Question:\n{case.question}\n\n"
        f"Expected answer:\n{case.expected_answer}\n\n"
        f"Rubric:\n{case.judge_rubric}\n\n"
        f"Answer to grade:\n{answer}"
    )
    verdict = complete(prompt, system=JUDGE_SYSTEM, model=JUDGE_MODEL, temperature=0.0).strip()
    first_line, _, rest = verdict.partition("\n")
    return Score(passed=first_line.strip().upper().startswith("PASS"), reason=rest.strip() or first_line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run evals against the golden set.")
    parser.add_argument("name", help="run name used in the result file, e.g. baseline")
    args = parser.parse_args()
    main(args.name)
