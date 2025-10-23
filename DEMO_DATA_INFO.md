# 🎭 Demo Data Information

## 🎯 Demo Mode Features

Your system now runs with **realistic demo data** that showcases the complete Zoho-ClickUp integration workflow without requiring real API credentials.

## 📊 Demo Tickets

The system generates **6 realistic demo tickets** that represent common scenarios:

### 1. Platform Issues
- **Ticket:** "Platform system crash during login"
- **Category:** Platform Issues → **Team:** Product/Tech
- **ClickUp List:** demo_platform_list_123

### 2. Facilities
- **Ticket:** "Projector not working in Room 101"  
- **Category:** Facilities → **Team:** Facilities
- **ClickUp List:** demo_facilities_list_456

### 3. Session Timing
- **Ticket:** "Session timing delay notification not working"
- **Category:** Session Timing Issues → **Team:** Curriculum/Content
- **ClickUp List:** demo_session_list_789

### 4. QA Reports
- **Ticket:** "QA report generation failing"
- **Category:** Tech QA Report Issue → **Team:** Product/Tech
- **ClickUp List:** demo_qa_list_101

### 5. Student Portal
- **Ticket:** "Student portal dashboard not loading"
- **Category:** Student Portal → **Team:** Product/Tech
- **ClickUp List:** demo_student_list_202

### 6. Instructor Issues
- **Ticket:** "Instructor unable to mark attendance"
- **Category:** Session Handling Issues → **Team:** Instructor
- **ClickUp List:** demo_instructor_list_303

## 🧠 Categorization Logic

The demo showcases intelligent categorization using **keyword matching**:

```python
"Platform Issues": ["platform", "system", "login", "portal", "access"]
"Facilities": ["projector", "room", "hardware", "facility", "equipment"]
"Session Timing": ["session", "timing", "schedule", "delay", "reschedule"]
"QA Reports": ["qa", "quality", "report", "bug", "testing"]
"Student Portal": ["student", "portal", "enrollment", "profile", "dashboard"]
"Instructor": ["instructor", "teaching", "class", "attendance", "mark"]
```

## 🎮 Demo API Endpoints

All endpoints work with demo data:

- `GET /api/status` - Shows demo mode status
- `POST /api/sync` - Processes 6 demo tickets
- `POST /api/categorize` - Categorizes any input tickets
- `GET /api/categories` - Lists all 6 categories
- `GET /api/teams` - Lists all 4 teams
- `GET /api/history` - Shows demo sync history

## 🔄 Demo Sync Results

When you run a sync, you'll see:

```json
{
  "total_tickets": 6,
  "processed": 6,
  "successful": 6,
  "errors": 0,
  "duplicates": 0,
  "execution_time": 1.2
}
```

## 🎯 Demo Credentials Used

```bash
# Zoho Demo Credentials
ZOHO_CLIENT_ID="demo_zoho_client_12345"
ZOHO_CLIENT_SECRET="demo_zoho_secret_67890"
ZOHO_REFRESH_TOKEN="demo_zoho_refresh_abcdef"
ZOHO_ORGANIZATION_ID="demo_org_123456789"

# ClickUp Demo Credentials  
CLICKUP_API_TOKEN="demo_clickup_token_xyz789"
CLICKUP_TEAM_ID="demo_team_456"

# Demo List IDs
PLATFORM_LIST_ID="demo_platform_list_123"
FACILITIES_LIST_ID="demo_facilities_list_456"
SESSION_LIST_ID="demo_session_list_789"
QA_LIST_ID="demo_qa_list_101"
STUDENT_LIST_ID="demo_student_list_202"
INSTRUCTOR_LIST_ID="demo_instructor_list_303"
```

## 🔄 Switching to Production

To use real APIs, simply replace demo credentials with actual ones:

```bash
firebase functions:config:set zoho.client_id="YOUR_REAL_CLIENT_ID"
firebase functions:config:set clickup.api_token="YOUR_REAL_TOKEN"
# ... etc
firebase deploy --only functions
```

## 🎉 Demo Benefits

✅ **No API Setup Required** - Works immediately  
✅ **Realistic Data** - Shows actual workflow  
✅ **Full Functionality** - All features demonstrated  
✅ **Safe Testing** - No real API calls  
✅ **Easy Transition** - Switch to production anytime  

The demo mode provides a complete preview of how your Zoho-ClickUp integration will work in production!