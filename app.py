from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return """
    <html>
    <head>
        <title>Steel Plate Fault Database</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
            }
            .container {
                width: 60%;
                margin: 120px auto;
                background: white;
                padding: 40px;
                border-radius: 6px;
            }
            a.button {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 18px;
                background: #2c7be5;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Steel Plate Fault Database</h1>
            <p>
                This web application provides access to a database of steel plate
                inspection records collected during an industrial quality control process.
            </p>
            <p>
                Users can browse steel plates by defect category and view detailed
                inspection measurements stored in the database.
            </p>
            <a class="button" href="/plates">View Plates</a>
        </div>
    </body>
    </html>
    """

@app.route("/plates")
def show_plates():
    page = request.args.get("page", default=1, type=int)
    fault = request.args.get("fault")

    if page < 1:
        page = 1

    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            pn.plate_id,
            f.fault_name,
            f.description
        FROM plates_new pn
        LEFT JOIN faults f
        ON pn.fault_code = f.fault_code
        ORDER BY pn.plate_id
        LIMIT ? OFFSET ?
        """,
        (per_page, offset)
    )

    rows = cursor.fetchall()
    cursor.execute("SELECT fault_code, fault_name FROM faults")
    faults = cursor.fetchall()

    conn.close()

    return render_template(
        "plates.html",
        rows=rows,
        faults=faults,
        selected_fault=fault,
        page=page
    )

@app.route("/plates/<int:plate_id>")
def plate_detail(plate_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            pn.plate_id,
            f.fault_name,
            f.description,
            m.thickness,
            m.width,
            m.surface_area
        FROM plates_new pn
        LEFT JOIN faults f
          ON pn.fault_code = f.fault_code
        LEFT JOIN plate_measurements m
          ON pn.plate_id = m.plate_id
        WHERE pn.plate_id = ?
        """,
        (plate_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return "Plate not found", 404

    return render_template(
        "plate_detail.html",
        plate=row
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
