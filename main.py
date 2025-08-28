# main.py
from flask import Flask, request, jsonify
from forge_package import build_package

app = Flask(__name__)

@app.route("/optimise", methods=["POST"])
def optimise():
    data = request.json or {}

    package_goal = data.get("package_goal")
    prompt = data.get("prompt")
    resources = data.get("resources", [])
    caption = data.get("caption", "")
    user_id = data.get("user_id", "default")

    # Validate
    if not package_goal or not prompt:
        return jsonify({"error": "Missing required fields: package_goal and prompt"}), 400

    # Build package
    package = build_package(package_goal, prompt, resources, caption, user_id)

    return jsonify(package)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
