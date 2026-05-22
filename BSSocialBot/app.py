import os
from flask import Flask, request, jsonify, render_template, session
from bsms_bot import handle_step

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "supersecretkey_fallback_for_development")

@app.route("/")
def home():
    session.pop("bsms_data", None)  # Clear the previous session
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    session_data = session.get("bsms_data", {"step": 0, "responses": {}})
    reply, updated_data = handle_step(session_data, user_input)

    if updated_data:
        session["bsms_data"] = updated_data
    else:
        session.pop("bsms_data", None)

    return jsonify({"reply": reply})

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("bsms_data", None)
    return "", 204  # No content

# Health check endpoint for deployment
@app.route("/health")
def health():
    return {"status": "healthy"}, 200
