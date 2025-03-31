import logging

from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
session_storage: dict[str, dict] = {}


@app.post("/post")
def request_handler():
    req_obj = request.get_json()
    logging.info(f'Request: {req_obj!r}')
    response = {
        "session": req_obj["session"],
        "version": req_obj["version"],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(req_obj, response)

    logging.info(f'Response:  {response!r}')
    return jsonify(response)


def handle_dialog(req_obj: dict, response: dict):
    user_id = req_obj["session"]["user_id"]
    new = req_obj["session"]["new"]

    if new:
        session_storage[user_id] = {"suggestions": ["Не хочу", "Не буду", "Отстань!"]}
        response["response"]["text"] = "Привет! Купи слона!"
        response["response"]["buttons"] = get_suggestions(user_id)
        return

    if req_obj["request"]["original_utterance"].lower() in ["ладно", "куплю", "покупаю", "хорошо"]:
        response["response"]["text"] = "Слона можно найти на Яндекс.Маркете!"
        response["response"]["end_session"] = True
    else:
        response['response']['text'] = f"Все говорят '{req_obj['request']['original_utterance']}', а ты купи слона!"
        response['response']['buttons'] = get_suggestions(user_id)


def get_suggestions(user_id: str):
    session = session_storage[user_id]
    suggestions = [
        {"title": suggestion, "hide": True} for suggestion in session["suggestions"][:2]
    ]
    if session["suggestions"]:
        del session["suggestions"][0]

    if len(suggestions) < 2:
        suggestions.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True,
        })

    return suggestions


if __name__ == '__main__':
    app.run()
