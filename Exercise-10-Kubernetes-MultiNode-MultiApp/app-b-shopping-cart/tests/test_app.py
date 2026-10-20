import unittest

from app import create_app


class ShoppingCartTests(unittest.TestCase):
    def setUp(self):
        # A new app factory instance gives every test an empty cart.
        self.client = create_app().test_client()

    def test_new_cart_is_empty(self):
        response = self.client.get("/cart")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"items": []})

    def test_valid_item_can_be_added_and_read_back(self):
        item = {
            "product_id": 1,
            "name": "Laptop",
            "price": 1200,
            "quantity": 1,
        }
        added = self.client.post("/cart", json=item)

        self.assertEqual(added.status_code, 201)
        self.assertEqual(added.get_json(), {"item": item, "message": "Item added"})
        contents = self.client.get("/cart")
        self.assertEqual(contents.status_code, 200)
        self.assertEqual(contents.get_json(), {"items": [item]})

    def test_malformed_json_is_rejected(self):
        response = self.client.post(
            "/cart", data="not json", content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_missing_or_invalid_item_fields_are_rejected(self):
        response = self.client.post("/cart", json={"product_id": 1, "name": "Laptop"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(), {"error": "price must be a non-negative number"}
        )

    def test_non_json_content_type_is_rejected(self):
        response = self.client.post("/cart", data="{}", content_type="text/plain")

        self.assertEqual(response.status_code, 415)

    def test_health_endpoint_is_successful(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
