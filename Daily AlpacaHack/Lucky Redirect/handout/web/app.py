import re
from flask import Flask, url_for, redirect
import secrets

FLAG = "Alpaca{Ill_never_gamble_again_I_bet_on_it}"
assert re.fullmatch(r"Alpaca\{\w+\}", FLAG)

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("nope"))


for i in range(len(FLAG)):
    def make_route(i):
        @app.get("/" + "/".join(FLAG[:i+1]), endpoint=f"flag_{i}")
        def route():
            is_lucky = secrets.randbelow(5) == 0
            if is_lucky and i == len(FLAG) - 1:
                return f"Well done! The flag is: {FLAG}"
            elif is_lucky:
                return redirect(url_for(f"flag_{i+1}"))
            else:
                return redirect(url_for("nope"))

        return route

    make_route(i)


@app.get("/nope")
def nope():
    return "Nope"

@app.get("/")
def index():
    return '<a href="/A">Feeling lucky?</a>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
