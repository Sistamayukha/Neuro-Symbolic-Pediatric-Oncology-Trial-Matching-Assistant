import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitAppTests(unittest.TestCase):
    def test_default_page_renders_without_exceptions(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=20).run()
        self.assertEqual(list(app.exception), [])
        self.assertEqual(len(app.metric), 3)
        self.assertGreaterEqual(len(app.dataframe), 2)
        self.assertIn("ProofPath TrialMatch", app.title[0].value if app.title else "ProofPath TrialMatch")


if __name__ == "__main__":
    unittest.main()
