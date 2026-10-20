from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, this is a secure Flask application running inside a Docker container!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
