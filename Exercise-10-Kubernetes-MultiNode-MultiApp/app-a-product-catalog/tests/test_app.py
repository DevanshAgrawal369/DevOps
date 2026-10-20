import unittest

from app import create_app


class ProductCatalogTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_products_returns_the_expected_catalog(self):
        response = self.client.get("/products")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "products": [
                    {"id": 1, "name": "Laptop", "price": 1200},
                    {"id": 2, "name": "Phone", "price": 800},
                    {"id": 3, "name": "Headphones", "price": 150},
                ]
            },
        )

    def test_health_endpoint_is_successful(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
