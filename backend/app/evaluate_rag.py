import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# FastAPI chat endpoint
API_URL = "http://127.0.0.1:8000/chat"

# Company policy evaluation tests
test_questions = [
    {
        "name": "Leave request deadline",
        "question": (
            "How many days before planned leave should "
            "employees submit their request?"
        ),
        "expected_keywords": ["seven days"],
    },
    {
        "name": "Working hours",
        "question": "What are the company's working hours?",
        "expected_keywords": [
            "monday",
            "friday",
            "9:00 am",
            "6:00 pm",
        ],
    },
    {
        "name": "Remote work policy",
        "question": (
            "How many days per week can employees work remotely?"
        ),
        "expected_keywords": [
            "two days per week",
            "manager approval",
        ],
    },
    {
        "name": "Missing maternity leave information",
        "question": (
            "What is the company's maternity leave policy?"
        ),
        "expected_keywords": ["could not find"],
    },
]


def ask_chatbot(question: str) -> dict:
    """Send a question to the existing FastAPI chatbot."""

    payload = json.dumps({
        "message": question
    }).encode("utf-8")

    request = Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def evaluate_answer(answer: str, expected_keywords: list[str]) -> bool:
    """Check whether every expected keyword appears in the answer."""

    answer_lower = answer.casefold()

    return all(
        keyword.casefold() in answer_lower
        for keyword in expected_keywords
    )


def main():
    passed = 0
    failed = 0
    errors = 0
    total = len(test_questions)

    print("=" * 65)
    print("ENTERPRISE AI COPILOT - RAG EVALUATION")
    print("=" * 65)

    for number, test in enumerate(test_questions, start=1):
        print(f"\nTEST {number}: {test['name']}")
        print("-" * 65)
        print("Question:", test["question"])

        try:
            result = ask_chatbot(test["question"])

            answer = result.get("answer", "")
            sources = result.get("sources", [])

            print("Answer:", answer)
            print("Sources returned:", len(sources))

            if evaluate_answer(
                answer,
                test["expected_keywords"],
            ):
                print("RESULT: PASS")
                passed += 1
            else:
                print("RESULT: FAIL")
                print(
                    "Expected keywords:",
                    test["expected_keywords"],
                )
                failed += 1

        except (
            URLError,
            HTTPError,
            TimeoutError,
            KeyError,
            ValueError,
        ) as error:
            print("RESULT: ERROR")
            print("Details:", error)
            errors += 1

        except Exception as error:
            print("RESULT: ERROR")
            print("Details:", error)
            errors += 1

    completed = passed + failed
    pass_rate = (
        (passed / completed) * 100
        if completed
        else 0
    )

    print("\n" + "=" * 65)
    print("EVALUATION SUMMARY")
    print("=" * 65)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    print(f"Total tests: {total}")
    print(f"Pass rate among completed tests: {pass_rate:.1f}%")
    print("=" * 65)

    if failed or errors:
        print("Overall status: NEEDS REVIEW")
    else:
        print("Overall status: ALL TESTS PASSED")


if __name__ == "__main__":
    main()