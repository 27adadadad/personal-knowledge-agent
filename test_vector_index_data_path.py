import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import rag_files
import vector_index
from agent_config import VECTOR_INDEX_FILE


class VectorIndexDataPathTests(unittest.TestCase):
    def test_save_vector_index_uses_data_dir(self):
        with TemporaryDirectory() as temp_dir:
            with patch.object(rag_files.settings, "data_dir", temp_dir):
                vector_index.save_vector_index(
                    [],
                    "test-hash"
                )

            file_path = Path(temp_dir) / VECTOR_INDEX_FILE

            self.assertTrue(file_path.exists())

            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

        self.assertEqual(data["knowledge_hash"], "test-hash")
        self.assertEqual(data["items"], [])

    def test_load_vector_index_uses_data_dir(self):
        expected_data = {
            "knowledge_hash": "test-hash",
            "items": []
        }

        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / VECTOR_INDEX_FILE

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(expected_data, file, ensure_ascii=False, indent=2)

            with patch.object(rag_files.settings, "data_dir", temp_dir):
                result = vector_index.load_vector_index()

        self.assertEqual(result, expected_data)


if __name__ == "__main__":
    unittest.main()