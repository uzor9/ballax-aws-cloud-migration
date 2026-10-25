from flask import Flask, jsonify, request
from datetime import datetime, timezone
import os
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "ballax_db"),
        cursorclass=DictCursor,
        connect_timeout=5,
        ssl_ca=os.environ["DB_SSL_CA"]
    )


@app.route("/")
def home():
    return jsonify({
        "company": "Ballax Technologies",
        "application": "Customer Management API",
        "status": "running"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/customers", methods=["GET"])
def get_customers():
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, email, status FROM customers ORDER BY id"
            )
            customers = cursor.fetchall()

        return jsonify({
            "total": len(customers),
            "customers": customers
        })
    finally:
        connection.close()


@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, email, status "
                "FROM customers WHERE id = %s",
                (customer_id,)
            )
            customer = cursor.fetchone()

        if customer is None:
            return jsonify({"error": "Customer not found"}), 404

        return jsonify(customer)
    finally:
        connection.close()


@app.route("/customers", methods=["POST"])
def add_customer():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    name = data.get("name")
    email = data.get("email")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Valid name is required"}), 400

    if not isinstance(email, str) or not email.strip():
        return jsonify({"error": "Valid email is required"}), 400

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO customers (name, email, status) "
                "VALUES (%s, %s, %s)",
                (name.strip(), email.strip(), "active")
            )

            new_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "id": new_id,
            "name": name.strip(),
            "email": email.strip(),
            "status": "active"
        }), 201
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=False)
