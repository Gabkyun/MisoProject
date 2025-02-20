import time
import serial
import pymysql
import atexit
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={r"/*": {"origins": "*"}})

# MySQL Database Configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",  # Change if your MySQL has a password
    "database": "sms_system",
    "port": 3306
}

def get_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ Database connection successful.")
        return conn
    except pymysql.MySQLError as e:
        print(f"❌ Database Connection Error: {e}")
        return None

# Initialize Serial Port
port = "COM4"  # Change this to your actual serial port
ser = None
try:
    ser = serial.Serial(port, baudrate=19200, timeout=2)
    print(f"✅ Serial port initialized successfully: {port}")
except Exception as e:
    print(f"❌ Error opening serial port: {e}")

# Function to send AT commands to SIM800C
def send_at_command(command, delay=5):
    if ser:
        ser.write((command + "\r\n").encode())
        time.sleep(delay)
        response = ser.read(ser.inWaiting()).decode(errors="ignore").strip()
        print(f"📡 Sent: {command}\n📨 Response: {response}\n")
        return response
    return "SIM800C modem not connected."

# Function to send SMS
def send_sms(phone_number, message):
    if not ser:
        print("❌ Serial connection not initialized.")
        return False

    print(f"📤 Sending SMS to {phone_number}...")
    
    send_at_command("AT+CMGF=1")  # Set text mode
    response = send_at_command(f'AT+CMGS="{phone_number}"')

    if ">" in response:
        ser.write((message + "\x1A").encode())  # Send message with Ctrl+Z
        time.sleep(5)
        final_response = ser.read(ser.inWaiting()).decode(errors="ignore").strip()

        if "OK" in final_response:
            print(f"✅ SMS sent successfully to {phone_number}")
            return True

    print(f"❌ SMS failed for {phone_number}")
    return False

# Function to log SMS into MySQL
def log_sms(phone_number, message, status):
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sms_logs (phone_number, message, status, sent_at)
                VALUES (%s, %s, %s, NOW())
            """, (phone_number, message, status))
            conn.commit()
        print(f"📝 Logged SMS to {phone_number}: {status}")
    except pymysql.MySQLError as e:
        print(f"❌ Database Error (Logging SMS): {e}")
    finally:
        conn.close()

# Function to fetch phone numbers by department
def get_contacts_by_department(department_name):
    conn = get_db_connection()
    if not conn:
        print("❌ ERROR: Database connection failed.")
        return []

    try:
        with conn.cursor() as cursor:
            print(f"🔍 Checking database for department: {department_name}")
            query = "SELECT phone_number FROM contacts WHERE department = %s"
            cursor.execute(query, (department_name,))
            results = cursor.fetchall()
            phone_numbers = [row[0] for row in results]
        
        if phone_numbers:
            print(f"✅ SUCCESS: Phone numbers found: {phone_numbers}")
        else:
            print(f"⚠️ WARNING: No contacts found for department '{department_name}'")
        
        return phone_numbers
    except pymysql.MySQLError as e:
        print(f"❌ ERROR: Database fetch failed - {e}")
        return []
    finally:
        conn.close()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# API to send SMS to a single contact
@app.route('/send-sms', methods=['POST'])
def send_sms_to_contact():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        message = data.get('message', '')

        if not phone_number or not message:
            return jsonify({"success": False, "error": "Phone number and message are required"}), 400

        if send_sms(phone_number, message):
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "error": "Failed to send SMS"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# API to send SMS to a group
@app.route('/send-sms-group', methods=['POST'])
def send_sms_to_group():
    try:
        data = request.get_json()
        department = data.get('department')
        message = data.get('message', '')

        if not department or not message:
            return jsonify({"success": False, "error": "Department and message are required"}), 400

        phone_numbers = get_contacts_by_department(department)

        if not phone_numbers:
            return jsonify({"success": False, "error": "No contacts found for this department"}), 404

        failed_numbers = []
        for number in phone_numbers:
            if not send_sms(number, message):
                failed_numbers.append(number)

        if failed_numbers:
            return jsonify({"success": False, "error": "Failed to send SMS to some numbers", "failed_numbers": failed_numbers}), 500

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Close Serial Port on Exit
def close_serial():
    if ser:
        ser.close()
        print("✅ Serial port closed.")

atexit.register(close_serial)

# Run Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
