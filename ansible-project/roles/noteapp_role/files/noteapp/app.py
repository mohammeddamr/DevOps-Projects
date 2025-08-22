from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="noteuser",
    password="yourpassword",
    database="notesdb"
)

cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        content TEXT NOT NULL
    )
""")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form["content"]
        cursor.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
        db.commit()
        return redirect("/")
    
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    return render_template("index.html", notes=notes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

