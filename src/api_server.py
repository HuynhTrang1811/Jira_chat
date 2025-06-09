from flask import Flask, request, jsonify
import os
import json
import requests
from chatbot import run_jira_search  # Đảm bảo đã xử lý an toàn bên trong chatbot

app = Flask(__name__)

# Load Telegram bot token từ biến môi trường
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise EnvironmentError("TELEGRAM_TOKEN chưa được thiết lập trong biến môi trường")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Middleware cho logging (có thể mở rộng thêm rate-limiting, auth...)
@app.before_request
def log_request_info():
    app.logger.info(f"Yêu cầu: {request.method} {request.path} - {request.get_json(silent=True)}")

# RESTful API - POST jira/issues/search
@app.route("/jira/issues/search", methods=["POST"])
def search_jira_issues():
    data = request.get_json(silent=True)
    if not data or "query" not in data:
        return jsonify({"error": {"message": "Thiếu trường 'query'."}}), 400

    user_query = data["query"]
    try:
        result = run_jira_search(user_query)

        if isinstance(result, dict) and "error" in result:
            return jsonify({
                "error": {
                    "code": "INVALID_QUERY",
                    "message": result["error"],
                    "detail": result.get("message", ""),
                    "candidates": result.get("candidates", [])
                }
            }), 400

        return jsonify({
            "result": {
                "count": len(result),
                "issues": result
            }
        }), 200

    except Exception as e:
        app.logger.error("Lỗi nội bộ: %s", str(e))
        return jsonify({
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Lỗi máy chủ.",
                "detail": str(e)
            }
        }), 500

# Webhook API cho Telegram bot
@app.route("/webhook/telegram", methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True)

    if "message" not in data:
        return jsonify({"error": "Thiếu trường 'message'."}), 400

    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"].get("text", "")

    try:
        result = run_jira_search(user_text)

        if isinstance(result, dict) and "error" in result:
            reply = f"⚠️ Lỗi: {result['error']}"
        elif isinstance(result, list):
            if not result:
                reply = "❌ Không tìm thấy issue nào."
            else:
                reply = f"📊 Tìm thấy {len(result)} issue:\n"
                for issue in result[:5]:
                    reply += f"- {issue['key']}: {issue['summary']}\n"
        else:
            reply = str(result)

        send_telegram_message(chat_id, reply)
        return "OK", 200

    except Exception as e:
        app.logger.error("Lỗi webhook Telegram: %s", str(e))
        send_telegram_message(chat_id, "⚠️ Lỗi hệ thống. Vui lòng thử lại sau.")
        return "Error", 500


def send_telegram_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        app.logger.error("Gửi tin nhắn Telegram thất bại: %s", str(e))


if __name__ == "__main__":
    app.run(debug=False, port=5001, host="0.0.0.0")