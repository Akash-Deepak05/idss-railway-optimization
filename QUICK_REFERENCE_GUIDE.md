# IDSS Quick Reference Guide
## Operator's Pocket Guide

---

## System Access
**URL:** `http://localhost:8000` (Development) / `https://idss.railways.gov.in` (Production)  
**Login:** Use your railway credentials  
**Browser:** Chrome/Firefox/Edge (latest versions)

---

## Dashboard Overview

### Key Indicators (Top Row)
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Total Trains│ │ Delayed     │ │ Conflicts   │ │ Throughput  │
│     156     │ │     12      │ │      5      │ │    92.3%    │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### Status Colors
- 🟢 **Green**: Normal/On-time
- 🟡 **Yellow**: Caution/Minor delay (0-5 min)
- 🔴 **Red**: Critical/Major delay (>5 min)
- 🔵 **Blue**: Information/Priority trains

---

## Quick Actions

### Emergency Scenarios
1. **Platform Congestion**
   - Click "Run Emergency Scenario"
   - Select "Platform Hold"
   - Choose affected train
   - Set duration: 5-15 minutes

2. **Signal Failure**
   - Click "Run Maintenance Scenario"  
   - Select "Signal Issue"
   - Choose affected section
   - Review impact before executing

3. **Weather Impact**
   - Click "Run Weather Scenario"
   - Select weather type (Rain/Fog)
   - Set severity level
   - Apply speed restrictions

### Viewing Train Details
- **Click any train marker** on the map
- View: Position, Speed, Delay, Next Station, ETA
- **Double-click** for detailed history

---

## Alert Response

### Alert Priorities
| Priority | Response Time | Authority Required |
|----------|--------------|-------------------|
| 🔴 CRITICAL | < 2 minutes | Station Master |
| 🟡 WARNING | < 5 minutes | Traffic Controller |
| 🔵 INFO | Monitor | Operator |

### Response Steps
1. **Acknowledge** alert (click notification)
2. **Review** AI recommendations
3. **Execute** approved actions
4. **Monitor** results
5. **Document** outcomes

---

## Keyboard Shortcuts

### Navigation
- **F1**: Help/Documentation
- **F5**: Refresh Dashboard  
- **F11**: Full Screen
- **Esc**: Close popups

### Actions
- **Ctrl+D**: Daily Report
- **Ctrl+S**: Save View
- **Ctrl+E**: Export Data
- **Space**: Quick Execute
- **Enter**: Confirm Action

---

## Performance Metrics

### Target Values
- **Punctuality**: >90%
- **Throughput**: >85%
- **Conflicts Predicted**: AI accuracy >90%
- **Response Time**: <100ms

### Daily Targets
- **On-time Performance**: 92%+
- **Average Delay**: <5 minutes
- **Section Utilization**: 85%+
- **Energy Efficiency**: 15%+ savings

---

## Common Issues & Quick Fixes

### Dashboard Not Loading
1. **Ctrl+F5** (hard refresh)
2. Clear browser cache
3. Check internet connection
4. Try incognito mode

### Data Not Updating
1. Click refresh button
2. Check system status indicators
3. Verify railway connectivity
4. Contact technical support

### Scenario Execution Fails
1. Check all required fields
2. Verify train ID format
3. Ensure valid time ranges
4. Try simpler scenario first

---

## Emergency Contacts

### Primary Contacts
- **Railway Emergency**: 182
- **IDSS Support**: 1800-XXX-XXXX
- **Technical Help**: 1800-YYY-YYYY

### Escalation Chain
1. **Level 1**: Station IT Support
2. **Level 2**: Divisional Support  
3. **Level 3**: IDSS Technical Team (24x7)

### Management Contacts
- **Station Master**: XXX-XXX-XXXX
- **Divisional Controller**: XXX-XXX-XXXX
- **Traffic Inspector**: XXX-XXX-XXXX

---

## System Status Indicators

### Service Health
```
Database: ●   Analytics: ●   API: ●   Monitoring: ●
         🟢           🟢      🟢            🟢
        ONLINE       ONLINE   ONLINE       ONLINE
```

### Connection Status
- **Strong Signal**: ████████ (8/8 bars)
- **Weak Signal**: ██░░░░░░ (2/8 bars)  
- **Offline**: ░░░░░░░░ (0/8 bars)

---

## Data Export Options

### Available Formats
- **PDF**: Reports and summaries
- **Excel**: Performance data and analytics
- **CSV**: Raw data for analysis
- **PNG**: Screenshots and charts

### Export Steps
1. **Ctrl+E** or click Export button
2. Select data range
3. Choose format
4. Click Generate
5. Download file

---

## Safety Reminders

### Before Taking Action
- ✓ Verify train identification
- ✓ Check current location
- ✓ Review impact analysis  
- ✓ Confirm authority level
- ✓ Document decision

### Critical Safety Rules
1. **Never override safety systems**
2. **Always verify train positions**
3. **Escalate uncertain situations**
4. **Maintain communication**
5. **Document all actions**

---

## Performance Tips

### For Better Response
- Keep browser updated
- Close unnecessary tabs
- Use wired internet connection
- Monitor system performance

### Best Practices
- Review morning briefings
- Check weather forecasts
- Monitor peak hour patterns
- Plan for contingencies
- Learn from past incidents

---

## Training Resources

### Self-Help
- **F1**: Context-sensitive help
- **Help Menu**: Video tutorials
- **FAQ Section**: Common questions
- **User Manual**: Complete documentation

### Training Schedule
- **Initial Training**: 16 hours
- **Certification**: Required
- **Refresher**: Annual
- **Updates**: As needed

---

## Version Information
- **IDSS Version**: 1.0
- **Guide Version**: 1.0  
- **Last Updated**: September 13, 2025
- **Next Review**: December 13, 2025

---

**Keep this guide accessible during operations!**

*For detailed procedures, refer to the complete User Training Manual*