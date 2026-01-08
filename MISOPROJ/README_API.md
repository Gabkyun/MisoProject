# SMS System API Documentation

Your SMS system is now ready to be used as an API for external websites and applications.

Base URL: `http://MIS.Messaging.ph` (if Port 80 is successful) or `http://MIS.Messaging.ph:5000`

## 🌍 Domain Setup (One-Time)
To use `MIS.Messaging.ph` instead of an IP address:
1.  **On the Server (This PC):** 
    Run the included `setup_local_domain.ps1` script as Administrator.
2.  **On Other PCs/Servers:**
    You must update their `hosts` file to point `MIS.Messaging.ph` to this computer's LAN IP Address.
    *Example line to add:*  
    `192.168.1.X   MIS.Messaging.ph`

## Endpoints

### 1. Send SMS
**Endpoint:** `/api/send`  
**Method:** `POST`  
**Content-Type:** `application/json`

**Body:**
```json
{
  "target": "09123456789",
  "message": "Your OTP is 1234",
  "type": "individual"  // or "group" to send to a department name
}
```

**Response:**
```json
{
  "success": true
}
```

### 2. Get Messages
**Endpoint:** `/api/messages`  
**Method:** `GET`

**Query Parameters:**
- `target`: Phone number or Department name
- `type`: `individual` or `group` (optional, defaults to individual logic)

**Example:**
`/api/messages?target=09123456789`

### 3. Add Contact
**Endpoint:** `/api/contacts`  
**Method:** `POST`

**Body:**
```json
{
  "name": "John Doe",
  "phone_number": "09123456789",
  "department": "IT"
}
```

## Security Note

Currently, the API is open to anyone on your network. 
1. **Firewall**: Ensure only trusted IPs can access port 5000.
2. **API Key**: If you need more security, we can add an API Key requirement to the headers.
