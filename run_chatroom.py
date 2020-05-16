from chatroom import app, socketio
if __name__ == "__main__":
    # app.run(use_reloader=True)
    socketio.run(app, debug=True, port=5001)
    # socketio.run(app, use_reloader=True, port=5001)