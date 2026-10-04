import os
from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# You can override this when running the container:
#   -e MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english
MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")

# Load the pretrained model once at startup (faster requests)
classifier = pipeline("text-classification", model=MODEL_NAME)

 
@app.get("/health")
def health():
    return jsonify({"status": "ok", "model": MODEL_NAME})


@app.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}

    # Accept either a single string or a list of strings
    text = data.get("text", None)
    if text is None:
        return jsonify({"error": "Missing required field 'text'. Provide a string or list of strings."}), 400

    # Run inference
    try:
        result = classifier(text)
    except Exception as e:
        return jsonify({"error": f"Inference failed: {str(e)}"}), 500

    return jsonify({"predictions": result})


if __name__ == "__main__":
    # Waitress is a production-ready WSGI server (better than Flask dev server)
    from waitress import serve

    port = int(os.getenv("PORT", "5001"))
    serve(app, host="0.0.0.0", port=port)
