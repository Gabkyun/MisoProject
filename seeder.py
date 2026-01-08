import pymysql

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "sms_system",
    "port": 3306
}

SAMPLE_DATA = [
    ("Alice Smith", "09171234567", "IT"),
    ("Bob Jones", "09181234567", "HR"),
    ("Charlie Day", "09191234567", "Sales"),
    ("David Lee", "09201234567", "IT"),
    ("Eve White", "09211234567", "Marketing"),
    ("Frank Ocean", "09221234567", "Finance"),
    ("Grace Hopper", "09231234567", "IT")
]

def seed_database():
    conn = None
    try:
        # Connect initially without DB to clear creation
        conn = pymysql.connect(host=DB_CONFIG["host"], user=DB_CONFIG["user"], password=DB_CONFIG["password"], port=DB_CONFIG["port"])
        with conn.cursor() as cursor:
            print(f"🛠  Creating database '{DB_CONFIG['database']}' if not exists...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # 1. Check/Update Schema
            print("Checking schema...")
            # Create table if not exists. Note: original schema might not have had 'name'
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    phone_number VARCHAR(20),
                    department VARCHAR(50)
                )
            """)
            
            # Check for 'name' column existence
            cursor.execute("DESCRIBE contacts")
            columns = [row[0] for row in cursor.fetchall()]
            
            if "name" not in columns:
                print("⚠️ 'name' column missing. Adding it now...")
                cursor.execute("ALTER TABLE contacts ADD COLUMN name VARCHAR(255) AFTER id")
            
            # 2. Seed Data
            print("🌱 Seeding data...")
            # We'll truncate to ensure clean state for testing, or just insert. 
            # I will TRUNCATE to avoid duplicates on multiple runs.
            cursor.execute("TRUNCATE TABLE contacts")
            
            query = "INSERT INTO contacts (name, phone_number, department) VALUES (%s, %s, %s)"
            cursor.executemany(query, SAMPLE_DATA)
            conn.commit()
            print(f"✅ Successfully seeded {len(SAMPLE_DATA)} contacts.")
            
            # Verify
            cursor.execute("SELECT * FROM contacts")
            print("Current Contacts in DB:")
            for row in cursor.fetchall():
                print(row)

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_database()
