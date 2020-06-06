from os import environ
from app import app, socketio

if __name__ == '__main__':
    port = int(environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port, threaded=True)
    socketio.run(app)
