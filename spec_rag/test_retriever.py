import unittest
from unittest.mock import MagicMock, patch

from spec_rag import retriever


class TestSpecRagRetriever(unittest.TestCase):
    def test_query_specs_requires_non_empty_query(self):
        with self.assertRaises(ValueError):
            retriever.query_specs("")

    def test_query_specs_accepts_valid_query_and_returns_documents(self):
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]

        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["chunk one", "chunk two"]],
            "metadatas": [[{"model": "Honda Accord"}, {"model": "Volkswagen Jetta"}]],
            "distances": [[0.12, 0.34]],
        }

        with patch("spec_rag.retriever._load_model", return_value=mock_model), patch(
            "spec_rag.retriever._get_collection", return_value=mock_collection
        ) as mock_get_collection:
            results = retriever.query_specs("Explain the Jetta suspensions.", n_results=2)

        mock_model.encode.assert_called_once_with(["Explain the Jetta suspensions."])
        mock_get_collection.assert_called_once()
        mock_collection.query.assert_called_once()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["document"], "chunk one")
        self.assertEqual(results[0]["metadata"], {"model": "Honda Accord"})
        self.assertEqual(results[0]["distance"], 0.12)

    def test_query_specs_rejects_non_positive_n_results(self):
        with self.assertRaises(ValueError):
            retriever.query_specs("Valid question", n_results=0)


if __name__ == "__main__":
    unittest.main()
