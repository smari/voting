import unittest
from tests import *

if __name__ == '__main__':
    tests = unittest.TestLoader().discover('tests', pattern='*.py', top_level_dir=".")
    unittest.TextTestRunner(buffer=True).run(tests)

