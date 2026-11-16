from pathlib import Path
import joblib
import numpy as np
from app.core.config import settings

class Predictor:
    def __init__(self):
        self.ctr_model = None
        self.cvr_model = None
        self.version = "baseline-v1"
        self._load()

    def _load(self):
        root = Path(settings.model_dir)
        try:
            self.ctr_model = joblib.load(root / "ctr_model.joblib")
            self.cvr_model = joblib.load(root / "cvr_model.joblib")
            self.version = "sklearn-logistic-v1"
        except Exception:
            self.ctr_model = self.cvr_model = None

    def _vector(self, request, campaign, features):
        # Fixed numeric feature schema shared by training and inference.
        return np.array([[
            float(campaign.base_ctr),
            float(campaign.base_cvr),
            float(request.device == "mobile"),
            float(request.country == "FR"),
            float(request.page_category == campaign.category),
            float(features.get("user_clicks", 0)),
            float(features.get("user_impressions", 0)),
        ]])

    def predict(self, request, campaign, features):
        x = self._vector(request, campaign, features)
        if self.ctr_model is not None and self.cvr_model is not None:
            ctr = float(self.ctr_model.predict_proba(x)[0, 1])
            cvr = float(self.cvr_model.predict_proba(x)[0, 1])
        else:
            # Cold-start-friendly prior with conservative context adjustment.
            relevance = 1.15 if request.page_category == campaign.category else 0.85
            ctr = campaign.base_ctr * relevance
            cvr = campaign.base_cvr * (1.05 if request.device == "mobile" else 1.0)
        return min(max(ctr, 0.0001), 0.95), min(max(cvr, 0.0001), 0.95)
