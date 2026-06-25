import os
import unittest
from pathlib import Path
from unittest.mock import patch

import rag_files



class DataFilePathTests(unittest.TestCase):
    def test_get_data_file_path_uses_project_dir_when_data_dir_is_not_set(
        self
    ):
        with patch.dict(os.environ, {}, clear=True):
            result = rag_files.get_data_file_path(
                "vector_index.json"
            )

        expected = (
            Path(rag_files.__file__).parent
            / "vector_index.json"
        )

        self.assertEqual(result, expected)

    def test_get_data_file_path_uses_data_dir_when_it_is_set(
        self
    ):
        with patch.dict(
            os.environ,
            {"DATA_DIR": "/data"}
        ):
            result = rag_files.get_data_file_path(
                "vector_index.json"
            )

        self.assertEqual(
            result,
            Path("/data") / "vector_index.json"
        )

if __name__ == "__main__":
    unittest.main()

