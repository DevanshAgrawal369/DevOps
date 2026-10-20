"""Small, read-only product catalog API for Exercise 10."""

import os

from flask import Flask, jsonify


PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 1200},
    {"id": 2, "name": "Phone", "price": 800},
    {"id": 3, "name": "Headphones", "price": 150},
]


def create_app():
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/products")
    def products():
        return jsonify(products=PRODUCTS)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        debug=False,
    )
