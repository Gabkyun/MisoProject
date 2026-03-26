# 🌐 SMS System Network Guide

You can now access your SMS System from any device (Phone, Tablet, or other PC) on your network without using a port number.

## 1. Primary Setup (Run as Administrator)
To enable Port 80 and open the Firewall, you **MUST** run your command prompt as Administrator.

1.  **Run Domain Script:** Right-click `setup_local_domain.ps1` and select **"Run with PowerShell"** (as Administrator).
2.  **Start API:** Open PowerShell as Administrator and run:
    ```powershell
    python MISOPROJ\MISOPROJ.py
    ```

---

## 2. How to Access

### 📱 From This Computer
- **URL:** [http://MIS.Messaging.ph](http://MIS.Messaging.ph)

### 💻 From Other Devices (Phones/Tablets/Other PCs)
Use the Local IP address of this computer:
- **URL:** [http://192.168.20.10](http://192.168.20.10)

---

## 3. Advanced: Using the Name on Other Devices
If you want other PCs on the network to use `http://MIS.Messaging.ph` (instead of the IP), you must edit the `C:\Windows\System32\drivers\etc\hosts` file on **THOSE** specific PCs and add this line:
```text
192.168.20.10    MIS.Messaging.ph
```

---

## 🔌 API Endpoints for Websites
Your websites can now send POST requests to:
`http://192.168.20.10/api/send`
