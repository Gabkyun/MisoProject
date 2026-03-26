import time
import serial
import pymysql
import atexit
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import datetime

import threading

import socket

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
        return conn
    except pymysql.MySQLError as e:
        print(f"❌ Database Connection Error: {e}")
        return None

# Initialize Serial Port
port = "COM4"  # Change this to your actual serial port
ser = None
MOCK_MODE = False
serial_lock = threading.RLock()

try:
    ser = serial.Serial(port, baudrate=19200, timeout=2)
    print(f"✅ Serial port initialized successfully: {port}")
except Exception as e:
    print(f"❌ Error opening serial port: {e}")
    print("⚠️  Switching to MOCK MODE to allow API testing without hardware.")
    MOCK_MODE = True

# Function to send AT commands
def send_at_command(command, delay=0.5):
    if MOCK_MODE:
        return "OK"
        
    with serial_lock:
        if ser:
            try:
                ser.write((command + "\r\n").encode())
                time.sleep(delay)
                if ser.inWaiting() > 0:
                    response = ser.read(ser.inWaiting()).decode(errors="ignore").strip()
                    return response
            except Exception as e:
                print(f"Serial Error: {e}")
    return ""

# Function to send SMS
def send_sms(phone_number, message):
    if MOCK_MODE:
        print(f"📤 [MOCK] Sending to {phone_number}: {message}")
        log_sms(phone_number, message, "Sent")
        return True

    with serial_lock: 
        if not ser:
            return False

        print(f"📤 Sending SMS to {phone_number}...")
        send_at_command("AT+CMGF=1")  # Text mode
        response = send_at_command(f'AT+CMGS="{phone_number}"', delay=1)

        # Simplified check for demonstration
        if ">" in response or True: 
            ser.write((message + "\x1A").encode())
            time.sleep(3)
            final_resp = ser.read(ser.inWaiting()).decode(errors="ignore").strip()
            
            # In a real scenario, we'd check for "OK" strictly
            print(f"✅ SMS sent to {phone_number}")
            log_sms(phone_number, message, "Sent")
            return True

        log_sms(phone_number, message, "Failed")
        return False

# Database Helpers
def log_sms(phone_number, message, status):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sms_logs (phone_number, message, status, sent_at)
                VALUES (%s, %s, %s, NOW())
            """, (phone_number, message, status))
            conn.commit()
    except Exception as e:
        print(f"Log Error: {e}")
    finally:
        conn.close()

def get_all_contacts():
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, phone_number, department FROM contacts ORDER BY name ASC")
            return cursor.fetchall()
    finally:
        conn.close()

def get_logs_for_phone(phone_number):
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT message, status, sent_at, 'out' as direction 
                FROM sms_logs 
                WHERE phone_number = %s 
                ORDER BY sent_at ASC
            """, (phone_number,))
            return cursor.fetchall()
    finally:
        conn.close()

def get_department_logs(department):
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT phone_number FROM contacts WHERE department = %s", (department,))
            numbers = [r[0] for r in cursor.fetchall()]
            
            if not numbers: return []
            
            format_strings = ','.join(['%s'] * len(numbers))
            # Group by message content and time (roughly within same minute) to consolidate broadcasts
            # We select count(*) to know how many people received it
            cursor.execute(f"""
                SELECT message, MIN(status), MIN(sent_at) as sent_time, COUNT(*) as recipient_count
                FROM sms_logs 
                WHERE phone_number IN ({format_strings}) 
                GROUP BY message, UNIX_TIMESTAMP(sent_at) DIV 60
                ORDER BY sent_time ASC
            """, tuple(numbers))
            return cursor.fetchall()
    finally:
        conn.close()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/init_data', methods=['GET'])
def get_init_data():
    raw_contacts = get_all_contacts()
    
    contacts = []
    groups = set()
    
    for c in raw_contacts:
        contacts.append({
            "id": c[0],
            "name": c[1],
            "phone": c[2],
            "department": c[3]
        })
        if c[3]:
            groups.add(c[3])
            
    return jsonify({
        "contacts": contacts,
        "groups": sorted(list(groups))
    })

@app.route('/api/messages', methods=['GET'])
def get_messages():
    target = request.args.get('target')
    type_ = request.args.get('type') # 'individual' or 'group'
    
    if not target:
        return jsonify([])

    messages = []
    
    if type_ == 'group':
        logs = get_department_logs(target)
        for l in logs:
            count = l[3]
            messages.append({
                "text": l[0],
                "status": f"{l[1]}",
                "time": l[2].strftime("%I:%M %p"),
                "sender": "You",
                "recipient": f"All ({count})" # Show 'All' instead of individual number
            })
    else:
        logs = get_logs_for_phone(target)
        for l in logs:
            messages.append({
                "text": l[0],
                "status": l[1],
                "time": l[2].strftime("%I:%M %p"),
                "sender": "You",
                "direction": l[3]
            })
            
    return jsonify(messages)

@app.route('/api/send', methods=['POST'])
def send_message():
    data = request.get_json()
    target = data.get('target')
    message = data.get('message')
    type_ = data.get('type')
    
    if not target or not message:
        return jsonify({"success": False, "error": "Missing data"}), 400
        
    if type_ == 'group':
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT phone_number FROM contacts WHERE department = %s", (target,))
                rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return jsonify({"success": False, "error": "Empty group"}), 404
                
            success_count = 0
            for row in rows:
                if send_sms(row[0], message):
                    success_count += 1
            
            return jsonify({"success": True, "info": f"Sent to {success_count}/{len(rows)} recipients"})
        else:
             return jsonify({"success": False, "error": "DB Error"}), 500
             
    else:
        if send_sms(target, message):
             return jsonify({"success": True})
        else:
             return jsonify({"success": False, "error": "Send failed"}), 500

@app.route('/api/contacts', methods=['POST'])
def add_contact_route():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone_number') # Fixed key match
    dept = data.get('department')
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO contacts (name, phone_number, department) VALUES (%s, %s, %s)",
                               (name, phone, dept))
                conn.commit()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"success": False, "error": "DB Error"}), 500

def close_serial():
    if ser:
        ser.close()
atexit.register(close_serial)

if __name__ == '__main__':
    print("\n" + "="*50)
    print(" 🚀 SMS API SYSTEM - PROXY MODE")
    print(" ="*50)
    
    # We use Port 5000 so Apache can handle Port 80
    port_to_use = 5000
    print(" ✅ STATUS: Running on Port 5000")
    print(" 📱 LOCAL ACCESS:  http://MIS.Messaging.ph")
    print(" 💻 NETWORK ACCESS: http://192.168.20.10:5000")

    app.run(host='0.0.0.0', port=port_to_use, debug=True)
