import jwt
from flask import request, jsonify, g
from generated_api import get_user
from generated_api import get_posts

def register_routes(app):
    # JWT Authentication Context Decoder
    @app.before_request
    def decode_token():
        auth_header = request.headers.get("Authorization")
        g.user = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, "pyreact_secret_key", algorithms=["HS256"])
                g.user = payload.get("user")
            except Exception:
                pass

    # Built-in Auth endpoints
    @app.route("/api/login", methods=["POST"])
    def default_login():
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")
        import generated_api
        if hasattr(generated_api, "login_user"):
            user_data = generated_api.login_user(username, password)
            if user_data:
                token = jwt.encode({"user": user_data}, "pyreact_secret_key", algorithm="HS256")
                return jsonify({"status": "ok", "token": token, "user": user_data})
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        if username and password:
            user_data = {"username": username, "role": "admin"}
            token = jwt.encode({"user": user_data}, "pyreact_secret_key", algorithm="HS256")
            return jsonify({"status": "ok", "token": token, "user": user_data})
        return jsonify({"status": "error", "message": "Username and password required"}), 400

    @app.route("/api/me", methods=["GET", "POST"])
    def get_me():
        if g.user:
            return jsonify({"status": "ok", "user": g.user})
        return jsonify({"status": "error", "message": "Not authenticated"}), 401

    @app.route("/api/studio/save", methods=["POST"])
    def studio_save():
        data = request.get_json(silent=True) or {}
        code = data.get("code")
        if code:
            with open("app.pyreact", "w", encoding="utf-8") as f:
                f.write(code)
            import subprocess
            subprocess.run(["python", "-m", "pyreact.cli", "compile", "app.pyreact"], check=False)
            return jsonify({"status": "ok", "message": "Saved and compiled successfully"})
        return jsonify({"status": "error", "message": "No code provided"}), 400

    @app.route("/api/get_user", methods=["POST"])
    def _get_user():
        try:
            if request.is_json:
                payload = request.get_json(silent=True) or {}
            else:
                payload = dict(request.form)
                for k, v in request.files.items():
                    payload[k] = v
            user_id = payload.get("user_id")
            result = get_user(user_id)
            return jsonify({"status": "ok", "result": result})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/get_posts", methods=["POST"])
    def _get_posts():
        try:
            if request.is_json:
                payload = request.get_json(silent=True) or {}
            else:
                payload = dict(request.form)
                for k, v in request.files.items():
                    payload[k] = v
            result = get_posts()
            return jsonify({"status": "ok", "result": result})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return app