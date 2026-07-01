from django.test import TestCase

from api.services.jd_understanding import analyze_job_description


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
        self.assertIn("python", ",".join(out["required_skills"]))
        self.assertEqual(out["seniority"], "senior")
        self.assertTrue(float(out["experience_years"]) >= 5.0)
        self.assertIn("leadership", out["behavioral_traits"])
