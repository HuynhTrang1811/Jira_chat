from export_jira_users import load_user_map_from_file
from jql_get_component_JQL import get_jql_json
from jql_user_mapper_service import replace_user_names_in_jql
from jql_get_Item_Jira import search_jira_issues
from jql_change_JSON_to_JQL import convert_dict_to_jql_with_ai

def run_jira_search(user_input: str):
    jql_components = get_jql_json(user_input)
    user_map = load_user_map_from_file()
    mapped_users = replace_user_names_in_jql(jql_components, user_map)

    # Kiểm tra lỗi trả về từ replace_user_names_in_jql
    if isinstance(mapped_users, dict) and "error" in mapped_users:
        print(mapped_users)
        return mapped_users  # Trả về dict lỗi ngay

    final_jql = convert_dict_to_jql_with_ai(mapped_users)
    issues = search_jira_issues(final_jql)

    if issues:
        return {
            "count": len(issues),
            "issues": [{"key": i["key"], "summary": i["fields"]["summary"]} for i in issues]
        }
    else:
        return {"count": 0, "issues": []}


def main():
    print("🚀 Công cụ tìm kiếm Jira thông minh")
    while True:
        user_input = input("\n📝 Bạn muốn tìm kiếm gì trong Jira? (gõ 'exit' để thoát):\n> ")
        if user_input.strip().lower() == 'exit':
            print("👋 Kết thúc chương trình.")
            break
        run_jira_search(user_input)

if __name__ == "__main__":
    main()
