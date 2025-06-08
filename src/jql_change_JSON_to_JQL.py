import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key từ .env
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Khởi tạo model Gemini
ai_model = genai.GenerativeModel('gemini-2.0-flash')  # Hoặc 'gemini-1.0-pro'

# Prompt hướng dẫn cho AI
AI_PROMPT = """
Bạn là một trợ lý JQL. Cho trước một object JSON Python dưới dạng dict chứa các điều kiện truy vấn,
hãy chuyển đổi nó thành một câu lệnh JQL tương đương.

Yêu cầu:
- Nếu giá trị là "currentUser()", không đặt trong dấu ngoặc kép.
- Nếu giá trị là chuỗi, đặt trong dấu ngoặc kép.
- Nối các điều kiện bằng "AND".
- Nếu có trường có 2 giá trị nối nhau bằng END, ví dụ: "created": ">= startOfYear() AND <= endOfYear()" thì phải chuyển đổi thành: created >= startOfYear() AND created <= endOfYear()

Chỉ trả về duy nhất chuỗi JQL, không giải thích.

Ví dụ:
Input: {"assignee": "currentUser()", "status": "In Progress"}
Output: assignee = currentUser() AND status = "In Progress"

Input: {"reporter": "alice", "priority": "High"}
Output: reporter = "alice" AND priority = "High"
"""

def convert_dict_to_jql_with_ai(input_dict: dict) -> str:
    prompt = f"{AI_PROMPT}\nInput: {json.dumps(input_dict, ensure_ascii=False)}\nOutput:"
    try:
        response = ai_model.generate_content(prompt)
    
        return response.text.strip()
    except Exception as e:
        print(f"❌ Lỗi khi gọi Gemini API: {e}")
        return ""


if __name__ == "__main__":
    test_query = {
        "assignee": "634fab347d4645af4f0011f1",
        "status": "In Progress"
    }
    jql = convert_dict_to_jql_with_ai(test_query)
    print("✅ JQL:", jql)
