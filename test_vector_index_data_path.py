import os
import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from agent_config import VECTOR_INDEX_FILE
import vector_index


class VectorIndexDataPathTests(unittest.TestCase):
    def test_save_vector_index_uses_data_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            expected_path = Path(temp_dir) / VECTOR_INDEX_FILE

            with patch.dict(
                os.environ,
                {"DATA_DIR": temp_dir}
            ):
                with patch.object(
                    vector_index,
                    "get_file_path",
                    create=True,
                    side_effect=AssertionError(
                        "保存索引时不应使用 get_file_path"
                    )
                ):
                    vector_index.save_vector_index(
                        [],
                        "test-hash"
                    )

            self.assertTrue(expected_path.exists())

    def test_load_vector_index_uses_data_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            expected_data = {
                "knowledge_hash": "test-hash",
                "items": []
            }

            data_path = Path(temp_dir) / VECTOR_INDEX_FILE

            with open(data_path, "w", encoding="utf-8") as file:
                json.dump(
                    expected_data,
                    file,
                    ensure_ascii=False
                )

            with patch.dict(
                os.environ,
                {"DATA_DIR": temp_dir}
            ):
                with patch.object(
                    vector_index,
                    "get_file_path",
                    create=True,
                    side_effect=AssertionError(
                        "读取索引时不应使用 get_file_path"
                    )
                ):
                    result = vector_index.load_vector_index()

            self.assertEqual(result, expected_data)


if __name__ == "__main__":
    unittest.main()