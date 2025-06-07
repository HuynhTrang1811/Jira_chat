from flask import Flask, request, Response
import os
print("Working directory:", os.getcwd())
from chatbot import run_jira_search
import os
import json
import requests
app = Flask(__name__)
# Thay bằng token bot của bạn
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# URL của API đã deploy trên Render
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
@app.route("/jira/issues/search", methods=["POST"])
def search_jira_issues():
    data = request.get_json(silent=True)
    if not data or "query" not in data:
        response = {
            "error": {
                "message": "Thiếu trường 'query'"
            }
        }
        return Response(
            json.dumps(response, ensure_ascii=False),
            content_type='application/json; charset=utf-8',
            status=400
        )

    user_query = data["query"]

    try:
        result = run_jira_search(user_query)

        if isinstance(result, dict) and "error" in result:
            response = {
                "error": {
                    "code": "INVALID_QUERY",
                    "message": result["error"],
                    "detail": result.get("message", ""),
                    "candidates": result.get("candidates", [])
                }
            }
            return Response(
                json.dumps(response, ensure_ascii=False),
                content_type='application/json; charset=utf-8',
                status=400
            )

        # Cấu trúc result: list of issues
        formatted_result = {
            "count": len(result),
            "issues": result or []
        }

        return Response(
            json.dumps({"result": result or []}, ensure_ascii=False,  indent=2),
            content_type='application/json; charset=utf-8',
            status=200
        )

    except Exception as e:
        response = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Đã xảy ra lỗi trong quá trình xử lý.",
                "detail": str(e)
            }
        }
        return Response(
            json.dumps(response, ensure_ascii=False),
            content_type='application/json; charset=utf-8',
            status=500
        )
# @app.route("/telegram/webhook", methods=["POST"])
# def telegram_webhook():
#     data = request.get_json()
#     if "message" in data:
#         chat_id = data["message"]["chat"]["id"]
#         user_text = data["message"].get("text", "")

#         # Gọi hàm tìm Jira
#         result = run_jira_search(user_text)

#         if isinstance(result, dict) and "error" in result:
#             reply = f"Lỗi: {result['error']}"
#         else:
#             count = result.get("count", 0)
#             issues = result.get("issues", [])
#             if count == 0:
#                 reply = "Không tìm thấy kết quả nào."
#             else:
#                 reply = f"Tìm thấy {count} issue:\n"
#                 for issue in issues[:5]:  # giới hạn 5 kết quả
#                     reply += f"- {issue['key']}: {issue['summary']}\n"

#         send_telegram_message(chat_id, reply)

#     return Response("OK", status=200)
@app.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if not data:
        return Response("No data", status=400)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")
        print(f"Received message from chat_id={chat_id}: {user_text}")

    return Response("OK", status=200)
def send_telegram_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)



if __name__ == "__main__":
    app.run(debug=True, port=5001)
