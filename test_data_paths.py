import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import rag_files
from agent_config import VECTOR_INDEX_FILE


class DataFilePathTests(unittest.TestCase):
    def test_get_data_file_path_uses_project_dir_when_data_dir_is_not_set(self):
        with patch.object(rag_files.settings, "data_dir", None):
            result = rag_files.get_data_file_path(VECTOR_INDEX_FILE)

        expected = rag_files.get_file_path(VECTOR_INDEX_FILE)

        self.assertEqual(result, expected)

    def test_get_data_file_path_uses_data_dir_when_it_is_set(self):
        with TemporaryDirectory() as temp_dir:
            with patch.object(rag_files.settings, "data_dir", temp_dir):
                result = rag_files.get_data_file_path(VECTOR_INDEX_FILE)

            expected = Path(temp_dir) / VECTOR_INDEX_FILE

            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()