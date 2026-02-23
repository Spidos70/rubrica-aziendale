from flask import Flask, render_template, request, jsonify, abort
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "rubrica.db")


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contatti (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT    NOT NULL,
                cognome     TEXT    NOT NULL,
                azienda     TEXT,
                reparto     TEXT,
                telefono    TEXT,
                cellulare   TEXT,
                email       TEXT,
                tariffa     REAL,
                valuta      TEXT    DEFAULT 'EUR',
                commenti    TEXT,
                creato_il   TEXT    DEFAULT (datetime('now','localtime')),
                modificato_il TEXT  DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()


# ---------------------------------------------------------------------------
# Routes — UI
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# API REST
# ---------------------------------------------------------------------------

@app.route("/api/contatti", methods=["GET"])
def lista_contatti():
    q = request.args.get("q", "").strip()
    with get_db() as conn:
        if q:
            like = f"%{q}%"
            rows = conn.execute("""
                SELECT * FROM contatti
                WHERE nome LIKE ? OR cognome LIKE ? OR azienda LIKE ?
                   OR reparto LIKE ? OR telefono LIKE ? OR cellulare LIKE ?
                   OR email LIKE ? OR commenti LIKE ?
                ORDER BY cognome, nome
            """, (like, like, like, like, like, like, like, like)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM contatti ORDER BY cognome, nome"
            ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/contatti/<int:id>", methods=["GET"])
def get_contatto(id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM contatti WHERE id=?", (id,)).fetchone()
    if row is None:
        abort(404)
    return jsonify(dict(row))


@app.route("/api/contatti", methods=["POST"])
def crea_contatto():
    data = request.get_json(force=True)
    required = ("nome", "cognome")
    for field in required:
        if not data.get(field, "").strip():
            return jsonify({"error": f"Campo obbligatorio: {field}"}), 400
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO contatti
                (nome, cognome, azienda, reparto, telefono, cellulare, email,
                 tariffa, valuta, commenti)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("nome", "").strip(),
            data.get("cognome", "").strip(),
            data.get("azienda", "").strip(),
            data.get("reparto", "").strip(),
            data.get("telefono", "").strip(),
            data.get("cellulare", "").strip(),
            data.get("email", "").strip(),
            data.get("tariffa") or None,
            data.get("valuta", "EUR").strip() or "EUR",
            data.get("commenti", "").strip(),
        ))
        conn.commit()
        new_id = cur.lastrowid
    with get_db() as conn:
        row = conn.execute("SELECT * FROM contatti WHERE id=?", (new_id,)).fetchone()
    return jsonify(dict(row)), 201


@app.route("/api/contatti/<int:id>", methods=["PUT"])
def aggiorna_contatto(id):
    data = request.get_json(force=True)
    required = ("nome", "cognome")
    for field in required:
        if not data.get(field, "").strip():
            return jsonify({"error": f"Campo obbligatorio: {field}"}), 400
    with get_db() as conn:
        exists = conn.execute("SELECT 1 FROM contatti WHERE id=?", (id,)).fetchone()
        if not exists:
            abort(404)
        conn.execute("""
            UPDATE contatti SET
                nome=?, cognome=?, azienda=?, reparto=?, telefono=?,
                cellulare=?, email=?, tariffa=?, valuta=?, commenti=?,
                modificato_il=datetime('now','localtime')
            WHERE id=?
        """, (
            data.get("nome", "").strip(),
            data.get("cognome", "").strip(),
            data.get("azienda", "").strip(),
            data.get("reparto", "").strip(),
            data.get("telefono", "").strip(),
            data.get("cellulare", "").strip(),
            data.get("email", "").strip(),
            data.get("tariffa") or None,
            data.get("valuta", "EUR").strip() or "EUR",
            data.get("commenti", "").strip(),
            id,
        ))
        conn.commit()
    with get_db() as conn:
        row = conn.execute("SELECT * FROM contatti WHERE id=?", (id,)).fetchone()
    return jsonify(dict(row))


@app.route("/api/contatti/<int:id>", methods=["DELETE"])
def elimina_contatto(id):
    with get_db() as conn:
        exists = conn.execute("SELECT 1 FROM contatti WHERE id=?", (id,)).fetchone()
        if not exists:
            abort(404)
        conn.execute("DELETE FROM contatti WHERE id=?", (id,))
        conn.commit()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    print("Rubrica avviata su http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
