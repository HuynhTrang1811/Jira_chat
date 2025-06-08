import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from requests.auth import HTTPBasicAuth
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
JIRA_BASE_URL= os.environ.get("JIRA_SERVER")
JIRA_EMAIL=os.environ.get("JIRA_USERNAME")
JIRA_API_TOKEN=os.environ.get("JIRA_PASSWORD")
genai.configure(api_key=GEMINI_API_KEY)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_CHANGE_FILE = os.path.join(BASE_DIR, "users.txt")
OUTPUT_CHANGE_FILE = os.path.join(BASE_DIR, "users_parsed.txt")
PROJECT_KEY="ATTT"
model = genai.GenerativeModel("gemini-1.5-flash")
# def get_all_jira_users():
#     url = f"{JIRA_BASE_URL}/rest/api/2/user/assignable/search?project={PROJECT_KEY}"
#     start_at = 0
#     max_results = 100

#     with open(INPUT_CHANGE_FILE, "w", encoding="utf-8") as f:
#         while True:
#             params = {
#                 "startAt": start_at,
#                 "maxResults": max_results
#             }
#             response = requests.get(
#                 url,
#                 params=params,
#                 auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
#                 headers={"Accept": "application/json"}
#             )

#             if response.status_code != 200:
#                 print(f"❌ Error: {response.status_code} - {response.text}")
#                 break

#             users = response.json()
#             if not users:
#                 break

#             for user in users:
#                 display_name = user.get("displayName", "").strip()
#                 account_id = user.get("accountId", "").strip()

#                 if display_name and account_id:
#                     # Ghi theo định dạng yêu cầu
#                     f.write(f'"{display_name}": "{account_id}"\n')

#             start_at += len(users)

PROMPT = """
Bạn là trợ lý ngôn ngữ có nhiệm vụ trích TÊN RIÊNG từ tên đầy đủ người Việt Nam.
Luôn giả định tên RIÊNG là thành phần CUỐI CÙNG của phần họ tên chính (bỏ qua hậu tố như ' - CNTT', ' - phòng kỹ thuật'... nếu có).
Nếu tên không tuân theo quy tắc tên của người Việt Nam, trả về đúng tên đó, bỏ qua hậu tố như ' - CNTT', ' - phòng kỹ thuật'... nếu có.
Chỉ trả về chính xác tên riêng. KHÔNG GIẢI THÍCH.

Ví dụ:
Input: "Nguyen Van A - CNTT"
Output: "A"
Ví dụ:
Input: "Trần Thị Bích Ngọc"
Output: "Ngọc"
Ví dụ:
Input: "A Văn Nguyễn"
Output: "A"
Ví dụ:
Input: "ThinhLX - CNTT"
Output: "ThinhLX"
"""



def extract_first_name(full_name: str) -> str:
    try:
        query = f'{PROMPT}\nInput: "{full_name}"\nOutput:'
        response = model.generate_content(query)
        return response.text.strip().strip('"')
    except Exception as e:
        print(f"Lỗi AI khi xử lý '{full_name}': {e}")
        return ""
def enhance_names_with_ai():
    if not os.path.exists(INPUT_CHANGE_FILE):
        print(f"❌ Không tìm thấy file: {INPUT_CHANGE_FILE}")
        return

    with open(INPUT_CHANGE_FILE, "r", encoding="utf-8") as f_in, open(OUTPUT_CHANGE_FILE, "w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line or ":" not in line:
                continue
            try:
                # Ví dụ line:  "Chu Thị Mỹ Hạnh - CNTT": "5e817ceb5b08780c1c2adfd0"
                json_line = "{" + line + "}"
                parsed = json.loads(json_line)
                full_name, account_id = list(parsed.items())[0]

                # Gọi AI lấy first_name
                first_name = extract_first_name(full_name)

                # Ghi ra file theo định dạng: 
                # "Chu Thị Mỹ Hạnh - CNTT": "5e817ceb5b08780c1c2adfd0", "Hạnh"
                output_line = f'"{full_name}": "{account_id}", "{first_name}"\n'
                f_out.write(output_line)

                print(f"✔ {full_name} → {first_name}")

            except Exception as e:
                print(f"❌ Lỗi xử lý dòng: {line} → {e}")

def load_user_map_from_file() -> dict:
    user_map = {}
    if not os.path.exists(OUTPUT_CHANGE_FILE):
        print(f"❌ Không tìm thấy file: {OUTPUT_CHANGE_FILE}")
        return user_map

    with open(OUTPUT_CHANGE_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                # Dòng dạng: "Chu Thị Mỹ Hạnh - CNTT": "5e817ceb5b08780c1c2adfd0", "Hạnh"
                parts = line.split('": ')
                full_name = parts[0].strip().strip('"')
                rest = parts[1].split(',')  # [' "5e817ceb5b08780c1c2adfd0"', ' "Hạnh"']
                account_id = rest[0].strip().strip('"')
                first_name = rest[1].strip().strip('"')

                user_map[full_name] = {
                    "account_id": account_id,
                    "first_name": first_name
                }
            except Exception as e:
                print(f"Lỗi khi đọc dòng: {line} -> {e}")
    return user_map


if __name__ == "__main__":
    load_user_map_from_file()
    print(f"\n✅ Đã ghi file mới: {OUTPUT_CHANGE_FILE}")



# def get_all_jira_users():
#     url = f"{JIRA_BASE_URL}/rest/api/2/user/assignable/search?project={PROJECT_KEY}"
#     start_at = 0
#     max_results = 100
#     all_users = []

#     while True:
#         params = {
#             "startAt": start_at,
#             "maxResults": max_results
#         }
#         response = requests.get(
#             url,
#             params=params,
#             auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
#             headers={"Accept": "application/json"}
#         )

#         if response.status_code != 200:
#             print(f"Error: {response.status_code} - {response.text}")
#             break

#         users = response.json()
#         if not users:
#             break

#         all_users.extend(users)
#         start_at += len(users)

#     return all_users

# def save_users_to_file(users, output_file=OUTPUT_FILE):
#     os.makedirs(os.path.dirname(output_file), exist_ok=True)

#     with open(output_file, "w", encoding="utf-8") as f:
#         for user in users:
#             if user.get("accountType") != "atlassian" or not user.get("active", False):
#                 continue
#             full_name = user.get("displayName", "").strip()
#             account_id = user.get("accountId", "")
#             if full_name and account_id:
#                 first_name = extract_first_name(full_name)
#                 record = {
#                     "full_name": full_name,
#                     "first_name": first_name,
#                     "account_id": account_id
#                 }
#                 f.write(json.dumps(record, ensure_ascii=False) + "\n")

# def fetch_and_load_user_map(filepath=OUTPUT_FILE):
#     user_map = {}
#     with open(filepath, "r", encoding="utf-8") as f:
#         for line in f:
#             try:
#                 record = json.loads(line.strip())
#                 user_map[record["full_name"]] = {
#                     "first_name": record["first_name"],
#                     "account_id": record["account_id"]
#                 }
#             except Exception as e:
#                 print(f"Error đọc dòng: {line}. Lỗi: {e}")
#     return user_map

# if __name__ == "__main__":
   
#     user_map = fetch_and_load_user_map()
#     # In ví dụ 5 user đầu
#     for full_name, info in list(user_map.items())[:5]:
#         print(f"{full_name} - Tên: {info['first_name']} - ID: {info['account_id']}")
