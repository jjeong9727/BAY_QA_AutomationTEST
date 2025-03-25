import json
import os

def extract_results(report_path="result.json", output_path="scripts/summary.json"):
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    summary = []

    for test in report.get("tests", []):
        name = test.get("nodeid", "").split("::")[-1]
        file = test.get("nodeid", "").split("::")[0]
        status = test.get("outcome", "")
        message = ""
        stack = ""

        if status == "failed":
            longrepr = test.get("longrepr", {})
            if isinstance(longrepr, dict):
                message = longrepr.get("reprcrash", {}).get("message", "")
                stack = longrepr.get("reprtraceback", {}).get("reprentries", [{}])[-1].get("data", "")
            elif isinstance(longrepr, str):
                message = longrepr
                stack = longrepr

        summary.append({
            "name": name,
            "file": file,
            "status": status,
            "message": message,
            "stack": stack
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("✅ summary.json 생성 완료")

if __name__ == "__main__":
    extract_results()
