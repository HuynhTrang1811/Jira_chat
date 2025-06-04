import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
# Use Gemini 2.0 Flash free
model = genai.GenerativeModel('gemini-2.0-flash')

# Prompt
SYSTEM_PROMPT = """
Bạn là chuyên gia JQL. Nhiệm vụ của bạn là phân tích câu hỏi tự nhiên của người dùng thành JSON gồm các thành phần truy vấn JQL.

Trả về JSON với các trường như: project, assignee, reporter, status, priority, issuetype, created, updated, resolution, labels, components, fixVersion, affectsVersion, summary, description, text, issueKey, parent, type, votes, comments, custom fields (ví dụ: 'customfield_12345'), ... tùy nội dung câu hỏi.
Trong JQL, mỗi điều kiện phải chỉ rõ field cần so sánh, không viết tắt như trong SQL.
Ví dụ:
Người dùng hỏi: "Tìm các bug được tạo bởi Trang trong tháng này"
Trả về JSON:
{
  "issuetype": "Bug",
  "reporter": "Trang",
  "created": ">= startOfMonth()"
}

Người dùng hỏi: "Liệt kê các công việc chưa hoàn thành của tôi trong dự án ABC"
Trả về JSON:
{
  "assignee": "currentUser()",
  "resolution": "Unresolved",
  "project": "ABC"
}

Người dùng hỏi: "Hiển thị các tác vụ nhãn phát triển trong phiên bản 1.0"
Trả về JSON:
{
  "issuetype": "Task",
  "labels": "phat_trien",
  "fixVersion": "1.0"
}
Người dùng hỏi: "Tìm các công việc phải hoàn thành trong trong tháng này"
Trả về JSON:
{
  "duedate": ">= startOfMonth()",
  "duedate": "<= endOfMonth()"
}
Người dùng hỏi:"Tìm các công việc được tạo trong 7 ngày qua"
Trả về JSON:
{
  "issuetype": "Bug",
  "created": ">= -7d"
}
Người dùng hỏi: "Tìm các công việc phải hoàn thành trong trong tháng sau"
Trả về JSON:
{
  "duedate": ">= startOfMonth(+1)",
  "duedate": "<= endOfMonth(+1)"
}
Người dùng hỏi: "Các công việc thuộc category tên Blueteam"
Trả về JSON:
{
  "category" : "Blueteam",
}

Chỉ trả về JSON, không giải thích thêm. Nếu không thể xác định bất kỳ thành phần JQL nào, hãy trả về JSON rỗng: {}.
"""

def get_jql_json(natural_query: str) -> dict:
    """
    Chuyển đổi câu hỏi ngôn ngữ tự nhiên thành JSON chứa các thành phần JQL.
    """

    prompt_to_gemini = SYSTEM_PROMPT + "\n\nNgười dùng hỏi: \"" + natural_query + "\"\n\nHãy trả kết quả dưới dạng JSON."

    try:
        response = model.generate_content(prompt_to_gemini)
        text = response.text.strip()

        # Find JSON in response
        json_start = text.find('{')
        json_end = text.rfind('}')

        if json_start == -1 or json_end == -1:
            print(f"Error: {text}")
            return {}

   
        json_string = text[json_start : json_end + 1]

        # Change JSON to Dictionary Python
        jql_components = json.loads(json_string)

        return jql_components

    except json.JSONDecodeError as e:
        print(f"Error {text}")
        return {}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

