import unittest

import test_math
import test_load

def suite():
  return unittest.TestSuite(
    (
      test_math.suite,
      test_load.suite
    )
  )

if __name__ == "__main__":
  unittest.TextTestRunner().run(suite())
