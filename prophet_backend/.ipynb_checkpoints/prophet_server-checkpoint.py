# prophet_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os, pickle, re, traceback, io, logging

# Optional: if some models were saved with joblib
try:
    import joblib
except Exception:
    joblib = None

# If you used prophet's JSON serialization
try:
    from prophet.serialize import model_from_json
except Exception:
    model_from_json = None

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prophet_server")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "backend", "models"))

logger.info("MODELS_DIR = %s", MODELS_DIR)

# ---------- Helper: Normalize text ----------
def normalize(s: str) -> str:
    if not isinstance(s, str):
        return ""
    # remove weird unicode spaces, collapse multiple spaces, lowercase, strip
    s = s.replace("\u00A0", " ")  # non-breaking
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()

# ---------- Try to load a model from path ----------
def load_prophet_model(path):
    logger.info("Attempting to load model from: %s", path)
    # 1) try pickle
    try:
        with open(path, "rb") as f:
            model = pickle.load(f)
        logger.info("Loaded model via pickle from %s", path)
        return model
    except Exception as e:
        logger.info("pickle load failed: %s", e)

    # 2) try joblib
    if joblib is not None:
        try:
            model = joblib.load(path)
            logger.info("Loaded model via joblib from %s", path)
            return model
        except Exception as e:
            logger.info("joblib load failed: %s", e)

    # 3) try prophet json
    if model_from_json is not None:
        try:
            with open(path, "r") as f:
                model = model_from_json(f.read())
            logger.info("Loaded model via prophet JSON from %s", path)
            return model
        except Exception as e:
            logger.info("prophet json load failed: %s", e)

    raise RuntimeError("Unable to load model: no supported loader succeeded.")

# ---------- Find best matching model file ----------
def find_model_file(commodity: str, market: str, suffix="_prophet.pkl"):
    norm_com = normalize(commodity)
    norm_mar = normalize(market)

    # exact normalized match first
    for f in os.listdir(MODELS_DIR):
        if not f.lower().endswith(suffix):
            continue
        parts = f.split("__")
        if len(parts) < 2:
            continue
        file_com = normalize(parts[0])
        file_mar = normalize(parts[1])
        if file_com == norm_com and file_mar == norm_mar:
            return os.path.join(MODELS_DIR, f)

    # fallback: try contains (robust when punctuation differs)
    for f in os.listdir(MODELS_DIR):
        if not f.lower().endswith(suffix):
            continue
        parts = f.split("__")
        if len(parts) < 2:
            continue
        file_com = normalize(parts[0])
        file_mar = normalize(parts[1])
        if norm_com in file_com and norm_mar in file_mar:
            return os.path.join(MODELS_DIR, f)

    # last resort: any file that startswith commodity
    for f in os.listdir(MODELS_DIR):
        if not f.lower().endswith(suffix):
            continue
        parts = f.split("__")
        if len(parts) < 2:
            continue
        file_com = normalize(parts[0])
        if file_com == norm_com:
            return os.path.join(MODELS_DIR, f)

    return None

@app.route("/api/forecast/7", methods=["GET"])
def forecast_7():
    try:
        commodity = request.args.get("commodity", "")
        market = request.args.get("market", "")
        logger.info("Request - commodity: %s market: %s", commodity, market)

        if not commodity or not market:
            return jsonify({"error": "commodity and market query params required"}), 400

        model_file = find_model_file(commodity, market, suffix="_prophet.pkl")
        if not model_file:
            msg = f"No prophet model file found for {commodity} / {market}"
            logger.warning(msg)
            return jsonify({"error": msg}), 404

        # load model
        model = load_prophet_model(model_file)

        # ensure model has make_future_dataframe & predict
        if not hasattr(model, "make_future_dataframe") or not hasattr(model, "predict"):
            msg = "Loaded object is not a Prophet-like model (missing methods)."
            logger.error(msg)
            return jsonify({"error": msg}), 500

        # create future and predict
        future = model.make_future_dataframe(periods=7)
        forecast_df = model.predict(future).tail(7)

        output = []
        for _, row in forecast_df.iterrows():
            ds = row.get("ds")
            yhat = row.get("yhat")
            yhat_lower = row.get("yhat_lower")
            yhat_upper = row.get("yhat_upper")
            output.append({
                "date": str(ds.date()) if hasattr(ds, "date") else str(ds),
                "predicted_price": float(yhat) if yhat is not None else None,
                "min_expected_price": float(yhat_lower) if yhat_lower is not None else None,
                "max_expected_price": float(yhat_upper) if yhat_upper is not None else None
            })

        return jsonify({
            "commodity": commodity,
            "market": market,
            "model_file": os.path.basename(model_file),
            "forecast": output
        })

    except Exception as e:
        # log full traceback for debugging
        tb = traceback.format_exc()
        logger.error("Unhandled exception:\n%s", tb)
        # Return error message and traceback fragment (useful while debugging locally)
        return jsonify({"error": str(e), "traceback": tb.splitlines()[-20:]}), 500

@app.route("/api/models/list", methods=["GET"])
def list_models():
    try:
        files = sorted(os.listdir(MODELS_DIR))
        return jsonify({"files": files})
    except Exception as e:
        logger.exception("Failed to list models")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return {"status": "Prophet backend running", "models_dir": MODELS_DIR}

if __name__ == "__main__":
    # quick sanity check
    if not os.path.isdir(MODELS_DIR):
        logger.error("MODELS_DIR does not exist: %s", MODELS_DIR)
    logger.info("Starting prophet server on port 5001...")
    app.run(host="0.0.0.0", port=5001, debug=False)
