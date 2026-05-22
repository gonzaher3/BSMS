from flask import Flask, request, jsonify, render_template, session
from bsms_bot import handle_step

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route("/")
def home():
    session.pop("bsms_data", None)  # <--- This clears the previous session
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

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("bsms_data", None)
    return "", 204  # No content
# This route is used to reset the session data
# and clear the conversation history.
