from export_jira_users import load_user_map_from_file
from jql_get_component_JQL import get_jql_json
from jql_user_mapper_service import replace_user_names_in_jql
from jql_get_Item_Jira import search_jira_issues
from jql_change_JSON_to_JQL import convert_dict_to_jql_with_ai

def run_jira_search(user_input: str):
    # jql_components = get_jql_json(user_input)
    # print(jql_components)
    
    # issues = search_jira_issues(jql_components)

    # if issues:
    #     return {
    #         "count": len(issues),
    #         "issues": [{"key": i["key"], "summary": i["fields"]["summary"]} for i in issues]
    #     }
    # else:
    #     return {"count": 0, "issues": []}
    jql_components = get_jql_json(user_input)
    print("JQL Components:", jql_components)

# Nếu là dict, tức là có thể là truy vấn JQL
    if isinstance(jql_components, dict) and jql_components:
        issues = search_jira_issues(jql_components)
    
        if issues:
            return {
            "count": len(issues),
            "issues": [
                {"key": i["key"], "summary": i["fields"]["summary"]}
                for i in issues
            ]
        }
        else:
            return {
            "count": 0,
            "issues": []
        }

# Ngược lại: jql_components là chuỗi —> trả về chuỗi như “Xin chào...”
    else:
        return jql_components



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
