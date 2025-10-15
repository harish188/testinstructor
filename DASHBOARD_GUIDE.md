# 📊 Excel-like Dashboard Guide

## 🚀 Quick Start

1. **Start the server:**
   ```bash
   cd zoho-clickup-automation
   source venv/bin/activate
   python main.py server
   ```

2. **Open dashboard:** http://localhost:8000

3. **Enable Preview Mode** (default: ON) - Uses mock data instead of live Zoho API

4. **Click "Fetch Tickets"** - Loads 10 sample tickets with realistic scenarios

## 🎯 Dashboard Features

### 📋 Excel-like Interface
- **Sortable columns** - Click any column header to sort
- **Color-coded rows** by team assignment:
  - 🔵 **Product/Tech** - Light blue background
  - 🟢 **Curriculum** - Light green background  
  - 🟠 **Instructor** - Light orange background
  - 🔴 **Uncategorized** - Light red background (for errors)

### ✅ Ticket Selection
- **Individual selection** - Check boxes for specific tickets
- **Select All** - Bulk select/deselect all tickets
- **Selection counter** - Shows how many tickets are selected

### 🎛️ Action Buttons
- **Fetch Tickets** - Load tickets from Zoho API or mock data
- **Sync to ClickUp** - Create tasks for selected tickets
- **Refresh** - Reload the table after changes
- **Edit Category** - Manually adjust ticket categorization

## 🧠 Smart Categorization

The system automatically categorizes tickets based on content analysis:

| **Keywords** | **Category** | **Team** |
|-------------|-------------|----------|
| quiz, assessment, score | Quiz Issues | Curriculum |
| portal, login, access | Portal Access | Product/Tech |
| bundle, content | Content Bundle | Curriculum |
| role, flag, permission | Feature Flags / Roles Adding | Product/Tech |
| unlock, unit not available | Units Unlock | Curriculum |
| instructor, mentor | Instructor Categories Adding | Instructor |
| feedback grooming | Grooming Check Issues | Instructor |
| *default* | Learning Portal Issues | Product/Tech |

## 📊 Sample Data

The mock data includes 10 realistic tickets:

1. **TICKET-001** - Quiz module not loading → Quiz Issues (Curriculum)
2. **TICKET-002** - Cannot login to portal → Portal Access (Product/Tech)
3. **TICKET-003** - Content bundle missing → Content Bundle (Curriculum)
4. **TICKET-004** - Need instructor role → Feature Flags (Product/Tech)
5. **TICKET-005** - Units locked → Units Unlock (Curriculum)
6. **TICKET-006** - Feedback grooming needed → Grooming Check (Instructor)
7. **TICKET-007** - Portal access denied → Portal Access (Product/Tech)
8. **TICKET-008** - Mentor permissions → Instructor Categories (Instructor)
9. **TICKET-009** - Duplicate quiz issue → Quiz Issues (Curriculum)
10. **TICKET-010** - General portal question → Learning Portal (Product/Tech)

## 🔄 Workflow

### Preview Mode (Default)
1. **Fetch Tickets** → Loads mock data instantly
2. **Review** → Check categorization and team assignments
3. **Edit** → Manually adjust categories if needed
4. **Select** → Choose tickets to sync
5. **Sync** → Simulates ClickUp task creation (generates fake task IDs)

### Production Mode
1. **Disable Preview Mode** → Uncheck the toggle
2. **Configure API credentials** → Update .env file
3. **Fetch Tickets** → Loads real data from Zoho Desk
4. **Sync** → Creates actual ClickUp tasks

## 🎨 Visual Features

### Color Legend
- Always visible at the top of the dashboard
- Shows team color mappings
- Helps identify ticket assignments at a glance

### Status Badges
- **Pending** - Yellow badge (not yet synced)
- **Synced** - Green badge (successfully created in ClickUp)
- **Failed** - Red badge (sync error occurred)

### Interactive Elements
- **Hover effects** on rows and buttons
- **Loading overlays** during operations
- **Success/error notifications** for user feedback
- **Modal dialogs** for editing categories

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Zoho Desk API
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORGANIZATION_ID=your_org_id

# ClickUp API
CLICKUP_API_TOKEN=your_api_token
CLICKUP_TEAM_ID=your_team_id

# ClickUp List IDs (one for each category)
LEARNING_PORTAL_LIST_ID=list_id_1
FEATURE_FLAGS_LIST_ID=list_id_2
CONTENT_ACCESS_LIST_ID=list_id_3
PORTAL_ACCESS_LIST_ID=list_id_4
CONTENT_BUNDLE_LIST_ID=list_id_5
QUIZ_ISSUES_LIST_ID=list_id_6
UNITS_UNLOCK_LIST_ID=list_id_7
INSTRUCTOR_LIST_ID=list_id_8
GROOMING_CHECK_LIST_ID=list_id_9
```

## 🚨 Error Handling

- **API failures** → Retry up to 3 times with exponential backoff
- **Invalid data** → Skip problematic tickets and continue
- **Network issues** → Show user-friendly error messages
- **Duplicate detection** → Automatically merge similar tickets

## 📈 Statistics

The dashboard shows real-time stats:
- **Total Tickets** - Number of loaded tickets
- **Team Distribution** - Count per team (Product/Tech, Curriculum, Instructor)
- **Selection Status** - How many tickets are selected

## 🎯 Best Practices

1. **Start with Preview Mode** to test categorization rules
2. **Review categories** before syncing to ClickUp
3. **Use Edit Category** to fine-tune assignments
4. **Select relevant tickets** rather than syncing everything
5. **Monitor the logs** for any sync issues

## 🔍 Troubleshooting

### Common Issues
- **No tickets loaded** → Check API credentials or use Preview Mode
- **Wrong categorization** → Use Edit Category to manually adjust
- **Sync failures** → Verify ClickUp list IDs in .env file
- **Duplicate tickets** → System automatically handles duplicates

### Debug Mode
```bash
# Enable detailed logging
LOG_LEVEL=DEBUG python main.py server
```

## 🎉 Success Indicators

✅ **Dashboard loads** with clean Excel-like interface  
✅ **Fetch Tickets** loads 10 mock tickets in Preview Mode  
✅ **Color coding** shows different teams clearly  
✅ **Sorting** works on all columns  
✅ **Selection** allows choosing specific tickets  
✅ **Edit Category** opens modal for manual adjustments  
✅ **Sync to ClickUp** generates task IDs in Preview Mode  
✅ **Statistics** update in real-time  

The dashboard is now ready for both preview testing and production use! 🚀