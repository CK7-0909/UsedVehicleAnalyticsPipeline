import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# Stub heavy external modules before importing api.main.
mock_sf_module = types.ModuleType("ml.data.snowflake.sf_connection")
mock_sf_module.query_to_df = lambda: MagicMock()
sys.modules["ml.data.snowflake.sf_connection"] = mock_sf_module

mock_predict_module = types.ModuleType("ml.src.predict")
mock_predict_module.predict = lambda df, path: [0.0]
sys.modules["ml.src.predict"] = mock_predict_module

from fastapi.testclient import TestClient

from api.main import app


class TestVehiclesAskEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("api.main.query_specs")
    @patch("api.main.run_query")
    @patch("api.main.parse_filters")
    def test_vehicles_ask_returns_filters_and_specs(
        self, mock_parse_filters, mock_run_query, mock_query_specs
    ):
        mock_parse_filters.return_value = {
            "price_min": None,
            "price_max": 20000,
            "year_min": 2015,
            "year_max": None,
            "body_type": "sedan",
            "reference_model": None,
            "limit": None,
        }
        mock_df = MagicMock()
        mock_df.head.return_value.to_dict.return_value = [{"id": 1, "model": "Toyota Corolla"}]
        mock_df.__len__.return_value = 1
        mock_run_query.return_value = mock_df
        mock_query_specs.return_value = [
            {
                "document": "Specs chunk",
                "metadata": {"model": "Toyota Corolla"},
                "distance": 0.1,
            }
        ]

        response = self.client.post(
            "/vehicles/ask?spec_top_k=1",
            json={"question": "Find a Corolla sedan under 20k"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("filters_used", body)
        self.assertIn("results", body)
        self.assertIn("spec_results", body)
        self.assertEqual(body["spec_results"][0]["document"], "Specs chunk")


if __name__ == "__main__":
    unittest.main()
