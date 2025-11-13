# 🛡️ Asset Sentinel

**Enterprise-Grade Asset Management and Vulnerability Monitoring System**

Asset Sentinel is a full-stack application that provides comprehensive asset tracking, automated vulnerability scanning, and real-time security monitoring with role-based access control.

---

## ✨ Key Features

### 🔐 Authentication & Authorization (100%)
- **JWT Authentication System**: Secure login, logout, and token refresh with session management
- **User Management APIs**: Complete CRUD operations with role assignment and password management
- **Role-Based Access Control (RBAC)**: Three permission levels (Admin, User, Viewer)
- **Modern Login UI**: Gradient design with secure session management
- **User Management Interface**: Full admin panel for user operations
- **Session Security**: Auto-redirect on 401, token refresh flow, secure token storage

### 📦 Asset Management (100%)
- **Full CRUD Operations**: Create, read, update, delete assets via UI and API
- **Enhanced Asset Tracking**: 
  - Tags and categorization
  - Criticality ratings (Low, Medium, High, Critical)
  - Hostname, IP address, OS, firmware version tracking
- **Bulk CSV Import**: Import multiple assets with validation and detailed error reporting
- **Active Directory Import**: Mock AD importer with 5 sample devices (LDAP hooks ready for production)
- **Real-Time Dashboard**: Live statistics and asset management tables

### 🔍 Vulnerability Monitoring (100%)
- **Multi-Source Scanning**:
  - NVD (National Vulnerability Database)
  - CISA KEV (Known Exploited Vulnerabilities)
  - OSV (Open Source Vulnerabilities)
  - Vulners Database
  - Vendor Advisory Feeds
- **Automated Background Scans**: Configurable interval (default: every 2 minutes)
- **CVSS Scoring**: Precise risk assessment with base scores (0.0-10.0)
- **Alert Prioritization**: Calculated from CVSS + exploitability + asset criticality
- **Full Provenance Tracking**: Source feed, matched CPE, confidence level, patch links
- **Webhook Notifications**: Instant alerts for CRITICAL/HIGH severity vulnerabilities
- **Bulk Alert Actions**: Mark multiple alerts as resolved simultaneously
- **Settings UI**: Configure vulnerability sources, scan interval, and API keys

### 📊 Reporting & Analytics (100%)
- **PDF Reports**: Professional executive summaries with top 10 critical vulnerabilities
- **CSV Export**: Bulk data export for analysis and compliance
- **Dashboard Statistics**: Real-time metrics (total assets, alerts, critical alerts)
- **Alert Filtering**: Filter by status (open/resolved) and severity
- **Weekly Reports**: Automated vulnerability reports

---

## 🚀 Quick Start - ONE COMMAND!

### Run Everything with a Single Command

```bash
./start.sh
```

That's it! This will:
- ✅ Install Python dependencies automatically
- ✅ Start the backend API server
- ✅ Serve the frontend UI
- ✅ Initialize the database with default admin user

**Then open your browser to:** http://localhost:5000

**Login with:**
- Username: `admin`
- Password: `admin123`

### Alternative: Manual Start

If you prefer to start manually:

```bash
cd backend
pip install -r requirements.txt
python3 app_integrated.py
```

Then open http://localhost:5000 in your browser.

> 📘 **See [QUICKSTART.md](QUICKSTART.md) for troubleshooting and detailed instructions**

### What You Get

- **Frontend**: http://localhost:5000 (Login page, Dashboard, Asset Management, etc.)
- **Backend API**: http://localhost:5000/api (RESTful endpoints)
- **Default Admin**: Pre-configured admin account for immediate use

---

## 📁 Architecture Overview

