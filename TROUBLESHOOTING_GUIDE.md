# IDSS Troubleshooting Guide
## Technical Issue Resolution for Railway Operations

### Version: 1.0
### Target: Operations Staff & Technical Support
### Classification: RESTRICTED

---

## Table of Contents

1. [System Access Issues](#system-access-issues)
2. [Dashboard Problems](#dashboard-problems)
3. [Data Related Issues](#data-related-issues)
4. [Performance Problems](#performance-problems)
5. [Scenario Execution Issues](#scenario-execution-issues)
6. [Alert System Problems](#alert-system-problems)
7. [Network Connectivity Issues](#network-connectivity-issues)
8. [Browser Related Problems](#browser-related-problems)
9. [Hardware Requirements](#hardware-requirements)
10. [Error Messages Reference](#error-messages-reference)

---

## System Access Issues

### Issue 1: Cannot Access Login Page

**Symptoms:**
- Browser shows "Site cannot be reached"
- Timeout errors
- DNS resolution failures

**Troubleshooting Steps:**

1. **Check URL**
   ```
   Development: http://localhost:8000
   Production:  https://idss.railways.gov.in
   Staging:     https://idss-staging.railways.gov.in
   ```

2. **Network Connectivity Test**
   ```powershell
   # Test basic connectivity
   ping idss.railways.gov.in
   
   # Test specific port
   Test-NetConnection -ComputerName idss.railways.gov.in -Port 443
   ```

3. **DNS Resolution**
   ```powershell
   nslookup idss.railways.gov.in
   ipconfig /flushdns
   ```

4. **Firewall/Proxy Check**
   - Contact IT team to verify firewall rules
   - Check corporate proxy settings
   - Try accessing from different network

**Resolution Priority:** HIGH
**Escalate to:** IT Support Team

---

### Issue 2: Login Authentication Fails

**Symptoms:**
- "Invalid credentials" message
- Account locked notifications
- Session timeout errors

**Troubleshooting Steps:**

1. **Credential Verification**
   ```
   ✓ Check username format (no spaces, correct case)
   ✓ Verify password (check Caps Lock)
   ✓ Confirm railway zone selection
   ✓ Check account expiry date
   ```

2. **Account Status Check**
   - Contact system administrator
   - Verify account is not locked
   - Check password expiry status
   - Confirm user permissions

3. **Browser Issues**
   ```
   ✓ Clear browser cache and cookies
   ✓ Disable browser extensions
   ✓ Try incognito/private mode
   ✓ Test different browser
   ```

**Common Solutions:**
- Password reset through admin
- Account unlock request
- Permission adjustment
- Browser cache clearing

**Resolution Priority:** HIGH
**Escalate to:** System Administrator

---

## Dashboard Problems

### Issue 3: Dashboard Not Loading Completely

**Symptoms:**
- Blank or partially loaded dashboard
- Missing widgets or panels
- Stuck on loading screen

**Diagnostic Steps:**

1. **Browser Console Check**
   ```
   Press F12 → Console tab
   Look for red error messages:
   
   Common Errors:
   - "Failed to fetch" → Network/API issue
   - "Unauthorized" → Session expired
   - "CORS error" → Security configuration
   ```

2. **Network Performance Test**
   ```
   F12 → Network tab → Refresh page
   Check for:
   - Failed requests (red status)
   - Slow loading resources (>5 seconds)
   - 404/500 error codes
   ```

3. **System Resources**
   ```
   Task Manager → Performance tab
   Check:
   - CPU usage < 80%
   - Memory usage < 90%
   - Disk activity
   ```

**Resolution Steps:**
1. **Force Refresh**: Ctrl+F5 or Ctrl+Shift+R
2. **Clear Cache**: Browser settings → Clear browsing data
3. **Restart Browser**: Close all windows and restart
4. **Check System Status**: Verify IDSS service health

**Resolution Priority:** MEDIUM
**Escalate to:** Technical Support

---

### Issue 4: Real-Time Data Not Updating

**Symptoms:**
- Train positions frozen
- Outdated timestamps
- No new alerts appearing
- KPI values not changing

**Troubleshooting Steps:**

1. **Data Connection Status**
   ```
   Dashboard → System Status Panel
   Check indicators:
   🟢 Database: ONLINE
   🟢 Analytics: ONLINE  
   🟢 Data Feed: ONLINE
   🟢 WebSocket: CONNECTED
   ```

2. **Manual Refresh Test**
   ```
   Click refresh button (🔄)
   Check if data updates immediately
   
   If YES: Automatic refresh issue
   If NO: Data pipeline problem
   ```

3. **Browser WebSocket Support**
   ```
   F12 → Console
   Type: typeof WebSocket
   Expected: "function"
   
   If undefined: Browser compatibility issue
   ```

4. **Network Connectivity**
   ```powershell
   # Test API endpoint
   curl -X GET http://localhost:8000/api/status
   
   # Expected response:
   {"status": "healthy", "uptime_minutes": 1440.5}
   ```

**Resolution Steps:**
1. **Manual Refresh**: F5 key or refresh button
2. **Reconnect WebSocket**: Close/open browser tab
3. **Check Source Systems**: Railway data feed status
4. **Restart IDSS Service**: Contact technical team

**Resolution Priority:** HIGH
**Escalate to:** Operations Manager + Technical Team

---

## Data Related Issues

### Issue 5: Incorrect Train Information

**Symptoms:**
- Wrong train positions
- Outdated schedule information
- Missing trains from display
- Incorrect delay calculations

**Verification Steps:**

1. **Cross-Reference with Source Systems**
   ```
   Check against:
   ✓ NTES (National Train Enquiry System)
   ✓ CRIS (Center for Railway Information Systems)
   ✓ Local station displays
   ✓ Radio communications
   ```

2. **Data Timestamp Check**
   ```
   Look for last update time in dashboard
   Compare with current time
   
   Acceptable delay: < 2 minutes
   Alert if delay: > 5 minutes
   ```

3. **Train ID Validation**
   ```
   Verify format: TXXXX (T followed by 4 digits)
   Check against train schedule
   Confirm route information
   ```

**Resolution Steps:**
1. **Manual Data Correction**: Update through admin interface
2. **System Synchronization**: Trigger data refresh
3. **Source System Check**: Verify upstream data quality
4. **Database Refresh**: Restart data ingestion service

**Resolution Priority:** HIGH
**Escalate to:** Data Management Team

---

## Performance Problems

### Issue 6: Slow System Response

**Symptoms:**
- Page loading takes >10 seconds
- Scenario execution timeout
- Delayed alert notifications
- UI freezing or stuttering

**Performance Diagnosis:**

1. **Client-Side Performance**
   ```
   F12 → Performance tab → Record
   Interact with system → Stop recording
   
   Look for:
   - Long tasks (>50ms)
   - Memory leaks
   - CPU spikes
   ```

2. **Network Performance**
   ```
   F12 → Network tab
   Check:
   - Request timing
   - Response sizes
   - Failed requests
   ```

3. **System Resources**
   ```
   Task Manager:
   - CPU: < 80%
   - RAM: < 8GB usage
   - Disk: < 90% usage
   - Network: Stable connection
   ```

**Optimization Steps:**
1. **Close Unnecessary Applications**
2. **Use Wired Internet Connection**
3. **Restart Browser**
4. **Clear Browser Cache**
5. **Check System Updates**

**Hardware Recommendations:**
- **CPU**: Intel i5 8th gen or equivalent
- **RAM**: 8GB minimum, 16GB recommended
- **Network**: 100 Mbps minimum
- **Browser**: Latest version

**Resolution Priority:** MEDIUM
**Escalate to:** IT Infrastructure Team

---

## Scenario Execution Issues

### Issue 7: Scenarios Fail to Execute

**Symptoms:**
- Error messages during scenario run
- Incomplete impact analysis
- System timeouts
- No response from AI engine

**Troubleshooting Steps:**

1. **Input Validation**
   ```
   Check scenario parameters:
   ✓ Train ID format (TXXXX)
   ✓ Valid time ranges
   ✓ Reasonable duration values
   ✓ Correct station codes
   ```

2. **System Capacity Check**
   ```
   Dashboard → System Health
   Verify:
   - Analytics Engine: ONLINE
   - Processing Queue: < 80% full
   - Database: Responsive
   ```

3. **Log File Review**
   ```
   Location: logs/scenarios/
   Look for:
   - Error timestamps
   - Stack traces
   - Input validation failures
   ```

**Common Fixes:**
1. **Simplify Scenario**: Reduce complexity
2. **Retry with Different Parameters**
3. **Clear Scenario Queue**: Cancel pending scenarios
4. **Restart Analytics Engine**: Contact technical team

**Resolution Priority:** MEDIUM
**Escalate to:** Analytics Team

---

## Alert System Problems

### Issue 8: Missing or Delayed Alerts

**Symptoms:**
- Critical events not generating alerts
- Notifications arriving late
- Alert fatigue (too many alerts)
- Inconsistent alert delivery

**Alert System Check:**

1. **Alert Configuration**
   ```
   Settings → Alert Management
   Verify:
   ✓ Alert rules enabled
   ✓ Threshold values correct
   ✓ Notification channels active
   ✓ User permissions set
   ```

2. **Notification Delivery**
   ```
   Test notification channels:
   - Dashboard notifications
   - Email alerts (if configured)
   - SMS alerts (if configured)
   - System logs
   ```

3. **Alert History Review**
   ```
   Reports → Alert History
   Check:
   - Recent alert patterns
   - Response times
   - False positive rate
   - Missing critical events
   ```

**Tuning Steps:**
1. **Adjust Thresholds**: Reduce false positives
2. **Priority Classification**: Critical vs. Warning
3. **Channel Configuration**: Enable/disable channels
4. **User Training**: Alert response procedures

**Resolution Priority:** HIGH
**Escalate to:** Operations Manager

---

## Network Connectivity Issues

### Issue 9: Intermittent Connection Loss

**Symptoms:**
- Frequent disconnection messages
- Data sync failures
- WebSocket reconnection attempts
- Partial functionality loss

**Network Diagnostics:**

1. **Connection Stability Test**
   ```powershell
   # Continuous ping test
   ping -t idss.railways.gov.in
   
   # Look for:
   # - Packet loss
   # - High latency (>500ms)
   # - Timeouts
   ```

2. **Bandwidth Test**
   ```
   Use online speed test tool
   Minimum requirements:
   - Download: 10 Mbps
   - Upload: 5 Mbps
   - Latency: <100ms
   ```

3. **WiFi vs. Wired Comparison**
   ```
   Test both connections:
   - Wired ethernet (preferred)
   - WiFi connection
   - Mobile hotspot (backup)
   ```

**Resolution Steps:**
1. **Switch to Wired Connection**
2. **Restart Network Equipment**: Modem/router
3. **Update Network Drivers**
4. **Contact ISP**: If persistent issues
5. **Use Backup Connection**: Mobile hotspot

**Resolution Priority:** HIGH
**Escalate to:** Network Administrator

---

## Browser Related Problems

### Issue 10: Browser Compatibility Issues

**Symptoms:**
- Features not working properly
- Display formatting problems
- JavaScript errors
- Missing functionality

**Browser Support Matrix:**
| Browser | Minimum Version | Recommended | Status |
|---------|----------------|-------------|--------|
| Chrome | 90+ | Latest | ✅ Fully Supported |
| Firefox | 88+ | Latest | ✅ Fully Supported |
| Edge | 90+ | Latest | ✅ Fully Supported |
| Safari | 14+ | Latest | ⚠️ Limited Support |
| IE | Any | N/A | ❌ Not Supported |

**Browser Configuration:**

1. **Enable JavaScript**
   ```
   Chrome: Settings → Privacy and Security → Site Settings → JavaScript
   Firefox: about:config → javascript.enabled = true
   Edge: Settings → Site Permissions → JavaScript
   ```

2. **Disable Interfering Extensions**
   ```
   Common problematic extensions:
   - Ad blockers (whitelist IDSS domain)
   - Privacy tools (may block WebSockets)
   - VPN extensions (check connectivity)
   - Script blockers
   ```

3. **Clear Browser Data**
   ```
   Recommended clearing:
   ✓ Cookies and site data
   ✓ Cached images and files
   ✓ Browsing history (optional)
   ✓ Download history (optional)
   ```

**Resolution Priority:** LOW
**Self-Service:** User can resolve

---

## Hardware Requirements

### Minimum System Requirements

**Desktop/Laptop:**
- **OS**: Windows 10, macOS 10.15, Ubuntu 18.04+
- **CPU**: Intel i3 8th gen / AMD Ryzen 3
- **RAM**: 8GB
- **Storage**: 500MB free space
- **Network**: 10 Mbps broadband
- **Display**: 1366x768 minimum

**Recommended Specifications:**
- **CPU**: Intel i5 10th gen / AMD Ryzen 5
- **RAM**: 16GB
- **Storage**: SSD with 2GB free space
- **Network**: 50 Mbps broadband
- **Display**: 1920x1080 or higher

**Mobile/Tablet:**
- **OS**: iOS 14+, Android 10+
- **RAM**: 4GB minimum
- **Screen**: 10" minimum for full functionality
- **Network**: 4G/WiFi with stable connection

---

## Error Messages Reference

### Authentication Errors

**ERR_AUTH_001: "Invalid Credentials"**
- **Cause**: Wrong username/password
- **Fix**: Verify credentials, reset password if needed

**ERR_AUTH_002: "Account Locked"**
- **Cause**: Too many failed login attempts
- **Fix**: Contact administrator to unlock account

**ERR_AUTH_003: "Session Expired"**
- **Cause**: Login session timeout (default: 8 hours)
- **Fix**: Login again

**ERR_AUTH_004: "Insufficient Permissions"**
- **Cause**: User role lacks required permissions
- **Fix**: Contact supervisor for access upgrade

### System Errors

**ERR_SYS_001: "Service Unavailable"**
- **Cause**: System maintenance or server overload
- **Fix**: Wait and retry, check system status page

**ERR_SYS_002: "Database Connection Failed"**
- **Cause**: Database server issues
- **Fix**: Contact technical support immediately

**ERR_SYS_003: "Data Sync Error"**
- **Cause**: Railway system connectivity problem
- **Fix**: Check source system status, retry sync

### Network Errors

**ERR_NET_001: "Connection Timeout"**
- **Cause**: Network latency or server overload
- **Fix**: Check internet connection, retry request

**ERR_NET_002: "WebSocket Connection Lost"**
- **Cause**: Network interruption
- **Fix**: Refresh page to reconnect

**ERR_NET_003: "API Rate Limit Exceeded"**
- **Cause**: Too many requests in short time
- **Fix**: Wait 1 minute before retrying

---

## Support Escalation Matrix

### Level 1: Self-Service (0-15 minutes)
**User Actions:**
- Browser refresh (F5)
- Clear cache
- Check internet connection
- Retry operation
- Restart browser

### Level 2: Local IT Support (15 minutes - 2 hours)
**Contact:** station-it@railways.gov.in
**Issues:**
- Hardware problems
- Network connectivity
- Browser configuration
- Local system issues

### Level 3: Divisional Support (2-8 hours)
**Contact:** div-support@railways.gov.in
**Issues:**
- User access management
- Data quality problems
- Regional connectivity issues
- Training requirements

### Level 4: IDSS Technical Team (24x7)
**Contact:** idss-support@railways.gov.in
**Phone:** 1800-XXX-XXXX
**Issues:**
- System outages
- Critical functionality failures
- Data corruption
- Security incidents

---

## Preventive Maintenance

### Daily Checks (Operations Staff)
- [ ] Verify system login
- [ ] Check all dashboard panels load
- [ ] Confirm real-time data updates
- [ ] Test alert notifications
- [ ] Review system status indicators

### Weekly Maintenance (IT Staff)
- [ ] Clear browser caches on shared terminals
- [ ] Check system performance metrics
- [ ] Review error logs
- [ ] Test backup procedures
- [ ] Update browser versions

### Monthly Reviews (Technical Team)
- [ ] Analyze performance trends
- [ ] Review user feedback
- [ ] Update troubleshooting procedures
- [ ] Conduct system health assessment
- [ ] Plan preventive maintenance

---

## Emergency Procedures

### System Outage Response

**Immediate Actions (0-5 minutes):**
1. Verify outage scope (local vs. system-wide)
2. Check alternative access methods
3. Notify operations manager
4. Activate manual procedures
5. Document outage start time

**Short-term Actions (5-30 minutes):**
1. Contact technical support
2. Implement backup procedures
3. Update status communications
4. Monitor restoration progress
5. Prepare situation report

**Recovery Actions (30+ minutes):**
1. Validate system functionality
2. Update all stakeholders
3. Review incident impact
4. Document lessons learned
5. Update procedures if needed

### Contact Information for Emergencies

**24x7 Emergency Hotline:** 1800-XXX-XXXX

**Emergency Email:** emergency@idss.railways.gov.in

**SMS Alerts:** Text "EMERGENCY" to XXXXX

---

**Document Information:**
- **Version**: 1.0
- **Last Updated**: September 13, 2025
- **Next Review**: December 13, 2025
- **Owner**: IDSS Technical Team
- **Classification**: RESTRICTED

**For immediate assistance:** Call 1800-XXX-XXXX