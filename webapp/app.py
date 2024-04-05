from flask import Flask, render_template
import mysql.connector
import os

app = Flask(__name__)

@app.route('/')
def home():
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM hourly_weather_data")
    data = cursor.fetchall()

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)