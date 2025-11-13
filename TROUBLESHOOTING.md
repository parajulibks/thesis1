# Asset Sentinel - Troubleshooting Guide

## Common Issues and Solutions

### Issue: "localhost undefined" or Stuck Loading Indicators

**Symptoms:**
- Pages show "Loading..." that never completes
- Console shows "localhost undefined" errors
- API calls fail silently

**Solutions:**

#### 1. Clear Browser Cache (Most Common Fix)

**Chrome/Edge:**
1. Press `Ctrl+Shift+Delete` (Windows/Linux) or `Cmd+Shift+Delete` (Mac)
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh the page with `Ctrl+F5` (hard refresh)

**Firefox:**
1. Press `Ctrl+Shift+Delete`
2. Check "Cache"
3. Click "Clear Now"
4. Refresh with `Ctrl+F5`

**Safari:**
1. Go to Safari > Clear History
2. Select "all history"
3. Click "Clear History"
4. Refresh with `Cmd+R`

#### 2. Make Sure You're Using the Integrated Server

The application must be run using the **integrated server** (`app_integrated.py`), not the old `app.py`.

**Correct way to start:**
```bash
./start.sh
```

Or manually:
```bash
cd backend
python3 app_integrated.py
```

**DO NOT use:** `python3 app.py` (old version with issues)

#### 3. Verify Server is Running Correctly

You should see this output when starting the server:

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

If you see errors about modules not found, install dependencies:
```bash
cd backend
pip3 install -r requirements.txt
```

#### 4. Check the Correct URL

Make sure you're accessing:
- ✅ **http://localhost:5000** (correct)
- ❌ NOT http://localhost:8000
- ❌ NOT just opening the HTML file directly

#### 5. Use Browser Developer Tools

Press `F12` to open developer tools and check:

**Console Tab:**
- Look for JavaScript errors (red text)
- Common error: "Failed to fetch" means server isn't running

**Network Tab:**
- Check if API calls are being made
- Look for failed requests (red status codes)
- Status 401: Token expired, logout and login again
- Status 404: Wrong URL or server not running

#### 6. Force Browser to Reload Everything

Instead of just clicking refresh:
- **Windows/Linux:** Press `Ctrl+Shift+R` or `Ctrl+F5`
- **Mac:** Press `Cmd+Shift+R`

This forces the browser to reload all JavaScript and CSS files.

#### 7. Try Incognito/Private Mode

This ensures no cached files are used:
- **Chrome/Edge:** `Ctrl+Shift+N`
- **Firefox:** `Ctrl+Shift+P`
- **Safari:** `Cmd+Shift+N`

Then navigate to http://localhost:5000

---

## Other Common Issues

### Issue: Port 5000 Already in Use

**Error:** `Address already in use` or `OSError: [Errno 98]`

**Solution:**
1. Find and kill the process using port 5000:
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Or use a different port by editing backend/app_integrated.py
# Change the last line to use a different port:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Login Button Does Nothing

**Symptoms:**
- Click Login, nothing happens
- No error messages

**Solutions:**
1. Check browser console (F12) for JavaScript errors
2. Make sure server is running
3. Clear browser cache
4. Try a different browser

### Issue: 401 Unauthorized After Login

**Symptoms:**
- Login works but immediately redirected back to login
- Console shows 401 errors

**Solutions:**
1. Clear browser's localStorage:
   - Open Console (F12)
   - Type: `localStorage.clear()`
   - Press Enter
   - Refresh page

### Issue: Assets/Alerts Don't Load

**Symptoms:**
- Dashboard shows 0 for everything
- Tables are empty

**Solutions:**
1. Import sample assets:
   - Go to Assets page
   - Click "Import from AD"
   - Confirm the import
2. Database may need initialization:
```bash
cd backend
rm -f asset_sentinel.db instance/asset_sentinel.db
python3 app_integrated.py
```

---

## Verifying Everything Works

### Quick Test Checklist

1. ✅ Start server: `./start.sh`
2. ✅ See "Asset Sentinel is running!" message
3. ✅ Open browser to http://localhost:5000
4. ✅ Login page appears with gradient background
5. ✅ Login with admin/admin123
6. ✅ Dashboard loads with statistics
7. ✅ Click Assets → page loads
8. ✅ Click Import from AD → assets appear
9. ✅ Return to Dashboard → Total Assets shows 5

If all steps work, the application is functioning correctly!

---

## Getting Help

If you're still experiencing issues:

1. **Check the browser console (F12)** - Look for error messages
2. **Check server logs** - Look at the terminal where you started the server
3. **Try the steps above** - Especially clearing cache and using hard refresh
4. **Open an issue** - Include:
   - Browser and version
   - Operating system
   - Error messages from console
   - Screenshot of the issue

---

## Performance Tips

### Making the Application Faster

1. **Disable Debug Mode for Production:**
   Edit `backend/app_integrated.py`, change last line:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. **Use Production WSGI Server:**
   ```bash
   pip3 install gunicorn
   cd backend
   gunicorn -w 4 -b 0.0.0.0:5000 app_integrated:app
   ```

3. **Database Performance:**
   For large deployments, migrate from SQLite to PostgreSQL
   (See README.md for instructions)

---

**Still having trouble?** The application has been tested and verified to work correctly. Most issues are browser caching or incorrect startup procedures. Follow the steps above carefully!
