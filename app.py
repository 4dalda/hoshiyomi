"""Flask web server for 星詠みChronicle PDF generation."""
import os
import sys
import uuid
from datetime import date, datetime, timedelta
from flask import Flask, request, send_file, render_template, jsonify, redirect
from io import BytesIO

sys.path.insert(0, os.path.dirname(__file__))
from fortune_calculator import calculate_all
from pdf_generator import generate_pdf

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB

import stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

PRICE_JPY = 500
_pending_orders: dict = {}


def _cleanup_orders():
    now = datetime.utcnow()
    expired = [k for k, v in _pending_orders.items() if now > v["expires"]]
    for k in expired:
        del _pending_orders[k]


def _validate_form(data: dict):
    required = ["year", "month", "day", "blood", "navigator", "name"]
    for field in required:
        if field not in data:
            return None, f"Missing field: {field}"
    try:
        year      = int(data["year"])
        month     = int(data["month"])
        day       = int(data["day"])
        blood     = str(data["blood"]).upper()
        navigator = str(data["navigator"])
        name      = str(data["name"]).strip() or "ゲスト"
    except (ValueError, TypeError) as e:
        return None, str(e)

    today = date.today()
    if not (1920 <= year <= today.year):
        return None, "生年月日の年が範囲外です"
    if blood not in ("A", "B", "O", "AB"):
        return None, "血液型が不正です"
    if navigator not in ("叢雲", "ノヴァ", "フレイヤ", "グレイス"):
        return None, "ニャビゲーターが不正です"
    return (year, month, day, blood, navigator, name), None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/checkout", methods=["POST"])
def checkout():
    if not stripe.api_key:
        return jsonify({"error": "Stripe APIキーが設定されていません。管理者にお問い合わせください。"}), 500

    data = request.get_json(force=True)
    fields, err = _validate_form(data)
    if err:
        return jsonify({"error": err}), 400
    year, month, day, blood, navigator, name = fields

    _cleanup_orders()
    order_id = str(uuid.uuid4())
    _pending_orders[order_id] = {
        "year": year, "month": month, "day": day,
        "blood": blood, "navigator": navigator, "name": name,
        "expires": datetime.utcnow() + timedelta(hours=1),
        "verified": False,
    }

    base_url = request.host_url.rstrip("/")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "jpy",
                    "product_data": {
                        "name": "星詠みChronicle 個人鑑定書",
                        "description": f"{name}様 ニャビゲーター：{navigator}",
                    },
                    "unit_amount": PRICE_JPY,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{base_url}/success?order_id={order_id}&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/cancel",
            locale="ja",
        )
    except stripe.error.StripeError as e:
        app.logger.exception("Stripe session creation failed")
        return jsonify({"error": f"決済エラー: {str(e.user_message or e)}"}), 500

    return jsonify({"checkout_url": session.url})


@app.route("/success")
def success():
    order_id   = request.args.get("order_id", "")
    session_id = request.args.get("session_id", "")
    return render_template("success.html", order_id=order_id, session_id=session_id)


@app.route("/download")
def download():
    order_id   = request.args.get("order_id", "")
    session_id = request.args.get("session_id", "")

    order = _pending_orders.get(order_id)
    if not order:
        return render_template("cancel.html", message="注文が見つかりません。URLをご確認ください。"), 404

    if datetime.utcnow() > order["expires"]:
        del _pending_orders[order_id]
        return render_template("cancel.html", message="ダウンロードリンクの有効期限が切れました（1時間）。"), 410

    if not order.get("verified"):
        if not stripe.api_key:
            return render_template("cancel.html", message="決済確認ができませんでした。"), 500
        try:
            stripe_session = stripe.checkout.Session.retrieve(session_id)
            if stripe_session.payment_status != "paid":
                return render_template("cancel.html", message="お支払いが確認できませんでした。"), 402
            order["verified"] = True
        except stripe.error.StripeError:
            app.logger.exception("Stripe verification failed")
            return render_template("cancel.html", message="決済確認中にエラーが発生しました。"), 500

    try:
        fortune_data = calculate_all(
            order["year"], order["month"], order["day"],
            order["blood"], order["navigator"], order["name"],
        )
        pdf_bytes = generate_pdf(fortune_data)
    except Exception:
        app.logger.exception("PDF generation failed")
        return render_template("cancel.html", message="PDF生成中にエラーが発生しました。"), 500

    filename = f"hoshiyomi_{order['name']}_{fortune_data['type']['name']}.pdf"
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/cancel")
def cancel():
    return render_template("cancel.html", message=None)


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    fields, err = _validate_form(data)
    if err:
        return jsonify({"error": err}), 400
    year, month, day, blood, navigator, name = fields

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
