from django.test import TestCase

from api.services.ranking import analyze_job_description


class JDAnalysisTests(TestCase):
    def test_basic_extraction(self):
        text = """
        Senior Machine Learning Engineer
        Required: Python, Machine Learning, PyTorch
        Preferred: TensorFlow, Docker
        5+ years experience in ML
        Looking for strong leadership and communication skills.
        """
        out = analyze_job_description(text, title="Senior Machine Learning Engineer")
        req = ",".join(out.get("required_skills", []))
        self.assertTrue(req)
        self.assertGreaterEqual(float(out.get("experience_min", 0)), 5.0)
