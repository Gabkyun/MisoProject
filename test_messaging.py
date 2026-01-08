import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_add_contact():
    log("Testing: Add Contact...")
    payload = {
        "name": "Test User",
        "phone_number": "09990001111",
        "department": "IT"
    }
    try:
        res = requests.post(f"{BASE_URL}/api/contacts", json=payload)
        if res.status_code == 200 or res.status_code == 201:
            log("Add Contact: SUCCESS", "PASS")
            return True
        else:
            log(f"Add Contact Failed: {res.text}", "FAIL")
            return False
    except Exception as e:
        log(f"Add Contact Exception: {e}", "FAIL")
        return False

def test_send_individual():
    log("Testing: Send Individual SMS...")
    payload = {
        "target": "09990001111",
        "message": "Hello Test User from Automated Test",
        "type": "individual"
    }
    try:
        res = requests.post(f"{BASE_URL}/api/send", json=payload)
        if res.status_code == 200:
            log("Send Individual: SUCCESS", "PASS")
            return True
        else:
            log(f"Send Individual Failed: {res.text}", "FAIL")
            return False
    except Exception as e:
        log(f"Send Individual Exception: {e}", "FAIL")
        return False

def test_check_messages(target):
    log(f"Testing: Check Messages for {target}...")
    try:
        res = requests.get(f"{BASE_URL}/api/messages?target={target}&type=individual")
        if res.status_code == 200:
            messages = res.json()
            if len(messages) > 0:
                last_msg = messages[-1]
                log(f"Check Messages: Found {len(messages)} messages. Last: '{last_msg['text']}'", "PASS")
                return True
            else:
                log("Check Messages: No messages found.", "FAIL")
                return False
        else:
            log(f"Check Messages Failed: {res.text}", "FAIL")
            return False
    except Exception as e:
        log(f"Check Messages Exception: {e}", "FAIL")
        return False

def test_send_group():
    log("Testing: Send Group Broadcast (IT)...")
    payload = {
        "target": "IT",
        "message": "Department Announcement Test",
        "type": "group"
    }
    try:
        res = requests.post(f"{BASE_URL}/api/send", json=payload)
        if res.status_code == 200:
            info = res.json().get("info", "")
            log(f"Send Group: SUCCESS ({info})", "PASS")
            return True
        else:
            log(f"Send Group Failed: {res.text}", "FAIL")
            return False
    except Exception as e:
        log(f"Send Group Exception: {e}", "FAIL")
        return False

def run_tests():
    print("=== STARTING MESSAGING SYSTEM TEST ===\n")
    
    # 1. Add Contact
    if not test_add_contact(): return

    # 2. Send Direct Message
    if not test_send_individual(): return
    
    # Wait for processing (Mock mode is instant but good practice)
    time.sleep(1)

    # 3. Verify Message Logged
    if not test_check_messages("09990001111"): return
    
    # 4. Send Group Message
    if not test_send_group(): return

    # 5. Verify Group Message on User (Since Test User is in IT)
    time.sleep(1)
    print("\nVerifying Group Message delivered to member...")
    test_check_messages("09990001111")
    
    print("\n=== ALL TESTS COMPLETED ===")

if __name__ == "__main__":
    run_tests()
