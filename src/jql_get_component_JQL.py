import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from export_jira_users import load_user_map_from_file
from jql_change_JSON_to_JQL import convert_dict_to_jql_with_ai
from jql_user_mapper_service import replace_user_names_in_jql
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
# Use Gemini 2.0 Flash free
model = genai.GenerativeModel('gemini-2.0-flash')

# Prompt
SYSTEM_PROMPT = """
Bạn là 1 trợ lý Jira. Nhiệm vụ của bạn là nhận câu hỏi từ người dùng và đưa ra câu trả lời. 
Nếu câu hỏi đó là câu hỏi liên quan tới công việc trên Jira thì hãy phân tích câu hỏi đó thành JSON gồm các thành phần truy vấn JQL. 
Trả về JSON với các trường như: project, assignee, reporter, status, priority, issuetype, created, updated, resolution, labels, components, fixVersion, affectsVersion, summary, description, text, issueKey, parent, type, votes, comments, custom fields (ví dụ: 'customfield_12345'), ... tùy nội dung câu hỏi.
Trong JQL, mỗi điều kiện phải chỉ rõ field cần so sánh, không viết tắt như trong SQL.
Với các từ chỉ người như anh, chị,... bỏ qua, chỉ lấy tên người đó, ví dụ chị Trang chuyển thành Trang, anh Nam chuyển thành Nam.
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
Người dùng hỏi: "Hôm nay tôi có những việc gì cần làm"
Trả về JSON:
{ "assignee": "currentUser()",
  "statusCategory" != "Done" ,
  "duedate" >= "startOfDay()"
}
Người dùng hỏi: "Hôm nay anh Chinh có những việc gì cần làm"
Trả về JSON:
{ "assignee": "Chinh",
  "statusCategory" != "Done" ,
  "duedate" >= "startOfDay()"
}


Chỉ trả về JSON, không giải thích thêm. Nếu không thể xác định bất kỳ thành phần JQL nào, hãy trả về JSON rỗng: {}.
Nếu câu hỏi không phải là liên quan tới công việc trên Jira, hãy trả lời: "Xin chào, tôi là trợ lí Jira của bạn, hãy hỏi tôi những công việc bạn cần".
"""

# def get_jql_json(natural_query: str) -> dict:
#     """
#     Chuyển đổi câu hỏi ngôn ngữ tự nhiên thành JSON chứa các thành phần JQL.
#     """

#     prompt_to_gemini = SYSTEM_PROMPT + "\n\nNgười dùng hỏi: \"" + natural_query + "\"\n\nHãy trả kết quả dưới dạng JSON."

#     try:
#         response = model.generate_content(prompt_to_gemini)
#         text = response.text.strip()

#         # Find JSON in response
#         json_start = text.find('{')
#         json_end = text.rfind('}')

#         if json_start == -1 or json_end == -1:
#             print(f"Error: {text}")
#             return {}

   
#         json_string = text[json_start : json_end + 1]

#         # Change JSON to Dictionary Python
#         jql_components = json.loads(json_string)

#         return jql_components

#     except json.JSONDecodeError as e:
#         print(f"Error {text}")
#         return {}
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         return {}
def get_jql_json(natural_query: str) -> dict | str:
    """
    Chuyển đổi câu hỏi ngôn ngữ tự nhiên thành JSON chứa các thành phần JQL.
    Nếu AI trả lời là lời chào hoặc không xác định, thì trả về chuỗi thông báo thay vì JSON.
    """

    prompt_to_gemini = SYSTEM_PROMPT + "\n\nNgười dùng hỏi: \"" + natural_query + "\"\n\n"

    try:
        response = model.generate_content(prompt_to_gemini)
        text = response.text.strip()
     
        # Nếu AI trả về lời chào thay vì JSON
        if text.startswith("xin chào") or "trợ lí Jira" in text:
            return "Xin chào, tôi là trợ lí Jira của bạn, hãy hỏi tôi những công việc bạn cần."

        # Tìm đoạn JSON trong text
        json_start = text.find('{')
        json_end = text.rfind('}')
        if json_start == -1 or json_end == -1:
            print(f"Error: {text}")
            return {}

   
        json_string = text[json_start : json_end + 1]

        # Change JSON to Dictionary Python
        jql_components = json.loads(json_string)
        user_map = load_user_map_from_file()
        mapped_users = replace_user_names_in_jql(jql_components, user_map)
     
        final_jql = convert_dict_to_jql_with_ai(mapped_users)
    
        return final_jql

    except json.JSONDecodeError:
        print(f"❌ JSON decode error: {text}")
        return "Xin lỗi, kết quả không hợp lệ. Vui lòng hỏi lại."
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return "Đã xảy ra lỗi trong quá trình xử lý câu hỏi của bạn."