```
thesis1/
├── backend/
│   ├── app.py              # Flask application entry point
│   ├── models.py           # Database models (User, Asset, Alert, Setting)
│   ├── scanner.py          # Vulnerability scanning engine
│   ├── routes/
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── users.py        # User management endpoints
│   │   ├── assets.py       # Asset management endpoints
│   │   ├── alerts.py       # Alert management endpoints
│   │   ├── reports.py      # Report generation endpoints
│   │   └── settings.py     # Settings endpoints
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment configuration template
├── frontend/
│   ├── index.html          # Login page
│   ├── dashboard.html      # Main dashboard
│   ├── dashboard.js        # Dashboard logic
│   ├── assets.html         # Asset management UI
│   ├── users.html          # User management UI
│   └── settings.html       # Settings UI
└── README.md               # This file
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:5000/api
```

### Authentication Flow

#### 1. Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "refresh_token": "eyJ0eXAiOiJKV1Q...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@assetsentinel.com",
    "role": "admin"
  }
}
```

#### 2. Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer {refresh_token}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1Q..."
}
```

#### 3. Get Current User
```http
GET /api/auth/me
Authorization: Bearer {access_token}
```

#### 4. Logout
```http
POST /api/auth/logout
Authorization: Bearer {access_token}
```

### User Management (Admin Only)

#### List Users
```http
GET /api/users
Authorization: Bearer {access_token}
```

#### Create User
```http
POST /api/users
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "securepass",
  "role": "user"
}
```

#### Update User
```http
PUT /api/users/{id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "role": "admin"
}
```

#### Delete User
```http
DELETE /api/users/{id}
Authorization: Bearer {access_token}
```

### Asset Management

#### List Assets
```http
GET /api/assets
Authorization: Bearer {access_token}
```

#### Create Asset
```http
POST /api/assets
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "WEB-SERVER-01",
  "hostname": "web01.company.com",
  "ip_address": "192.168.1.10",
  "asset_type": "Server",
  "os": "Ubuntu 22.04",
  "firmware_version": "1.0.0",
  "criticality": "high",
  "tags": ["production", "web"],
  "description": "Main web server"
}
```

#### Update Asset
```http
PUT /api/assets/{id}
Authorization: Bearer {access_token}
Content-Type: application/json
```

#### Delete Asset
```http
DELETE /api/assets/{id}
Authorization: Bearer {access_token}
```

#### Import from CSV
```http
POST /api/assets/import/csv
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: assets.csv
```

#### Import from Active Directory
```http
POST /api/assets/import/ad
Authorization: Bearer {access_token}
```

### Alert Management

#### List Alerts
```http
GET /api/alerts?status=open&severity=critical
Authorization: Bearer {access_token}
```

#### Get Alert Statistics
```http
GET /api/alerts/statistics
Authorization: Bearer {access_token}
```

#### Resolve Alert
```http
POST /api/alerts/{id}/resolve
Authorization: Bearer {access_token}
```

#### Bulk Resolve Alerts
```http
POST /api/alerts/bulk-resolve
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "alert_ids": [1, 2, 3, 4]
}
```

### Reports

#### Generate PDF Report
```http
GET /api/reports/pdf
Authorization: Bearer {access_token}
```

#### Export Alerts to CSV
```http
GET /api/reports/csv
Authorization: Bearer {access_token}
```

### Settings (Admin Only)

#### List Settings
```http
GET /api/settings
Authorization: Bearer {access_token}
```

#### Update Setting
```http
PUT /api/settings/{key}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "value": "5"
}
```

---

## 👥 Role Permission Matrix

| Feature | Viewer | User | Admin |
|---------|--------|------|-------|
| View Assets | ✅ | ✅ | ✅ |
| Create/Edit Assets | ❌ | ✅ | ✅ |
| Delete Assets | ❌ | ❌ | ✅ |
| View Alerts | ✅ | ✅ | ✅ |
| Resolve Alerts | ❌ | ✅ | ✅ |
| View Users | Self Only | Self Only | ✅ |
| Manage Users | ❌ | ❌ | ✅ |
| Configure Settings | ❌ | ❌ | ✅ |
| Generate Reports | ✅ | ✅ | ✅ |

---

## ⚙️ Configuration

### Environment Variables

Edit `.env` file in the backend directory:

