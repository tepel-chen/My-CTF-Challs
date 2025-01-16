from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'hello'

@app.route('/flag', methods=["GET", "POST", "OPTIONS"])
def flag():
    return 'Hacker!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001)