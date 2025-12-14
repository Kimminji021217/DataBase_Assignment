from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return "<h3>Database Assignment</h3><p><a href='/plates'>View Plates</a></p>"

@app.route("/plates")
def show_plates():
    page = request.args.get("page", default=1, type=int)
    if page < 1:
        page = 1

    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            p.id,
            p.thickness,
            p.width,
            p.surface_area,
            f.fault_name,
            f.description
        FROM plates p
        LEFT JOIN faults f
          ON p.fault_type = f.fault_code
        ORDER BY p.id
        LIMIT ? OFFSET ?
        """,
        (per_page, offset)
    )

    rows = cursor.fetchall()
    conn.close()

    return render_template(
        "plates.html",
        rows=rows,
        page=page
    )

@app.route("/add", methods=["GET", "POST"])
def add_plate():
    if request.method == "POST":
        fault_type = request.form["fault_type"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO plates (fault_type) VALUES (?)",
            (fault_type,)
        )

        conn.commit()
        conn.close()

        return redirect("/plates")

    return render_template("add_plate.html")

@app.route("/delete/<int:plate_id>")
def delete_plate(plate_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM plates WHERE id = ?", (plate_id,))

    conn.commit()
    conn.close()

    return redirect("/plates")

@app.route("/edit/<int:plate_id>", methods=["GET", "POST"])
def edit_plate(plate_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        fault_type = request.form["fault_type"]

        cursor.execute(
            "UPDATE plates SET fault_type = ? WHERE id = ?",
            (fault_type, plate_id)
        )
        conn.commit()
        conn.close()
        return redirect("/plates")

    cursor.execute(
        "SELECT fault_type FROM plates WHERE id = ?",
        (plate_id,)
    )
    fault_type = cursor.fetchone()[0]
    conn.close()

    return render_template(
        "edit_plate.html",
        fault_type=fault_type
    )

if __name__ == "__main__":
    app.run(debug=True)
