from flask import Flask, request

app = Flask(__name__)

@app.route('/flag', methods=["GET", "POST", "OPTIONS"])
def flag():
    if len(request.get_data()) > 0:
        return 'Hacker!'
    return "<3"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001)