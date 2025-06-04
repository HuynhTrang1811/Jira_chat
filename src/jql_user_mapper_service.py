import json
import os
import unicodedata
import sys
from export_jira_users import load_user_map_from_file
# Thư mục chứa file code
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "users_parsed.txt")


def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize(text: str) -> str:
    text = text.strip().lower()
    text = remove_accents(text)
    return text

def find_user(user_map: dict, input_name: str) -> str | dict:
    input_norm = normalize(input_name)
    word_count = len(input_name.strip().split())

    # Nếu chỉ 1 từ thì tìm theo first_name
    if word_count == 1:
        matches_first_name = [
            (full_name, info)
            for full_name, info in user_map.items()
            if normalize(info["first_name"]) == input_norm
        ]

        if len(matches_first_name) == 1:
            return matches_first_name[0][1]["account_id"]
        elif len(matches_first_name) == 0:
            return {
                "error": f"Không tìm thấy người dùng nào có tên '{input_name}'."
            }
        else:
            candidates = [full_name for full_name, _ in matches_first_name]
            return {
                "error": f"Có {len(candidates)} người dùng có tên '{input_name}'.",
                "candidates": candidates,
                "message": "Vui lòng yêu cầu lại với thông tin đầy đủ và chính xác hơn."
            }

    # Nếu 2 từ trở lên thì tìm theo tên đầy đủ chứa chuỗi input
    matches_full_name = [
        (full_name, info)
        for full_name, info in user_map.items()
        if input_norm in normalize(full_name)
    ]

    if len(matches_full_name) == 1:
        return matches_full_name[0][1]["account_id"]
    elif len(matches_full_name) == 0:
        return {
            "warning": f"Không tìm thấy người dùng nào phù hợp với '{input_name}'."
        }
    else:
        candidates = [full_name for full_name, _ in matches_full_name]
        return {
            "warning": f"Có {len(candidates)} người dùng có tên chứa '{input_name}'.",
            "candidates": candidates,
            "message": "Vui lòng yêu cầu lại với thông tin đầy đủ và chính xác hơn."
        }



def replace_user_names_in_jql(jql_dict: dict, user_map: dict) -> dict | dict:
    """
    Thay thế các tên người dùng trong JQL JSON (trường 'assignee' và 'reporter') bằng account_id nếu tìm được.
    Nếu không tìm thấy hoặc có nhiều kết quả thì trả về dict lỗi.
    """
    fields_to_check = ['assignee', 'reporter']
    updated_jql = jql_dict.copy()

    for field in fields_to_check:
        if field not in updated_jql:
            continue

        input_value = updated_jql[field]
        if not isinstance(input_value, str):
            continue

        input_value = input_value.strip()
        if not input_value or input_value.lower() == "currentuser()":
            continue

        result = find_user(user_map, input_value)

        if isinstance(result, str):
            # Tìm thấy account_id -> thay thế
            updated_jql[field] = result
        elif isinstance(result, dict) and "error" in result:
            # Trả về dict lỗi cho caller xử lý (API sẽ trả JSON lỗi)
            return result

    return updated_jql



if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "users_parsed.txt")

    # Load user_map từ file
    user_map = load_user_map_from_file()

    # JSON JQL mẫu có sẵn (đổi tên theo dữ liệu của bạn)
    jql_data = {
        "assignee": "Trúc Huynh",
        "reporter": "Mỹ Hạnh",
        "project": "ABC",
        "summary": "Test issue"
    }

    # Gọi hàm thay thế tên
    replaced = replace_user_names_in_jql(jql_data, user_map)
    print(replaced)
    # In kết quả
   

# def map_jql_user_names_to_ids(
#     jql_query: Dict[str, Any], 
#     user_map: Dict[str, str]
# ) -> Dict[str, Any] | Dict[str, Any]:
#     """
#     Trả về:
#       - Nếu ánh xạ thành công: JQL với user ID đã thay thế.
#       - Nếu không rõ ràng: dict dạng {'need_user_input': True, 'field': ..., 'original_input': ..., 'message': ...}
#     """
#     if not jql_query:
#         return {}

#     normalized_user_map = {
#         normalize(name): (name, user_id) for name, user_id in user_map.items()
#     }

#     modified_jql = jql_query.copy()

#     for field in ['assignee', 'reporter']:
#         if field not in modified_jql:
#             continue

#         raw_input = modified_jql[field]

#         # Giữ nguyên nếu là currentUser()
#         if raw_input.lower() == "currentuser()":
#             modified_jql[field] = "currentUser()"
#             continue

#         # Bước 1: Tìm khớp chính xác (normalize)
#         normalized_input = normalize(raw_input)
#         if normalized_input in normalized_user_map:
#             name, user_id = normalized_user_map[normalized_input]
#             modified_jql[field] = user_id
#             continue

#         # Bước 2: Dùng AI để trích xuất tên người dùng
#         extracted_name = _extract_user_from_string_with_ai(raw_input)
#         normalized_ai_name = normalize(extracted_name)

#         # Thử match với user map bằng AI output
#         if normalized_ai_name in normalized_user_map:
#             name, user_id = normalized_user_map[normalized_ai_name]
#             modified_jql[field] = user_id
#             continue

#         # Bước 3: Fuzzy match - tìm các ứng viên
#         matches = []
#         for name, user_id in user_map.items():
#             if normalized_ai_name in normalize(name) or normalized_input in normalize(name):
#                 matches.append({'name': name, 'user_id': user_id})

#         if len(matches) == 1:
#             modified_jql[field] = matches[0]['user_id']
#         elif len(matches) > 1:
#             return {
#                 'need_user_input': True,
#                 'field': field,
#                 'original_input': raw_input,
#                 'message': f"🔍 Có {len(matches)} người dùng khớp với '{raw_input}'. Vui lòng nhập tên đầy đủ hơn của người bạn cần tìm.",
#                 'candidates_preview': [m['name'] for m in matches]
#             }
#         else:
#             return {
#                 'need_user_input': True,
#                 'field': field,


#                 'original_input': raw_input,
#                 'message': f"❗Không tìm thấy người dùng nào khớp với '{raw_input}'. Vui lòng nhập lại.",
#                 'candidates_preview': []
#             }

#     return modified_jql
