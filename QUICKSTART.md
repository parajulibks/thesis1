# Asset Sentinel - Quick Start Guide

## Run Everything with ONE Command! 🚀

### Option 1: Using the Startup Script (Recommended)

```bash
./start.sh
```

That's it! This single command will:
- ✅ Check and install Python dependencies
- ✅ Start the backend API server
- ✅ Serve the frontend UI
- ✅ Initialize the database with default admin user

### Option 2: Manual Start

If you prefer to run it manually:

```bash
cd backend
pip3 install -r requirements.txt
python3 app_integrated.py
```

## Access the Application

Once the server starts, you'll see:

```
==================================================
Asset Sentinel is running!
==================================================

Frontend: http://localhost:5000
Backend API: http://localhost:5000/api

Login with:
  Username: admin
  Password: admin123
```

### Open Your Browser

1. Navigate to **http://localhost:5000**
2. You'll see the login page
3. Enter the default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
4. Click "Login"

## What's Included?

The integrated server provides:

- ✅ **Frontend UI** - All HTML pages served at http://localhost:5000
- ✅ **Backend API** - RESTful endpoints at http://localhost:5000/api
- ✅ **Database** - SQLite database auto-initialized
- ✅ **Default Admin** - Pre-created admin account

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, you can change it in `backend/app_integrated.py`:

```python
# Change the last line:
app.run(debug=True, host='0.0.0.0', port=5001)  # Use a different port
```

### Module Not Found Error

If you get a "Module not found" error:

```bash
cd backend
pip3 install -r requirements.txt
```

### Cannot Connect to Server

Make sure:
1. The backend is running (you should see "Asset Sentinel is running!" message)
2. You're accessing http://localhost:5000 (not http://localhost:8000)
3. No firewall is blocking port 5000

## Next Steps

After logging in, you can:

1. **Dashboard** - View real-time statistics
2. **Assets** - Manage your IT assets
3. **Users** - Create and manage users (Admin only)
4. **Settings** - Configure vulnerability scanning

## Features

- 🔐 JWT Authentication
- 👥 User Management with RBAC
- 📦 Asset Management
- 🔍 Vulnerability Monitoring
- 📊 Dashboard & Statistics
- 📄 PDF & CSV Reports

For detailed documentation, see [README.md](README.md)
