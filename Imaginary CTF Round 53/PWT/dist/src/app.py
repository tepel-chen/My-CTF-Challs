from functools import wraps
from flask import Flask, flash, make_response, redirect, request, render_template, url_for
import pickle
import base64
from Crypto.Cipher import AES
from hashlib import sha256
from Crypto.Util.Padding import pad
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)

SHA_KEY = os.urandom(16)
AES_KEY = os.urandom(16)
AES_IV = os.urandom(16)

def encrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return base64.b64encode(encrypted).decode()

def decrypt(data):
    decoded = base64.b64decode(data)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    decrypted = cipher.decrypt(decoded)
    return decrypted[:-decrypted[-1]]


def auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        pkl = request.cookies.get("pkl")
        if pkl:
            try:
                pickled_data = decrypt(pkl)
                username, hash = pickle.loads(pickled_data)
                assert sha256(SHA_KEY + username.encode()).digest() == hash
                return f(username, *args, **kwargs)
            except:
                flash("Invalid pickle data", "error")
                return redirect(url_for('register'))
        return redirect(url_for('register'))
    return decorated

@app.route('/')
@auth
def index(username):
    return f"Welcome, {username}"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')

        hash = sha256(SHA_KEY + username.encode()).digest()
        pickled_data = pickle.dumps((username, hash))

        encrypted_pkl = encrypt(pickled_data)
        response = make_response(redirect(url_for('index')))
        response.set_cookie("pkl", encrypted_pkl, max_age=3600)
        return response
    return render_template('register.html')

if __name__ == '__main__':
    app.run(port=8000, host="0.0.0.0")