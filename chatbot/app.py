from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import chatbot

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

socketio = SocketIO(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/get')
def chatbot_response():
    user_input = request.args.get('msg', '')
    # TODO: process user_input with chatbot and get the chatbot response
    res = chatbot.get_user_response(user_input)
    #res = "hello i am me"
    return res





if __name__ == "__main__":
    socketio.run(app, debug=True)
