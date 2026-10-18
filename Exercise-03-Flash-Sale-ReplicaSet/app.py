
from flask import Flask, request
import socket
import time
import random

app = Flask(__name__)


@app.get("/")
def homepage():
    return {
        "message": "Welcome to Big Sale!",
        "pod": socket.gethostname(),
        "ts": time.time()
    }


@app.get("/buy")
def buy():
    item = random.choice([
        "Smartphone",
        "Shoes",
        "Headphones",
        "Laptop"
    ])

    user = request.args.get(
        "user",
        f"user{random.randint(1, 1000)}"
    )

    return {
        "status": "success",
        "item": item,
        "user": user,
        "served_by_pod": socket.gethostname(),
        "time": time.strftime("%H:%M:%S")
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "pod": socket.gethostname()
    }
