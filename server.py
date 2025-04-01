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
        session_storage[user_id] = {"suggestions": ["Не хочу", "Не буду", "Отстань!"], "now_buying": "слон"}
        response["response"]["text"] = f"Привет! Купи {session_storage[user_id]['now_buying']}а!"
        response["response"]["buttons"] = get_suggestions(user_id)
        return

    bought = False
    utterance = req_obj["request"]["original_utterance"].lower()
    for agreement in ["ладно", "куплю", "покупаю", "хорошо"]:
        if agreement in utterance:
            bought = True
            break

    if bought:
        if session_storage[user_id]['now_buying'] == "слон":
            response["response"]["text"] = "А теперь купи кролика!"
            session_storage[user_id] = {"suggestions": ["Не хочу", "Не буду", "Отстань!"], "now_buying": "кролик"}
            response['response']['buttons'] = get_suggestions(user_id)
        else:
            response["response"][
                "text"] = f"{session_storage[user_id]['now_buying'].title()}а можно найти на Яндекс.Маркете!"
            response["response"]["end_session"] = True
    else:
        response['response']['text'] = (f"Все говорят '{req_obj['request']['original_utterance']}', "
                                        f"а ты купи {session_storage[user_id]['now_buying']}а!")
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
            "url": "https://market.yandex.ru/search?text=кролик" if session_storage[user_id]["now_buying"] == "кролик" \
                else None,
            "hide": True,
        })

    return suggestions


if __name__ == '__main__':
    app.run(port=8808, host="0.0.0.0")
