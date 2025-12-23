import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

from .game import game_room, Role, GameState

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "blind-typing-secret")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/player")
def player_page():
    return render_template("player.html")


@app.route("/spectator")
def spectator_page():
    return render_template("spectator.html")


@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    game_room.remove_player(request.sid)
    emit("room_update", game_room.get_room_info(), broadcast=True)
    print(f"Client disconnected: {request.sid}")


@socketio.on("join_game")
def handle_join(data):
    nickname = data.get("nickname", "").strip()
    role_str = data.get("role", "player")
    password = data.get("password", "")

    if not nickname:
        emit("error", {"message": "닉네임을 입력해주세요."})
        return

    if role_str == "admin":
        if password != ADMIN_PASSWORD:
            emit("error", {"message": "어드민 비밀번호가 틀렸습니다."})
            return
        role = Role.ADMIN
    elif role_str == "spectator":
        role = Role.SPECTATOR
    else:
        role = Role.PLAYER

    success, message = game_room.add_player(request.sid, nickname, role)

    if not success:
        emit("error", {"message": message})
        return

    join_room("game")
    emit("joined", {
        "success": True,
        "role": role.value,
        "nickname": nickname,
        "room_info": game_room.get_room_info(),
    })
    emit("room_update", game_room.get_room_info(), room="game")
    emit("player_joined", {"nickname": nickname, "role": role.value}, room="game")


@socketio.on("start_game")
def handle_start_game(data):
    if request.sid not in game_room.admins:
        emit("error", {"message": "어드민만 게임을 시작할 수 있습니다."})
        return

    language = data.get("language", "korean")
    success, result = game_room.start_game(language)

    if not success:
        emit("error", {"message": result})
        return

    emit("game_started", {
        "sentence": result,
        "room_info": game_room.get_room_info(),
    }, room="game")


@socketio.on("typing_update")
def handle_typing(data):
    if game_room.state != GameState.PLAYING:
        return

    text = data.get("text", "")
    status = game_room.update_typing(request.sid, text)

    if status:
        emit("typing_broadcast", {
            "players": game_room.get_all_players_status(),
            "room_info": game_room.get_room_info(),
        }, room="game")

        if status.get("is_finished") and game_room.winner:
            emit("game_over", {
                "winner": game_room.winner.nickname,
                "finish_time": game_room.winner.finish_time,
                "room_info": game_room.get_room_info(),
            }, room="game")


@socketio.on("reset_game")
def handle_reset():
    if request.sid not in game_room.admins:
        emit("error", {"message": "어드민만 게임을 리셋할 수 있습니다."})
        return

    game_room.reset_game()
    emit("game_reset", {"room_info": game_room.get_room_info()}, room="game")


@socketio.on("get_room_info")
def handle_get_room_info():
    emit("room_update", game_room.get_room_info())


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
