# IDSS User Training Manual
## AI-Powered Section Throughput Optimization - User Guide

### Version: 1.0
### Target Audience: Railway Operations Staff
### Classification: RESTRICTED - For Railway Personnel Only

---

## Table of Contents

1. [Introduction to IDSS](#introduction-to-idss)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Operating the System](#operating-the-system)
5. [Scenario Management](#scenario-management)
6. [Analytics and Reports](#analytics-and-reports)
7. [Emergency Procedures](#emergency-procedures)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Quick Reference](#quick-reference)
10. [Frequently Asked Questions](#frequently-asked-questions)

---

## Introduction to IDSS

### What is IDSS?
The Intelligent Decision Support System (IDSS) is an AI-powered platform designed to optimize section throughput in Indian Railways. It provides real-time analytics, conflict prediction, and optimization recommendations to help railway operators make informed decisions.

### Key Benefits
- **Improved Punctuality**: 15-20% reduction in delays through predictive analytics
- **Enhanced Safety**: Early conflict detection and prevention
- **Increased Throughput**: 12-18% improvement in section capacity utilization
- **Cost Savings**: ₹2-5 lakhs per section per month through optimization
- **Better Decision Making**: Data-driven insights for operational decisions

### System Components
1. **Unified Dashboard**: Web-based control interface
2. **Analytics Engine**: AI-powered prediction and optimization
3. **What-If Scenarios**: Impact simulation capabilities
4. **Real-time Monitoring**: Live train tracking and status updates
5. **Alert System**: Automated notifications for critical events

---

## Getting Started

### System Requirements
- **Browser**: Chrome 90+, Firefox 88+, Edge 90+
- **Screen Resolution**: Minimum 1366x768 (Recommended: 1920x1080)
- **Internet Connection**: Stable broadband connection
- **Login Credentials**: Provided by Railway IT Department

### First Time Login

#### Step 1: Access the System
1. Open your web browser
2. Navigate to: `https://idss.railways.gov.in`
3. Ensure secure connection (🔒 icon in address bar)

#### Step 2: Authentication
```
Login Page Elements:
┌─────────────────────────────────────┐
│        Indian Railways IDSS        │
├─────────────────────────────────────┤
│                                     │
│  Username: [________________]       │
│  Password: [________________]       │
│  Zone:     [Central Railway ▼]     │
│                                     │
│         [LOGIN] [HELP]              │
│                                     │
└─────────────────────────────────────┘
```

1. Enter your assigned username
2. Enter your password
3. Select your railway zone from dropdown
4. Click **LOGIN**

#### Step 3: Initial Setup
After first login, you'll be prompted to:
1. Change default password
2. Set up security questions
3. Review user permissions
4. Complete system orientation

### Password Requirements
- Minimum 12 characters
- Must include: uppercase, lowercase, numbers, special characters
- Cannot reuse last 5 passwords
- Must be changed every 90 days

---

## Dashboard Overview

### Main Dashboard Layout

```
┌────────────────────────────────────────────────────────────────────┐
│ IDSS - Central Railway │ User: Operator1 │ Zone: CR │ [LOGOUT] │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Active    │ │   Delayed   │ │ Conflicts   │ │ Throughput  │ │
│ │   Trains    │ │   Trains    │ │ Predicted   │ │    Rate     │ │
│ │     156     │ │     12      │ │      5      │ │    92.3%    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                    │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │                    Live Train Map                              │ │
│ │  STN_A ●────●────●────●────● STN_B ●────●────●────●────● STN_C │ │
│ │      T001   T002   T003                T004   T005           │ │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────┐ │
│ │   Active Alerts  │ │  What-If Scenarios │ │  Performance Trends  │ │
│ │                  │ │                    │ │                      │ │
│ │ • Platform Conf. │ │ [Run Emergency]    │ │ ╭─╮  Punctuality     │ │
│ │ • Signal Delay   │ │ [Run Maintenance]  │ │ │ │╱  ╱╲             │ │
│ │ • Track Issue    │ │ [Run Weather]      │ │ ╰─╱  ╱  ╲ 92.3%      │ │
│ └──────────────────┘ └──────────────────┘ └──────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### Dashboard Sections

#### 1. Key Performance Indicators (Top Row)
- **Active Trains**: Number of trains currently in section
- **Delayed Trains**: Trains running behind schedule
- **Conflicts Predicted**: AI-detected potential conflicts
- **Throughput Rate**: Current section efficiency percentage

#### 2. Live Train Map (Center)
- Real-time visualization of train positions
- Color-coded status indicators:
  - 🟢 **Green**: On-time trains
  - 🟡 **Yellow**: Minor delays (0-5 minutes)
  - 🔴 **Red**: Significant delays (>5 minutes)
  - 🔵 **Blue**: Priority/Express trains

#### 3. Control Panels (Bottom Row)
- **Active Alerts**: Real-time notifications and warnings
- **What-If Scenarios**: Quick access to simulation tools
- **Performance Trends**: Historical data visualization

---

## Operating the System

### Daily Operation Workflow

#### Morning Startup Checklist
1. **System Health Check**
   ```
   ✓ Login successfully
   ✓ Verify all services are online (green indicators)
   ✓ Check connectivity to railway systems
   ✓ Review overnight alerts and logs
   ✓ Confirm current shift personnel assignments
   ```

2. **Data Validation**
   ```
   ✓ Verify train schedules are updated
   ✓ Check signal and track status
   ✓ Confirm weather data integration
   ✓ Review maintenance windows
   ✓ Validate crew assignments
   ```

3. **Initial Assessment**
   ```
   ✓ Review current section status
   ✓ Identify potential bottlenecks
   ✓ Check predicted conflicts for next 4 hours
   ✓ Prepare contingency plans
   ✓ Brief team on priority trains
   ```

### Real-Time Monitoring

#### Train Status Monitoring
```
Train Details Panel:
┌─────────────────────────────────────┐
│ Train: 12345 (Rajdhani Express)     │
│ Route: CSMT → BCT                   │
│ Status: On-time ✓                   │
│ Current: Kurla (KR)                 │
│ Next: Bandra (BA) - ETA: 10:15      │
│ Delay: +2 minutes                   │
│ Speed: 85 km/h                      │
│ Coach: 16, Load: 95%                │
└─────────────────────────────────────┘
```

Click on any train marker to view:
- Current location and speed
- Schedule adherence
- Next station and ETA
- Passenger load information
- Crew details
- Route deviations

#### Alert Management
Alerts are categorized by priority:

**🔴 CRITICAL (Immediate Action Required)**
- Signal failures
- Track obstructions
- Emergency situations
- System malfunctions

**🟡 WARNING (Monitor Closely)**
- Minor delays building up
- Equipment issues
- Weather warnings
- Crew changes

**🔵 INFORMATION (Awareness Only)**
- Schedule updates
- Routine maintenance
- System notifications
- Performance reports

### Responding to Alerts

#### Alert Response Procedure
1. **Acknowledge Alert**: Click notification to acknowledge
2. **Assess Impact**: Review affected trains and routes
3. **Consult AI Recommendations**: Check system suggestions
4. **Take Action**: Implement corrective measures
5. **Monitor Results**: Track effectiveness of actions
6. **Document**: Log actions taken and outcomes

#### Example Alert Response
```
ALERT: Platform congestion predicted at Dadar (DR)
Time: 14:30
Affected Trains: 12345, 67890, 11111
AI Recommendation: Hold train 67890 at Kurla for 3 minutes

Response Options:
[Accept AI Recommendation]  [Run Custom Scenario]  [Manual Override]

Actions Taken:
✓ Implemented 3-minute hold for train 67890
✓ Notified station master at Dadar
✓ Updated passenger information system
✓ Monitoring situation - estimated resolution: 14:45
```

---

## Scenario Management

### What-If Scenarios
Scenarios help predict the impact of operational decisions before implementation.

### Common Scenario Types

#### 1. Emergency Hold Scenario
**When to Use**: Signal failure, track obstruction, emergency situations

**Steps to Execute**:
1. Click **"Run Emergency"** button
2. Select affected train from dropdown
3. Choose hold location
4. Set hold duration (5-30 minutes)
5. Review impact analysis
6. Confirm execution

```
Emergency Hold Configuration:
┌─────────────────────────────────────┐
│ Train to Hold: [12345 ▼]            │
│ Hold Location: [Kurla (KR) ▼]       │
│ Duration: [15] minutes               │
│ Reason: [Signal Failure ▼]          │
│                                     │
│ Predicted Impact:                   │
│ • 3 trains affected                 │
│ • 12 minutes average delay          │
│ • Platform congestion: MODERATE     │
│                                     │
│ [EXECUTE] [CANCEL] [SAVE SCENARIO]  │
└─────────────────────────────────────┘
```

#### 2. Maintenance Window Scenario
**When to Use**: Planned maintenance, track work, signal testing

**Configuration Options**:
- **Start Time**: When maintenance begins
- **Duration**: Expected maintenance time
- **Affected Sections**: Which tracks/signals involved
- **Traffic Diversion**: Alternative routing options

#### 3. Weather Impact Scenario
**When to Use**: Heavy rain, fog, extreme weather conditions

**Automatic Adjustments**:
- Speed restrictions based on weather conditions
- Extended station stops for passenger safety
- Alternative routing for weather-affected sections
- Updated ETAs based on weather impact

### Scenario Results Interpretation

#### Impact Analysis Report
```
Scenario: Emergency Hold - Train 12345
Execution Time: 14:30:00
Duration: 15 minutes

Direct Impact:
• Train 12345: +15 minutes delay
• Platform KR: Moderate congestion

Cascading Effects:
• Train 67890: +8 minutes delay
• Train 11111: +12 minutes delay
• Train 22222: +5 minutes delay

Recovery Estimate: 45 minutes
Passenger Impact: ~2,400 passengers affected
Cost Impact: ₹45,000 estimated

Recommendations:
1. Implement speed recovery on clear sections
2. Priority boarding at next stations
3. Update passenger announcements
4. Consider express routing for delayed trains
```

### Best Practices for Scenarios
1. **Run scenarios before implementing real changes**
2. **Save successful scenarios for future use**
3. **Document outcomes for learning purposes**
4. **Share effective scenarios with team members**
5. **Regular training on different scenario types**

---

## Analytics and Reports

### Performance Analytics

#### Daily Performance Dashboard
Access via: **Analytics** → **Daily Performance**

```
Daily Performance Summary - Date: 12/09/2025
┌─────────────────────────────────────────────────────────────┐
│                    Section Performance                      │
│                                                            │
│ Punctuality: 92.3% ████████████████████████████▓▓          │
│ Throughput:  88.7% ███████████████████████████▓▓▓          │
│ Efficiency:  91.1% ████████████████████████████▓▓▓         │
│                                                            │
│ Trains Processed: 245 | On-time: 226 | Delayed: 19        │
│ Average Delay: 4.2 minutes | Max Delay: 23 minutes        │
│ Cost Savings: ₹2,35,000 | Energy Saved: 15.2%            │
└─────────────────────────────────────────────────────────────┘
```

#### Key Performance Metrics
- **Punctuality Rate**: Percentage of trains arriving on time
- **Throughput Rate**: Section capacity utilization
- **Average Delay**: Mean delay time across all trains
- **Conflict Resolution**: Success rate of AI recommendations
- **Energy Efficiency**: Power consumption optimization
- **Cost Impact**: Financial savings from optimization

### Report Generation

#### Standard Reports Available
1. **Daily Operations Report**
   - Generated automatically at 00:00 hours
   - Includes all trains, delays, incidents
   - Sent to supervisors and managers

2. **Weekly Performance Analysis**
   - Trend analysis and comparisons
   - Key performance indicators
   - Improvement recommendations

3. **Monthly Executive Summary**
   - High-level performance metrics
   - ROI analysis and cost savings
   - Strategic recommendations

4. **Incident Analysis Report**
   - Detailed analysis of major incidents
   - Root cause analysis
   - Prevention strategies

#### Custom Report Creation
```
Custom Report Builder:
┌─────────────────────────────────────┐
│ Report Name: [____________]          │
│ Date Range: [01/09] to [12/09]      │
│ Include:                            │
│ ☑ Train delays                      │
│ ☑ Signal incidents                  │
│ ☐ Weather impacts                   │
│ ☑ AI recommendations               │
│ ☐ Energy consumption                │
│                                     │
│ Format: [PDF ▼] [Excel ▼]          │
│ Schedule: [Generate Now ▼]         │
│                                     │
│ [GENERATE] [SAVE TEMPLATE]          │
└─────────────────────────────────────┘
```

### Analytics Tools

#### Trend Analysis
- **Performance Trends**: Track improvements over time
- **Pattern Recognition**: Identify recurring issues
- **Seasonal Analysis**: Weather and festival impact
- **Predictive Analytics**: Forecast future performance

#### Comparative Analysis
- **Zone Comparisons**: Performance vs. other railway zones
- **Historical Comparisons**: Year-over-year improvements
- **Benchmark Analysis**: Against Indian Railway standards
- **International Benchmarks**: Global best practices

---

## Emergency Procedures

### Emergency Response Protocol

#### Level 1: Minor Disruptions
**Response Time**: Immediate (< 2 minutes)
**Authority**: Station Master/Traffic Controller

**Common Scenarios**:
- Single train delays (5-15 minutes)
- Minor signal issues
- Platform congestion
- Crew changes

**Response Steps**:
1. Acknowledge alert in IDSS
2. Review AI recommendations
3. Implement corrective actions
4. Monitor situation
5. Update passenger information

#### Level 2: Significant Disruptions
**Response Time**: < 5 minutes
**Authority**: Divisional Controller

**Common Scenarios**:
- Multiple train delays
- Signal failures
- Track issues
- Severe weather warnings

**Response Steps**:
1. Escalate to supervisory level
2. Implement emergency scenarios
3. Coordinate with affected stations
4. Deploy additional resources
5. Activate passenger assistance

#### Level 3: Major Emergencies
**Response Time**: < 2 minutes
**Authority**: Divisional Railway Manager

**Common Scenarios**:
- Track obstructions
- Signal system failures
- Natural disasters
- Security incidents

**Response Steps**:
1. Immediate escalation to management
2. Activate emergency response team
3. Implement system-wide changes
4. Coordinate with emergency services
5. Public communication strategy

### Emergency Contacts
```
Emergency Contact Directory:
┌─────────────────────────────────────┐
│ Divisional Control: 022-2694-XXXX   │
│ Station Master DR: 022-2695-XXXX    │
│ Signal Maintenance: 022-2696-XXXX   │
│ Medical Emergency: 108               │
│ Railway Police: 182                 │
│ Fire Services: 101                  │
│ IDSS Support: 1800-XXX-XXXX        │
└─────────────────────────────────────┘
```

### System Backup Procedures

#### Manual Operation Fallback
If IDSS becomes unavailable:

1. **Switch to Manual Mode**
   - Inform all stations immediately
   - Revert to traditional signaling
   - Maintain radio communication

2. **Data Backup**
   - Save current system state
   - Export critical train information
   - Document all ongoing incidents

3. **Recovery Process**
   - Contact IDSS technical support
   - Follow system restart procedures
   - Validate data integrity after restoration

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Dashboard Not Loading
**Symptoms**: Blank screen, loading errors, timeout messages

**Troubleshooting Steps**:
1. **Check Internet Connection**
   ```
   • Open another website to test connectivity
   • Try refreshing the page (Ctrl+F5)
   • Check if VPN is required and active
   ```

2. **Browser Issues**
   ```
   • Clear browser cache and cookies
   • Disable browser extensions
   • Try incognito/private mode
   • Update browser to latest version
   ```

3. **System Issues**
   ```
   • Check IDSS status page
   • Contact IT helpdesk
   • Use backup access method
   ```

#### Issue 2: Real-Time Data Not Updating
**Symptoms**: Static data, outdated train positions, no new alerts

**Troubleshooting Steps**:
1. **Verify Data Sources**
   ```
   • Check railway system connectivity indicators
   • Confirm signal system is operational
   • Validate GPS tracking systems
   ```

2. **Network Issues**
   ```
   • Test network latency
   • Check for firewall blocks
   • Verify API connections are active
   ```

3. **System Refresh**
   ```
   • Use manual refresh button
   • Restart dashboard session
   • Contact technical support if persistent
   ```

#### Issue 3: Scenario Execution Fails
**Symptoms**: Error messages when running scenarios, no impact analysis

**Troubleshooting Steps**:
1. **Input Validation**
   ```
   • Check all required fields are filled
   • Verify train IDs are correct
   • Ensure time ranges are valid
   ```

2. **System Resources**
   ```
   • Check if multiple scenarios running
   • Verify system performance status
   • Try simpler scenario first
   ```

3. **Data Issues**
   ```
   • Confirm train data is current
   • Check schedule information
   • Validate route data
   ```

### Error Messages Reference

#### Authentication Errors
- **"Invalid Credentials"**: Username/password incorrect
- **"Account Locked"**: Too many failed attempts (contact admin)
- **"Session Expired"**: Login again required
- **"Insufficient Permissions"**: Contact supervisor for access

#### System Errors
- **"Service Unavailable"**: System maintenance in progress
- **"Data Sync Error"**: Railway system connectivity issue
- **"Processing Timeout"**: High system load, try again
- **"Invalid Input"**: Check data format and try again

#### Network Errors
- **"Connection Lost"**: Network connectivity interrupted
- **"Slow Response"**: Network latency issues
- **"Access Denied"**: Firewall or security restriction
- **"Certificate Error"**: SSL/security configuration issue

### Getting Help

#### Self-Service Resources
1. **In-App Help**: Click ? icon for context-sensitive help
2. **Video Tutorials**: Access training videos from help menu
3. **Quick Reference**: Downloadable cheat sheets
4. **FAQ Section**: Common questions and answers

#### Support Escalation
```
Support Levels:
Level 1: Station IT Support (Local Issues)
└── Phone: XXX-XXX-XXXX
└── Email: station-it@railways.gov.in

Level 2: Divisional IT Support (System Issues)
└── Phone: XXX-XXX-XXXX  
└── Email: div-support@railways.gov.in

Level 3: IDSS Technical Team (Critical Issues)
└── Phone: 1800-XXX-XXXX (24x7)
└── Email: idss-support@railways.gov.in
```

---

## Quick Reference

### Keyboard Shortcuts
```
Navigation:
F1          - Help/Documentation
F5          - Refresh Dashboard
Ctrl+F5     - Hard Refresh (Clear Cache)
F11         - Full Screen Mode
Esc         - Close Popups/Cancel Actions

Dashboard:
Ctrl+D      - Open Daily Report
Ctrl+S      - Save Current View
Ctrl+P      - Print Current Screen
Ctrl+E      - Export Data
Alt+A       - Open Alerts Panel

Scenarios:
Ctrl+N      - New Scenario
Ctrl+R      - Run Scenario
Ctrl+H      - Scenario History
Space       - Quick Execute
Enter       - Confirm Action
```

### Status Indicators Reference
```
System Status:
🟢 Green   - Normal Operation
🟡 Yellow  - Caution/Warning
🔴 Red     - Critical/Error
🔵 Blue    - Information
⚪ Gray    - Inactive/Disabled

Train Status:
▶️ Green   - On Time
⏸️ Yellow  - Minor Delay (0-5 min)
⏹️ Orange  - Moderate Delay (5-15 min)
🛑 Red     - Major Delay (>15 min)
🔄 Blue    - Priority/Express

Alert Priorities:
🔴 CRITICAL - Immediate action required
🟡 WARNING  - Monitor closely
🔵 INFO     - Awareness only
```

### Important Phone Numbers
```
Emergency Contacts:
Railway Emergency: 182
Medical Emergency: 108
Fire Emergency: 101
Police Emergency: 100

IDSS Support:
Help Desk: 1800-XXX-XXXX
Technical Support: 1800-YYY-YYYY
Emergency Support: 1800-ZZZ-ZZZZ (24x7)

Management:
Station Master: XXX-XXX-XXXX
Divisional Controller: XXX-XXX-XXXX
Traffic Inspector: XXX-XXX-XXXX
```

### Data Backup Locations
```
Local Backups:
Dashboard Screenshots: C:\Users\%USERNAME%\IDSS\Screenshots
Exported Reports: C:\Users\%USERNAME%\IDSS\Reports
User Settings: C:\Users\%USERNAME%\IDSS\Config

Network Backups:
Server Backups: \\railways-backup\IDSS\
Archive Location: \\railways-archive\IDSS\{YYYY}\{MM}
```

---

## Frequently Asked Questions

### General Questions

**Q1: What browsers are supported?**
A: Chrome 90+, Firefox 88+, Edge 90+, Safari 14+. Internet Explorer is not supported.

**Q2: Can I access IDSS from mobile devices?**
A: Yes, IDSS has a responsive design that works on tablets and smartphones. However, full functionality is best on desktop computers.

**Q3: How often is the data updated?**
A: Train positions are updated every 30 seconds. System status and alerts are updated in real-time.

**Q4: What happens if my internet connection is lost?**
A: IDSS will display a connection lost message and attempt to reconnect automatically. Recent data remains cached for viewing.

**Q5: Can I customize the dashboard layout?**
A: Yes, you can rearrange widgets and save custom layouts. Contact your supervisor for advanced customization options.

### Technical Questions

**Q6: Why are some trains not showing on the map?**
A: This could be due to GPS tracking issues, system maintenance, or trains outside the monitored section.

**Q7: How accurate are the AI predictions?**
A: IDSS has a 91.5% accuracy rate for conflict predictions and 88.7% for delay predictions based on current performance metrics.

**Q8: What should I do if a scenario shows unrealistic results?**
A: Verify input parameters, check data currency, and if issues persist, contact technical support with scenario details.

**Q9: Can I override AI recommendations?**
A: Yes, operators can always override AI suggestions. However, manual overrides are logged for analysis and learning.

**Q10: How long are system logs retained?**
A: Operational logs are kept for 3 years, audit logs for 7 years, and critical incident logs permanently.

### Operational Questions

**Q11: When should I escalate an issue?**
A: Escalate when delays exceed 15 minutes, multiple trains are affected, or safety concerns arise.

**Q12: Can I see historical performance data?**
A: Yes, performance data is available for up to 3 years through the Analytics section.

**Q13: What training is required to use IDSS?**
A: All operators must complete the 16-hour IDSS certification course and pass the competency assessment.

**Q14: How do I report system bugs or suggestions?**
A: Use the feedback form in the Help section or email idss-feedback@railways.gov.in.

**Q15: What happens during system maintenance?**
A: Scheduled maintenance is announced 48 hours in advance. Emergency maintenance triggers fallback procedures.

### Access and Security

**Q16: How do I reset my password?**
A: Contact your local IT administrator or use the self-service password reset option (if enabled).

**Q17: Why was my account locked?**
A: Accounts are locked after 5 failed login attempts or 90 days of inactivity. Contact IT support to unlock.

**Q18: Can I share my login credentials?**
A: No, sharing credentials is strictly prohibited and may result in disciplinary action.

**Q19: What data can I export from IDSS?**
A: You can export reports, performance data, and analytics based on your role permissions.

**Q20: Is IDSS data secure?**
A: Yes, IDSS uses enterprise-grade security including encryption, secure authentication, and audit logging.

---

## Training Completion Certificate

```
┌──────────────────────────────────────────────────────────────────┐
│                        TRAINING CERTIFICATE                      │
│                                                                  │
│                      IDSS User Certification                    │
│                                                                  │
│   This certifies that _________________________ has successfully │
│   completed the IDSS User Training Program and demonstrated      │
│   competency in operating the Intelligent Decision Support      │
│   System for railway operations.                                │
│                                                                  │
│   Training Completed: ___________  Valid Until: ___________      │
│   Instructor: ________________    Supervisor: _____________      │
│                                                                  │
│   Signature: _________________    Date: ___________________      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Post-Training Requirements
1. Complete practical assessment within 30 days
2. Shadow experienced operator for minimum 5 shifts
3. Pass competency evaluation (80% minimum score)
4. Annual refresher training mandatory
5. Additional training required for system updates

---

**Document Control:**
- Version: 1.0
- Last Updated: September 12, 2025
- Next Review: December 12, 2025
- Approved By: Chief Operations Manager
- Classification: RESTRICTED - Railway Personnel Only

**For technical support or training questions:**
Email: idss-training@railways.gov.in
Phone: 1800-XXX-XXXX (Mon-Fri, 9:00-18:00)