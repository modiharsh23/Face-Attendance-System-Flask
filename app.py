from flask import Flask, render_template, request, Response
import sqlite3
import csv
from datetime import datetime
import io

app = Flask(__name__)

@app.route('/')
def index():
    # Render the index page with initial values
    return render_template('index.html', selected_date='', no_data=False)

@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')  # Parse the date string to a datetime object
    formatted_date = selected_date_obj.strftime('%B %d, %Y')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Query the attendance data for the selected date
    cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (selected_date,))
    attendance_data = cursor.fetchall()
    conn.close()

    # Format the time to 12-hour format with AM/PM
    attendance_data = [(name, datetime.strptime(time, '%H:%M:%S').strftime('%I:%M %p')) for name, time in attendance_data]

    if not attendance_data:
        return render_template('index.html', selected_date=formatted_date, no_data=True)

    return render_template('index.html', selected_date=formatted_date, attendance_data=attendance_data)

@app.route('/download_csv')
def download_csv():
    # Get the selected date from the query parameters
    selected_date = request.args.get('selected_date')
    selected_date_obj = datetime.strptime(selected_date, '%B %d, %Y')  # Parse the formatted date
    selected_date_str = selected_date_obj.strftime('%Y-%m-%d')  # Format the date as "YYYY-MM-DD"

    # Connect to the SQLite database
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Query the attendance data for the selected date
    cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (selected_date_str,))
    attendance_data = cursor.fetchall()

    conn.close()

    # Create an in-memory file-like object to hold the CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Time', 'Date'])  # Write the header row
    for row in attendance_data:
        writer.writerow([row[0], row[1], selected_date_str])  # Write data rows

    # Create a response with the CSV data
    response = Response(output.getvalue(), content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=attendance_data.csv"
    return response

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode