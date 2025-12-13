from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("app.db")
    return conn

@app.route("/")
def index():
    return "<h3>Database Assignment</h3><p><a href='/plates'>View Plates</a></p>"

@app.route("/plates")
def show_plates():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM plates LIMIT 50")
    rows = cursor.fetchall()

    column_names = [description[0] for description in cursor.description]

    conn.close()

    return render_template(
        "plates.html",
        rows=rows,
        columns=column_names
    )

if __name__ == "__main__":
    app.run(debug=True)
