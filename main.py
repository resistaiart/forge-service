# main.py
from flask import Flask, request, jsonify
from forge_package import build_package
from forge_image_analysis import analyse_image

app = Flask(__name__)

@app.route("/optimise", methods=["POST"])
def optimise():
    data = request.json or {}

    package_goal = data.get("package_goal")
    prompt = data.get("prompt")
    resources = data.get("resources", [])
    caption = data.get("caption", "")
    user_id = data.get("user_id", "default")

    if not package_goal or not prompt:
        return jsonify({"error": "Missing required fields: package_goal and prompt"}), 400

    package = build_package(package_goal, prompt, resources, caption, user_id)
    return jsonify(package)


@app.route("/analyse_image", methods=["POST"])
def analyse_image_endpoint():
    """
    Analyse an uploaded image (by URL or base64).
    Returns structured descriptors: subject, style, tags, caption.
    """
    data = request.json or {}
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "No image provided"}), 400

    descriptors = analyse_image(image_url)
    return jsonify(descriptors)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
