import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app)

# store connected users by socket id
users = {}

# store room metadata
rooms = {}
# rooms = {
#   "roomName": {
#       "creator": "Adrish",
#       "users": set(["Adrish", "Sherry"])
#   }
# }

@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def handle_join(data):
    username = data["username"]
    room = data["room"]

    users[request.sid] = {
        "username": username,
        "room": room
    }

    # create room if first time
    if room not in rooms:
        rooms[room] = {
            "creator": username,
            "users": set()
        }

    rooms[room]["users"].add(username)
    join_room(room)

    emit(
        "message",
        {"msg": f"{username} has joined the room."},
        room=room
    )

    emit(
        "room_info",
        {
            "creator": rooms[room]["creator"],
            "online_users": list(rooms[room]["users"])
        },
        room=room
    )


@socketio.on("send_message")
def handle_message(data):
    user = users.get(request.sid)
    if not user:
        return

    username = user["username"]
    room = user["room"]

    emit(
        "message",
        {"msg": f"{username}: {data['message']}"},
        room=room
    )


@socketio.on("disconnect")
def handle_disconnect():
    user = users.get(request.sid)
    if not user:
        return

    username = user["username"]
    room = user["room"]

    if room in rooms:
        rooms[room]["users"].discard(username)

        emit(
            "message",
            {"msg": f"{username} left the room."},
            room=room
        )

        emit(
            "room_info",
            {
                "creator": rooms[room]["creator"],
                "online_users": list(rooms[room]["users"])
            },
            room=room
        )

    users.pop(request.sid, None)


if __name__ == "__main__":
    socketio.run(app, debug=True)
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)

