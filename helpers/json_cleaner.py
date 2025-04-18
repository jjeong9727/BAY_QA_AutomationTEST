import json

def keep_only_order_status_6(file_path="product_name.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        filtered = [item for item in data if item.get("order_status") == 6]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)

        print(f"✅ order_status == 6 항목만 유지 완료 (총 {len(filtered)}개)")

    except FileNotFoundError:
        print("⚠️ product_name.json 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ JSON 처리 중 오류 발생: {e}")
