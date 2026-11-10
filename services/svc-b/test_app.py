import unittest

from app import greet


class AppTest(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("x"), "svc-b hello x")


if __name__ == "__main__":
    unittest.main()
