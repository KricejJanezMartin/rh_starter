from flask import Flask, render_template
import mysql.connector
import os
import logging

app = Flask(__name__)
app.config['ENV'] = 'production'
print(app.config['ENV'])
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    try:
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
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=False)