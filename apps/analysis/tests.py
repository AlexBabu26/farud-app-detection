from types import SimpleNamespace

from django.test import SimpleTestCase

from .views import _calibrate_label_from_reviews


class LabelCalibrationTests(SimpleTestCase):
    def _base_validated(self):
        return {
            "label": "SUSPICIOUS",
            "confidence": 0.4,
            "rationale": "Limited evidence.",
            "key_signals": [],
            "safety_score": 60,
            "addiction_risk": "LOW",
            "privacy_concerns": [],
            "top_bugs": [],
            "feature_requests": [],
            "sentiment_breakdown": {"anger": 20, "joy": 20, "fear": 20, "sadness": 20},
            "privacy_risk_score": 50,
            "privacy_policy_readability": "MISSING",
            "data_sharing_concerns": [],
            "safety_recommendation": "",
            "recommendation_action": "PROCEED_WITH_CAUTION",
            "health_scores": {"safety": 50, "privacy": 50, "quality": 50, "trust": 50, "sentiment": 50},
        }

    def test_calibration_promotes_legit_for_consistent_positive_reviews(self):
        reviews = [
            SimpleNamespace(text="Great app, very reliable and useful.", rating=5),
            SimpleNamespace(text="Excellent experience, smooth and clean UI.", rating=5),
            SimpleNamespace(text="Really good and safe app.", rating=4),
        ]
        calibrated = _calibrate_label_from_reviews(self._base_validated(), reviews)
        self.assertEqual(calibrated["label"], "LEGIT")
        self.assertEqual(calibrated["recommendation_action"], "SAFE_TO_INSTALL")
        self.assertGreaterEqual(calibrated["confidence"], 0.72)

    def test_calibration_promotes_fraud_for_severe_negative_signals(self):
        reviews = [
            SimpleNamespace(text="Scam app. Unauthorized charge and stolen money.", rating=1),
            SimpleNamespace(text="Fraud! Fake payment and phishing behavior.", rating=1),
            SimpleNamespace(text="Do not install. This is malware.", rating=1),
        ]
        calibrated = _calibrate_label_from_reviews(self._base_validated(), reviews)
        self.assertEqual(calibrated["label"], "FRAUD")
        self.assertEqual(calibrated["recommendation_action"], "RECOMMEND_UNINSTALL")
        self.assertGreaterEqual(calibrated["confidence"], 0.72)

    def test_calibration_keeps_suspicious_for_mixed_signals(self):
        reviews = [
            SimpleNamespace(text="Works okay but crashes sometimes.", rating=3),
            SimpleNamespace(text="Good features, but lots of ads.", rating=4),
            SimpleNamespace(text="Not bad, not great.", rating=3),
        ]
        calibrated = _calibrate_label_from_reviews(self._base_validated(), reviews)
        self.assertEqual(calibrated["label"], "SUSPICIOUS")
        self.assertEqual(calibrated["recommendation_action"], "PROCEED_WITH_CAUTION")
