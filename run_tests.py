import unittest

if __name__ == "__main__":
    # Automatically finds tests in folder "tests"
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
