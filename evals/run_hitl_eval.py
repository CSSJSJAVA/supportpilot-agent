import json
import sqlite3
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(
    0,
    str(SRC_DIR),
)


from supportpilot.db import (
    create_ticket_in_db,
    get_ticket_from_db,
    init_db,
    update_ticket_status_in_db,
)


CASES_PATH = ROOT_DIR / "evals" / "hitl_cases.jsonl"
DB_PATH = ROOT_DIR / "supportpilot.db"


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

            cases.append(
                json.loads(line)
            )

    return cases


def count_matching_tickets(
    order_id: str,
    issue_type: str,
    description: str,
) -> int:
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        WHERE order_id = ?
          AND issue_type = ?
          AND description = ?
        """,
        (
            order_id,
            issue_type,
            description,
        ),
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


def evaluate_create_ticket(case: dict) -> bool:
    before_count = count_matching_tickets(
        order_id=case["order_id"],
        issue_type=case["issue_type"],
        description=case["description"],
    )

    if case["decision"] == "approve":
        create_ticket_in_db(
            order_id=case["order_id"],
            issue_type=case["issue_type"],
            description=case["description"],
        )

    after_count = count_matching_tickets(
        order_id=case["order_id"],
        issue_type=case["issue_type"],
        description=case["description"],
    )

    if case["decision"] == "reject":
        passed = after_count == before_count
    else:
        passed = after_count == before_count + 1

    print()
    print("-" * 50)
    print(f"Case: {case['case']}")
    print(f"Decision: {case['decision']}")
    print(f"Before count: {before_count}")
    print(f"After count: {after_count}")
    print(
        f"Result: {'PASS' if passed else 'FAIL'}"
    )

    return passed


def evaluate_update_status(case: dict) -> bool:
    numeric_id = int(
        case["ticket_id"][1:]
    )

    before_ticket = get_ticket_from_db(
        numeric_id
    )

    if before_ticket is None:
        print()
        print("-" * 50)
        print(f"Case: {case['case']}")
        print("Result: FAIL")
        print("Reason: ticket not found")
        return False

    before_status = before_ticket["status"]

    if case["decision"] == "approve":
        update_ticket_status_in_db(
            numeric_id,
            case["new_status"],
        )

    after_ticket = get_ticket_from_db(
        numeric_id
    )

    after_status = after_ticket["status"]

    if case["decision"] == "reject":
        passed = after_status == before_status
    else:
        passed = after_status == case["new_status"]

    print()
    print("-" * 50)
    print(f"Case: {case['case']}")
    print(f"Decision: {case['decision']}")
    print(f"Before status: {before_status}")
    print(f"After status: {after_status}")
    print(
        f"Result: {'PASS' if passed else 'FAIL'}"
    )

    return passed


def evaluate_read_only() -> bool:
    """验证只读操作本身不会修改数据库。"""

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        """
    )

    before_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE order_id = ?
        """,
        ("A1002",),
    )

    cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        """
    )

    after_count = cursor.fetchone()[0]

    conn.close()

    passed = before_count == after_count

    print()
    print("-" * 50)
    print("Case: read_only_no_write")
    print(f"Before ticket count: {before_count}")
    print(f"After ticket count: {after_count}")
    print(
        f"Result: {'PASS' if passed else 'FAIL'}"
    )

    return passed


def main() -> None:
    init_db()

    cases = load_cases()

    passed_count = 0
    total_count = 0

    for case in cases:
        total_count += 1

        if case["action"] == "create_ticket":
            passed = evaluate_create_ticket(
                case
            )

        elif case["action"] == "update_ticket_status":
            passed = evaluate_update_status(
                case
            )

        else:
            print(
                f"Unknown action: "
                f"{case['action']}"
            )
            passed = False

        if passed:
            passed_count += 1

    total_count += 1

    if evaluate_read_only():
        passed_count += 1

    accuracy = (
        passed_count / total_count
        if total_count
        else 0
    )

    print()
    print("=" * 50)
    print("HITL Eval Summary")
    print("=" * 50)
    print(
        f"Passed: "
        f"{passed_count}/{total_count}"
    )
    print(
        f"Accuracy: "
        f"{accuracy:.2%}"
    )


if __name__ == "__main__":
    main()