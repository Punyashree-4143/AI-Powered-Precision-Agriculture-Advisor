import numpy as np
import joblib
import os
import logging

log = logging.getLogger(__name__)

class EnsembleWrapper:
    def __init__(self, xgb_path=None, cat_path=None, meta_path=None):
        self.xgb_path = xgb_path
        self.cat_path = cat_path
        self.meta_path = meta_path

    def predict(self, df_input):
        preds = []

        # XGBoost
        if self.xgb_path and os.path.exists(self.xgb_path):
            xgb = joblib.load(self.xgb_path)
            p_xgb = xgb.predict(df_input)
        else:
            p_xgb = np.zeros(len(df_input))

        # CatBoost
        p_cat = np.zeros(len(df_input))
        if self.cat_path and os.path.exists(self.cat_path):
            try:
                from catboost import CatBoostRegressor
                cb = CatBoostRegressor()
                cb.load_model(self.cat_path)
                p_cat = cb.predict(df_input)
            except Exception:
                try:
                    cb = joblib.load(self.cat_path)
                    p_cat = cb.predict(df_input)
                except Exception:
                    log.exception("CatBoost load failed")

        # Meta weights
        w_xgb, w_cat = 0.5, 0.5
        if self.meta_path and os.path.exists(self.meta_path):
            try:
                meta = joblib.load(self.meta_path)
                if isinstance(meta, dict):
                    w_xgb = meta.get("w_xgb", w_xgb)
                    w_cat = meta.get("w_cat", w_cat)
            except Exception:
                log.exception("Meta weights load failed")

        return w_xgb * np.array(p_xgb) + w_cat * np.array(p_cat)
