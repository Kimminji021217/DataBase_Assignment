from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# --------------------
# DB Connection
# --------------------
def get_db_connection():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn


# --------------------
# Landing Page
# --------------------
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
                This web application demonstrates a database-driven inspection
                system for industrial steel plates.
            </p>
            <a class="button" href="/plates">View Plates</a>
        </div>
    </body>
    </html>
    """


# --------------------
# Plate List (fault filter)
# --------------------
@app.route("/plates")
def show_plates():
    page = request.args.get("page", default=1, type=int)
    selected_fault = request.args.get("fault", default="", type=str)

    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    # fault 목록
    cursor.execute("SELECT fault_code, fault_name FROM faults ORDER BY fault_code")
    faults = cursor.fetchall()

    # plates 목록
    if selected_fault:
        cursor.execute(
            """
            SELECT
                pn.plate_id,
                f.fault_name,
                f.description
            FROM plates_new pn
            JOIN faults f ON pn.fault_code = f.fault_code
            WHERE pn.fault_code = ?
            ORDER BY pn.plate_id
            LIMIT ? OFFSET ?
            """,
            (selected_fault, per_page, offset)
        )
    else:
        cursor.execute(
            """
            SELECT
                pn.plate_id,
                f.fault_name,
                f.description
            FROM plates_new pn
            JOIN faults f ON pn.fault_code = f.fault_code
            ORDER BY pn.plate_id
            LIMIT ? OFFSET ?
            """,
            (per_page, offset)
        )

    rows = cursor.fetchall()
    conn.close()

    return render_template(
        "plates.html",
        rows=rows,
        faults=faults,
        selected_fault=selected_fault,
        page=page
    )


# --------------------
# Plate Detail
# --------------------
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
        JOIN faults f ON pn.fault_code = f.fault_code
        JOIN plate_measurements m ON pn.plate_id = m.plate_id
        WHERE pn.plate_id = ?
        """,
        (plate_id,)
    )

    plate = cursor.fetchone()
    conn.close()

    if plate is None:
        return "Plate not found", 404

    return render_template("plate_detail.html", plate=plate)


# --------------------
# Range Filter (fault + measurement)
# --------------------
@app.route("/plates/filter")
def filter_plates():
    fault = request.args.get("fault")
    min_th = request.args.get("min_th", type=float)
    max_th = request.args.get("max_th", type=float)
    min_w = request.args.get("min_w", type=float)
    max_w = request.args.get("max_w", type=float)
    min_sa = request.args.get("min_sa", type=float)
    max_sa = request.args.get("max_sa", type=float)

    query = """
        SELECT
            pn.plate_id,
            f.fault_name,
            m.thickness,
            m.width,
            m.surface_area
        FROM plates_new pn
        JOIN faults f ON pn.fault_code = f.fault_code
        JOIN plate_measurements m ON pn.plate_id = m.plate_id
        WHERE 1=1
    """
    params = []

    if fault:
        query += " AND pn.fault_code = ?"
        params.append(fault)

    if min_th is not None:
        query += " AND m.thickness >= ?"
        params.append(min_th)

    if max_th is not None:
        query += " AND m.thickness <= ?"
        params.append(max_th)

    if min_w is not None:
        query += " AND m.width >= ?"
        params.append(min_w)

    if max_w is not None:
        query += " AND m.width <= ?"
        params.append(max_w)

    if min_sa is not None:
        query += " AND m.surface_area >= ?"
        params.append(min_sa)

    if max_sa is not None:
        query += " AND m.surface_area <= ?"
        params.append(max_sa)


    query += " ORDER BY pn.plate_id"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    fault_name = None
    if fault:
        conn2 = get_db_connection()
        cur2 = conn2.cursor()
        cur2.execute(
            "SELECT fault_name FROM faults WHERE fault_code = ?",
            (fault,)
        )
        row = cur2.fetchone()
        if row:
            fault_name = row["fault_name"]
        conn2.close()
    conn.close()

    return render_template(
        "plate_filter.html",
        rows=rows,
        fault_code=fault,
        fault_name=fault_name,
        min_th=min_th,
        max_th=max_th,
        min_w=min_w,
        max_w=max_w,
        min_sa=min_sa,
        max_sa=max_sa
    )

@app.route("/add", methods=["GET", "POST"])
def add_plate():
    conn = get_db_connection()
    cursor = conn.cursor()

    # fault 목록 (select box용)
    cursor.execute("SELECT fault_code, fault_name FROM faults")
    faults = cursor.fetchall()

    if request.method == "POST":
        fault_code = request.form["fault_code"]
        thickness = request.form["thickness"]
        width = request.form["width"]
        surface_area = request.form["surface_area"]

        try:
            # 🔹 트랜잭션 시작
            cursor.execute(
                "INSERT INTO plates_new (fault_code) VALUES (?)",
                (fault_code,)
            )

            plate_id = cursor.lastrowid  # 방금 생성된 plate_id

            cursor.execute(
                """
                INSERT INTO plate_measurements
                (plate_id, thickness, width, surface_area)
                VALUES (?, ?, ?, ?)
                """,
                (plate_id, thickness, width, surface_area)
            )

            conn.commit()

        except Exception as e:
            conn.rollback()
            conn.close()
            return f"Error occurred: {e}"

        conn.close()
        return redirect("/plates")

    conn.close()
    return render_template("add_plate.html", faults=faults)

@app.route("/edit/<int:plate_id>", methods=["GET", "POST"])
def edit_plate(plate_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # fault 목록
    cursor.execute("SELECT fault_code, fault_name FROM faults")
    faults = cursor.fetchall()

    if request.method == "POST":
        fault_code = request.form["fault_code"]
        thickness = request.form["thickness"]
        width = request.form["width"]
        surface_area = request.form["surface_area"]

        try:
            cursor.execute(
                "UPDATE plates_new SET fault_code = ? WHERE plate_id = ?",
                (fault_code, plate_id)
            )

            cursor.execute(
                """
                UPDATE plate_measurements
                SET thickness = ?, width = ?, surface_area = ?
                WHERE plate_id = ?
                """,
                (thickness, width, surface_area, plate_id)
            )

            conn.commit()

        except Exception as e:
            conn.rollback()
            conn.close()
            return f"Error occurred: {e}"

        conn.close()
        return redirect(f"/plates/{plate_id}")

    # GET 요청: 기존 데이터 불러오기
    cursor.execute(
        """
        SELECT
            pn.fault_code,
            m.thickness,
            m.width,
            m.surface_area
        FROM plates_new pn
        JOIN plate_measurements m
          ON pn.plate_id = m.plate_id
        WHERE pn.plate_id = ?
        """,
        (plate_id,)
    )

    plate = cursor.fetchone()
    conn.close()

    if plate is None:
        return "Plate not found", 404

    return render_template(
        "edit_plate.html",
        plate=plate,
        plate_id=plate_id,
        faults=faults
    )

@app.route("/delete/<int:plate_id>", methods=["POST"])
def delete_plate(plate_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 먼저 measurement 삭제 (FK 구조 고려)
        cursor.execute(
            "DELETE FROM plate_measurements WHERE plate_id = ?",
            (plate_id,)
        )

        # 그 다음 plate 삭제
        cursor.execute(
            "DELETE FROM plates_new WHERE plate_id = ?",
            (plate_id,)
        )

        conn.commit()

    except Exception as e:
        conn.rollback()
        conn.close()
        return f"Error occurred: {e}"

    conn.close()
    return redirect("/plates")


# --------------------
# Run
# --------------------
if __name__ == "__main__":
    app.run(debug=True)
