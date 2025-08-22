import logging
import os
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from .db import get_connection, ensure_schema

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    # Minimal secret for flash messages; override via env
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-not-secret")

    # Logging: request + errors to stdout
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    @app.before_request
    def _log_request():
        app.logger.info("%s %s", request.method, request.path)

    # Create schema at startup (idempotent)
    try:
        ensure_schema()
        app.logger.info("Schema ensured.")
    except Exception as e:
        app.logger.error("Schema check failed at startup: %s", e)

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            content = (request.form.get("content") or "").strip()
            if not content:
                flash("Note cannot be empty.", "error")
                return redirect(url_for("index"))
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
                conn.commit()
            finally:
                try:
                    cur.close()
                    conn.close()
                except Exception:
                    pass
            return redirect(url_for("index"))

        # GET -> list notes newest first
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        notes = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("index.html", notes=notes)

    @app.route("/notes", methods=["GET", "POST"])
    def notes_api():
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            content = (data.get("content") or "").strip()
            if not content:
                return jsonify({"error": "content required"}), 400
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
            note_id = cur.lastrowid
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"id": note_id, "content": content}), 201

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows), 200

    @app.route("/healthz", methods=["GET"])
    def healthz():
        try:
            # DB reachable AND schema applied
            ensure_schema()
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            app.logger.error("Health check failed: %s", e)
            return jsonify({"status": "error", "detail": str(e)}), 500

    return app
