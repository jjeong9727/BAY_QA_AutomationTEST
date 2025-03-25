import json

def extract_failures(report_path="result.json", output_path="failures.json"):
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    failures = []
    for suite in report.get("suites", []):
        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                result = test.get("results", [])[0]
                if result.get("status") == "failed":
                    error = result.get("error", {})
                    failures.append({
                        "name": spec["title"],
                        "file": suite["file"],
                        "message": error.get("message", ""),
                        "stack": error.get("stack", "")
                    })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(failures, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    extract_failures()
