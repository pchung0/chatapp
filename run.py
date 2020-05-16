from chatapp import app, socketio
# from chatroom import app, socketio
if __name__ == "__main__":
    # socketio.run(app, use_reloader=True)
    socketio.run(app, debug=True, port=5005)