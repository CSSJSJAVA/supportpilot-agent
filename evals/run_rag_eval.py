import json
import sys
from pathlib import Path


SRC_DIR = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))


from supportpilot.rag.retriever import search_knowledge_base


CASES_PATH = Path("evals/rag_cases.jsonl")


def load_cases() -> list[dict]:
    cases = []

    with CASES_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            cases.append(json.loads(line))

    return cases


def run_eval():
    cases = load_cases()

    retrieval_total = 0
    retrieval_correct = 0

    recall_at_3_total = 0
    recall_at_3_correct = 0

    no_answer_total = 0
    no_answer_correct = 0

    print(f"共加载 {len(cases)} 条测试数据。\n")

    for index, case in enumerate(cases, start=1):
        query = case["query"]
        expected_source = case["expected_source"]

        results = search_knowledge_base(
            query=query,
            top_k=3,
        )

        top1_source = None
        top3_sources = []

        if results:
            top1_source = results[0]["source"]

            top3_sources = [
                result["source"]
                for result in results[:3]
            ]

        if expected_source is None:
            no_answer_total += 1

            passed = top1_source is None

            if passed:
                no_answer_correct += 1

        else:
            retrieval_total += 1
            recall_at_3_total += 1

            passed = top1_source == expected_source

            if passed:
                retrieval_correct += 1

            recall_at_3_passed = expected_source in top3_sources

            if recall_at_3_passed:
                recall_at_3_correct += 1

        print("=" * 60)
        print(f"Case {index}")
        print(f"问题：{query}")
        print(f"期望来源：{expected_source}")
        print(f"实际 Top1：{top1_source}")
        print(f"实际 Top3：{top3_sources}")
        print(f"结果：{'PASS' if passed else 'FAIL'}")
        print()

    top1_accuracy = (
        retrieval_correct / retrieval_total
        if retrieval_total > 0
        else 0
    )

    recall_at_3 = (
        recall_at_3_correct / recall_at_3_total
        if recall_at_3_total > 0
        else 0
    )

    no_answer_accuracy = (
        no_answer_correct / no_answer_total
        if no_answer_total > 0
        else 0
    )

    print("=" * 60)
    print("RAG Eval Summary")
    print("=" * 60)

    print(
        f"Top1 Accuracy："
        f"{retrieval_correct}/{retrieval_total} "
        f"= {top1_accuracy:.2%}"
    )

    print(
        f"Recall@3："
        f"{recall_at_3_correct}/{recall_at_3_total} "
        f"= {recall_at_3:.2%}"
    )

    print(
        f"No-answer Accuracy："
        f"{no_answer_correct}/{no_answer_total} "
        f"= {no_answer_accuracy:.2%}"
    )


if __name__ == "__main__":
    run_eval()