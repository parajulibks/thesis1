# Changelog

## [Latest] - 2025-11-13

### Added
- **NVD API Integration**: Real-time vulnerability search using official NVD API v2.0
  - Search by product name and optional version
  - Returns CVE details, CVSS scores, severity, and publication dates
  - Direct links to NVD vulnerability details
  
- **Vulnerabilities Page**: New dedicated page for vulnerability management
  - Manual scan button for on-demand asset scanning
  - Product-based CVE search interface
  - Real-time scan status feedback
  - Beautiful card-based results display with severity badges
  
- **Manual Scanning**: One-click scanning of all assets
  - Scans all imported assets instantly
  - Creates alerts for found vulnerabilities
  - Shows scan results (scanned count, vulnerabilities found, errors)
  
- **Modern UI Theme**: Updated color scheme across all pages
  - New blue gradient: #1e3c72 → #2a5298
  - Glassmorphism effects on navigation bars
  - Improved button styles with hover animations
  - Color-coded severity badges (Critical, High, Medium, Low)
  
- **Navigation Updates**: Added "Vulnerabilities" link to all page navbars
  - Dashboard
  - Assets
  - Users
  - Settings

### Fixed
- **HTTP 405 Errors on Settings**: Added `PUT /api/settings/<key>` endpoint
  - Individual setting updates now work correctly
  - All settings save properly with 200 OK responses
  - Frontend updated to use PUT instead of POST for individual settings

### Changed
- **Login Page**: Updated gradient colors to match new theme
- **Dashboard**: Modernized navbar with new color scheme
- **All Pages**: Updated button styles and hover effects
- **README**: Updated to reflect new features and color scheme

### Technical Details

**New Backend Endpoints:**
```python
POST /api/vulnerabilities/scan          # Manual scan all assets
POST /api/vulnerabilities/search        # Search CVEs by product/version
PUT  /api/settings/<key>                # Update individual setting
```

**New Functions:**
```python
search_nvd_by_product(product, version)  # Query NVD API v2.0
scan_asset_vulnerabilities(asset)        # Automated asset scanning
scan_all_assets()                        # Manual scan trigger
```

**New Files:**
- `frontend/vulnerabilities.html` (18KB) - Vulnerability scanner page
- `screenshots/` - 6 screenshots showing new features

### Dependencies
No new dependencies required. Using existing:
- `requests` for NVD API calls
- `Flask` for backend
- Vanilla JavaScript for frontend

### Testing Verified
- ✅ Manual vulnerability scanning (5 assets)
- ✅ NVD API search (tested with "Windows 10")
- ✅ Settings PUT endpoints (all 5 settings)
- ✅ New UI colors across all pages
- ✅ Navigation between pages
- ✅ Assets import from AD (5 devices)

### Known Limitations
- NVD API requires internet connectivity
- API rate limits apply (unauthenticated: 5 requests per 30 seconds)
- Optional API key can be configured for higher limits

### Performance
- Fast searches (< 2 seconds typical)
- Efficient parallel asset scanning
- Real-time UI updates
- Non-blocking operations

### Security
- Session-based authentication maintained
- Admin-only access to scans and settings
- Input validation on all endpoints
- Secure API calls with 15-second timeouts
- HTTPS used for NVD API calls

## Previous Versions

### [v1.0.0] - 2025-11-13
- Initial release with JWT authentication
- Replaced JWT with simple session-based auth
- Basic asset management
- Alert system framework
- User management
- Settings page

---

For more details, see the commit history.
