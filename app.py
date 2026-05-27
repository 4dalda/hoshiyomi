"""Flask web server for 星詠みChronicle PDF generation."""
import os
import sys
from datetime import date
from flask import Flask, request, send_file, render_template, jsonify
from io import BytesIO

sys.path.insert(0, os.path.dirname(__file__))
from fortune_calculator import calculate_all
from pdf_generator import generate_pdf

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)

    # Validate
    required = ["year", "month", "day", "blood", "navigator", "name"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        year      = int(data["year"])
        month     = int(data["month"])
        day       = int(data["day"])
        blood     = str(data["blood"]).upper()
        navigator = str(data["navigator"])
        name      = str(data["name"]).strip() or "ゲスト"
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400

    today = date.today()
    if not (1920 <= year <= today.year):
        return jsonify({"error": "生年月日の年が範囲外です"}), 400
    if blood not in ("A", "B", "O", "AB"):
        return jsonify({"error": "血液型が不正です"}), 400
    if navigator not in ("叢雲", "ノヴァ", "フレイヤ", "グレイス"):
        return jsonify({"error": "ニャビゲーターが不正です"}), 400

    try:
        fortune_data = calculate_all(year, month, day, blood, navigator, name)
        pdf_bytes    = generate_pdf(fortune_data)
    except Exception as e:
        app.logger.exception("PDF generation failed")
        return jsonify({"error": f"PDF生成エラー: {str(e)}"}), 500

    filename = f"hoshiyomi_{name}_{fortune_data['type']['name']}.pdf"
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/api/preview", methods=["POST"])
def preview():
    """Return fortune data as JSON (for live preview in UI)."""
    data = request.get_json(force=True)
    try:
        year      = int(data.get("year", 1990))
        month     = int(data.get("month", 1))
        day       = int(data.get("day", 1))
        blood     = str(data.get("blood", "A")).upper()
        navigator = str(data.get("navigator", "叢雲"))
        name      = str(data.get("name", "ゲスト")).strip() or "ゲスト"
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400

    from fortune_data import get_navigator_message
    fortune_data = calculate_all(year, month, day, blood, navigator, name)
    nav_msg = get_navigator_message(navigator, fortune_data["type_id"], name)

    return jsonify({
        "type_id":   fortune_data["type_id"],
        "type_name": fortune_data["type"]["name"],
        "type_keyword": fortune_data["type"]["keyword"],
        "zodiac":    fortune_data["zodiac"]["name"],
        "chinese":   fortune_data["chinese"]["name"],
        "life_path": fortune_data["life_path"]["number"],
        "scores":    fortune_data["scores"],
        "navigator_message": nav_msg["message"][:60] + "……",
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"★ 星詠みChronicle サーバー起動中 → http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
