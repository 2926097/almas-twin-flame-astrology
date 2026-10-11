import unittest
from private_gate import PersonalAnalysisDisabled, require_personal_processing_allowed

class TestPrivateGate(unittest.TestCase):
    def test_default_denial(self):
        with self.assertRaises(PersonalAnalysisDisabled):
            require_personal_processing_allowed()

    def test_user_arguments_cannot_override_denial(self):
        with self.assertRaises(PersonalAnalysisDisabled):
            require_personal_processing_allowed(consent=True, authenticated=True)

if __name__ == "__main__":
    unittest.main()