```env
# Security Keys (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///asset_sentinel.db

# Vulnerability Scanning
SCAN_INTERVAL_MINUTES=2

# API Keys (Optional)
NVD_API_KEY=

# Webhook (Optional)
WEBHOOK_URL=
```

### Application Settings

Configure via UI (`Settings` page) or API:

- **Scan Interval**: How often to scan for vulnerabilities (minutes)
- **NVD Enabled**: Enable/disable National Vulnerability Database scanning
- **CISA Enabled**: Enable/disable CISA KEV scanning
- **OSV Enabled**: Enable/disable Open Source Vulnerabilities scanning
- **Vulners Enabled**: Enable/disable Vulners database scanning
- **NVD API Key**: Optional - increases rate limits
- **Webhook URL**: Receive instant notifications for critical/high alerts

---

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure, stateless authentication
- **Password Hashing**: bcrypt with salt
- **Token Expiration**: Access tokens expire after 1 hour
- **Refresh Tokens**: Long-lived tokens for seamless re-authentication
- **Role-Based Access Control**: Granular permissions by role

### API Security
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CORS Configuration**: Cross-Origin Resource Sharing controls
- **Input Validation**: All inputs validated and sanitized
- **Error Handling**: Secure error messages (no sensitive data exposure)

### Data Protection
- **Secure Session Management**: Tokens stored in localStorage with auto-expiration
- **Auto-Redirect on 401**: Automatic logout on token expiration
- **Database Security**: Prepared statements, no raw SQL queries

---

## 🎯 Alert Prioritization Logic

Priority Score = (CVSS Score × 50%) + (Exploitability × 30%) + (Asset Criticality × 20%)

### CVSS Weight (50%)
- CVSS score normalized to 0-50 scale
- Directly from vulnerability database

### Exploitability Weight (30%)
- **High**: 30 points - Known exploit code available
- **Medium**: 20 points - Proof of concept available
- **Low**: 10 points - Theoretical vulnerability

### Asset Criticality Weight (20%)
- **Critical**: 20 points - Core infrastructure
- **High**: 15 points - Important services
- **Medium**: 10 points - Standard assets
- **Low**: 5 points - Non-critical assets

**Example**: CVE with CVSS 9.0 + High exploitability + Critical asset = (45 + 30 + 20) = **95/100 priority**

---

## 🚀 Production Deployment

### Using Gunicorn (Recommended)

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Nginx (Reverse Proxy)

1. **Install Nginx**
```bash
sudo apt install nginx
```

2. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/thesis1/frontend;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Enable HTTPS with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Database Migration to PostgreSQL

For production, consider PostgreSQL:

```bash
pip install psycopg2-binary
```

Update `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost/asset_sentinel
```

---

## 📝 Vulnerability Data Sources

### NVD (National Vulnerability Database)
- **URL**: https://nvd.nist.gov/
- **API**: https://services.nvd.nist.gov/rest/json/cves/2.0
- **Data**: CVE entries with CVSS scores, descriptions, and remediation

### CISA KEV (Known Exploited Vulnerabilities)
- **URL**: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- **Focus**: Actively exploited vulnerabilities in the wild
- **Priority**: High-priority vulnerabilities requiring immediate action

### OSV (Open Source Vulnerabilities)
- **URL**: https://osv.dev/
- **Focus**: Open source software vulnerabilities
- **Coverage**: npm, PyPI, Go, Maven, etc.

### Vulners
- **URL**: https://vulners.com/
- **Data**: Aggregated vulnerability intelligence
- **Coverage**: Multiple sources and vendors

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Bikash Parajuli**
- GitHub: [@parajulibks](https://github.com/parajulibks)

---

## 🙏 Acknowledgments

- NIST for the National Vulnerability Database
- CISA for the Known Exploited Vulnerabilities Catalog
- OSV for the Open Source Vulnerabilities database
- The open-source community for various tools and libraries

---

## 📞 Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

**Built with ❤️ for Thesis Project**
