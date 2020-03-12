# todo: database
# todo: websockets

import time
import logging
from datetime import datetime

from flask import Flask, request, jsonify

app = Flask(__name__)
app.after = 0  # default parameter - send all current messages available
logging.getLogger(__name__)  # deafult logging

app.users = {  # test userset
    'Mary': '12345',
    'Jack': '12345',
}

messages = [  # test messages
    {'username': 'Jack', 'text': 'Hello, everyone!', 'time': time.time()},
    {'username': 'Mary', 'text': 'Hi, there!', 'time': time.time()},
]


@app.route("/")
def hello():
    """
    no parameters
    :return: a string
    """
    return "<h1>Available links:</h1><hr />" \
           "<h3>- <a href='/status'>Status page</a></h3><br>" \
           "<h3>- <a href='/messages'>View messages</a></h3><br>"


@app.route("/status/")
def status_view():
    """
    View current status of the server
    Просмотр текущего состояния

    no parameters
    :return: status, time, users, messages
    as string
    """
    _result = {
        'status': True,
        'time': str(datetime.now()),
        'users': len(app.users),
        'messages': len(messages),
    }
    _output = [str(k) + ': ' + str(_result[k]) for k in _result.keys()]
    return "<hr />".join(_output)


@app.route("/messages/", methods=['GET'])
def messages_view():
    """
    Getting messages "after" (parameter set)
    Получение сообщений после отметки времени after

    input: app.after - отметка времени
    output: {
        "messages": [
            {"username": str, "text": str, "time": float},
            ...
        ]
    }
    """
    after = float(request.args.get('after', 0))
    new_messages = [message for message in messages if message['time'] > after]
    return jsonify(new_messages)


@app.route("/send", methods=['POST'])
def send_view():
    """
    Send messages, authentication is required
    Отправка сообщений от имени пользователя

    input: {
        "username": str,
        "password": str,
        "text": str
    }
    output: {"ok": bool}
    """
    data = request.json
    username = data["username"]
    password = data["password"]

    if username not in app.users or app.users[username] != password:
        logging.warning(f"{username}/{password} are not correct login credentials!")
        return jsonify({"ok": False})

    text = data["text"]
    _data = {"username": username, "text": text, "time": time.time()}
    messages.append(_data)
    logging.info(str(_data))
    return jsonify({'ok': True})


@app.route("/auth", methods=['POST'])
def auth_view():
    """
    Authorize a user - return False on fail
    Авторизовать пользователя - вернуть False в противном случае

    input: {
        "username": str,
        "password": str
    }
    output: {"ok": bool}
    """
    data = request.json
    username = data["username"]
    password = data["password"]

    if username not in app.users:
        app.users[username] = password
        return {"ok": True}
    elif app.users[username] == password:
        return {"ok": True}
    else:
        return {"ok": False}


if __name__ == 'main':
    app.run()  # run the server with default parameters
