"""Small hand-authored educational fixtures, not an independent benchmark.

These examples are bundled/trusted. They must never be overwritten with user input.
"""

_BOUNDARY_SOURCE = '''def eligible(age):
    return age >= 18
'''
_BOUNDARY_TESTS = '''import unittest
from subject import eligible

class EligibilityTests(unittest.TestCase):
    def test_underage(self):
        self.assertFalse(eligible(17))

    def test_exact_boundary(self):
        self.assertTrue(eligible(18))

    def test_above_boundary(self):
        self.assertTrue(eligible(19))
'''

SAMPLES = [
    {
        "id": "missing_regression",
        "title": "A removed boundary assertion hides a regression",
        "requirement": "A person is eligible if and only if their age is at least 18. In particular, age 18 must be eligible and age 17 must not be eligible.",
        "source_before": _BOUNDARY_SOURCE,
        "source_after": '''def eligible(age):
    return age > 18
''',
        "tests_before": _BOUNDARY_TESTS,
        "tests_after": '''import unittest
from subject import eligible

class EligibilityTests(unittest.TestCase):
    def test_underage(self):
        self.assertFalse(eligible(17))

    def test_above_boundary(self):
        self.assertTrue(eligible(19))
''',
    },
    {
        "id": "legitimate_refactor",
        "title": "A legitimate table-driven test refactor",
        "requirement": "A person is eligible if and only if their age is at least 18. In particular, age 18 must be eligible and age 17 must not be eligible.",
        "source_before": _BOUNDARY_SOURCE,
        "source_after": _BOUNDARY_SOURCE,
        "tests_before": _BOUNDARY_TESTS,
        "tests_after": '''import unittest
from subject import eligible

class EligibilityTests(unittest.TestCase):
    def test_eligibility_cases(self):
        for age, expected in [(17, False), (18, True), (19, True)]:
            with self.subTest(age=age):
                self.assertEqual(eligible(age), expected)
''',
    },
    {
        "id": "missing_spec",
        "title": "Changed behavior without an authoritative requirement",
        "requirement": "",
        "source_before": '''def shipping_cost(total):
    return 0 if total >= 50 else 5
''',
        "source_after": '''def shipping_cost(total):
    return 0 if total > 50 else 5
''',
        "tests_before": '''import unittest
from subject import shipping_cost

class ShippingTests(unittest.TestCase):
    def test_threshold(self):
        self.assertEqual(shipping_cost(50), 0)
''',
        "tests_after": '''import unittest
from subject import shipping_cost

class ShippingTests(unittest.TestCase):
    def test_threshold(self):
        self.assertEqual(shipping_cost(50), 5)
''',
    },
    {
        "id": "supported_boundary",
        "title": "Boundary requirement backed by an explicit assertion",
        "requirement": "A person is eligible if and only if their age is at least 18. In particular, age 18 must be eligible and age 17 must not be eligible.",
        "source_before": _BOUNDARY_SOURCE,
        "source_after": _BOUNDARY_SOURCE,
        "tests_before": '''import unittest
from subject import eligible

class EligibilityTests(unittest.TestCase):
    def test_above_boundary(self):
        self.assertTrue(eligible(19))
''',
        "tests_after": _BOUNDARY_TESTS,
    },
]
