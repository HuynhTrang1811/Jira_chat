import os
from dotenv import load_dotenv
import requests
import base64
import json
from urllib.parse import quote

load_dotenv()

jira_server = os.environ.get("JIRA_SERVER")
jira_username = os.environ.get("JIRA_USERNAME")
jira_password = os.environ.get("JIRA_PASSWORD")

can_connect_jira = False
if all([jira_server, jira_username, jira_password]):
    auth_string = f"{jira_username}:{jira_password}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }
    can_connect_jira = True
else:
    print(f"[{'Ho Chi Minh City'}]: Cảnh báo: Chưa thiết lập đầy đủ thông tin Jira trong file .env.")

def search_jira_issues(jql_query):
    if can_connect_jira:
        print(jql_query)
        url = f"{jira_server}/rest/api/3/search?jql={quote(jql_query)}"
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            issues = data.get("issues", [])
            return issues
        except requests.exceptions.RequestException as e:
            print(f"[{'Ho Chi Minh City'}]: Lỗi khi gọi Jira API: {e}")
            return None
        except json.JSONDecodeError:
            print(f"[{'Ho Chi Minh City'}]: Lỗi khi giải mã JSON từ Jira API.")
            return None
    else:
        print(f"[{'Ho Chi Minh City'}]: Không thể kết nối đến Jira API.")
        return None

def display_jira_issues(issues):
    if issues:
        print(f"[{'Ho Chi Minh City'}]: Tìm thấy {len(issues)} issue:")
        for issue in issues:
            print(f" {issue['key']}: {issue['fields']['summary']}")
    else:
        print(f"[{'Ho Chi Minh City'}]: Không tìm thấy issue nào hoặc có lỗi xảy ra.")

if __name__ == "__main__":
    sample_jql = 'label = "Blueteam"'
    found_issues = search_jira_issues(sample_jql)
    display_jira_issues(found_issues)
    #gemini-2.0-flash