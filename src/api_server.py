from flask import Flask, request, Response
from chatbot import run_jira_search
import json

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True, port=5001)
