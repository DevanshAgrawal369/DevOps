"""Small in-memory shopping cart API for Exercise 10."""

import math
import os

from flask import Flask, jsonify, request


def create_app():
    app = Flask(__name__)
    # Each app process (and therefore each pod) has independent, temporary state.
    cart = []

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/cart")
    def get_cart():
        return jsonify(items=list(cart))

    @app.post("/cart")
    def add_to_cart():
        if not request.is_json:
            return jsonify(error="Content-Type must be application/json"), 415

        item = request.get_json(silent=True)
        if not isinstance(item, dict):
            return jsonify(error="Request body must be a JSON object"), 400

        product_id = item.get("product_id")
        name = item.get("name")
        price = item.get("price")
        quantity = item.get("quantity")

        if (
            isinstance(product_id, bool)
            or not isinstance(product_id, int)
            or product_id <= 0
        ):
            return jsonify(error="product_id must be a positive integer"), 400
        if not isinstance(name, str) or not name.strip():
            return jsonify(error="name must be a non-empty string"), 400
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            return jsonify(error="price must be a non-negative number"), 400
        if not math.isfinite(price) or price < 0:
            return jsonify(error="price must be a non-negative finite number"), 400
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity < 1
        ):
            return jsonify(error="quantity must be a positive integer"), 400

        added = {
            "product_id": product_id,
            "name": name.strip(),
            "price": price,
            "quantity": quantity,
        }
        cart.append(added)
        return jsonify(item=added, message="Item added"), 201

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        debug=False,
    )
