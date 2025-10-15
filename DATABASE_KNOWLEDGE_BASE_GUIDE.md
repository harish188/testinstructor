# 🗄️ Database-Based Knowledge Base System

## 🎯 Overview

The system now uses a **database-based knowledge base** instead of CSV files. All categorization rules are stored in the database and can be updated programmatically. When tickets are created, the system automatically checks the knowledge base and categorizes them accordingly.

## 📊 How It Works

1. **Knowledge Base Storage**: Categories, teams, keywords, and rules are stored in the `knowledge_base` table
2. **Automatic Categorization**: When a ticket is processed, the system queries the database for matching keywords
3. **Real-time Updates**: Knowledge base changes take effect immediately without restarting the system
4. **Weighted Scoring**: Each category can have different weights for more accurate categorization

## 🚀 Quick Setup

### 1. Initialize the Knowledge Base:
```bash
cd zoho-clickup-automation
source venv/bin/activate
python3 add_knowledge_base.py
```

This will create the database and populate it with your 17 categories across 5 teams.

### 2. Test Categorization:
```bash
python3 test_categorization.py
```

This will test the categorization with sample tickets and show results.

### 3. Start the System:
```bash
python3 main.py server
```

The dashboard will now use the database-based knowledge base automatically.

## 📝 Adding Knowledge Base Entries

### Method 1: Direct Script (Recommended)
Edit `add_knowledge_base.py` and add your entries:

```python
knowledge_base_entries = [
    {
        "category": "Your New Category",
        "team": "Your Team",
        "keywords": ["keyword1", "keyword2", "phrase with spaces"],
        "description": "Description of this category",
        "weight": 1.0  # Higher weight = higher priority
    }
]
```

Then run: `python3 add_knowledge_base.py`

### Method 2: Via API (When Server is Running)
```python
import requests

entries = [
    {
        "category": "New Category",
        "team": "Team Name", 
        "keywords": ["keyword1", "keyword2"],
        "description": "Category description",
        "weight": 1.0
    }
]

response = requests.post(
    "http://localhost:8000/api/knowledge-base/add",
    json=entries
)
```

### Method 3: Via Dashboard CSV Upload
- Click "Upload KB" in the dashboard
- Upload a CSV file with format: `category,team,keywords,description`
- System will update the database automatically

## 🎯 Current Knowledge Base

Your system includes **17 categories** across **5 teams**:

### Product/Tech Team (6 categories):
- Platform Issues
- Tech QA Report Issue  
- Student Portal
- Learning Portal Issues
- Feature Flags / Roles Adding
- Portal Access

### Curriculum/Content Team (6 categories):
- Session Timing Issues
- Scheduling Issue
- Content Access
- Content Bundle
- Quiz Issues
- Units Unlock

### Instructor Team (2 categories):
- Session Handling Issues
- Instructor Categories Adding

### Facilities Team (2 categories):
- Facilities
- Other On-Ground Issues

### DA Team (1 category):
- Data mismatching in lookers studio

## 🔍 How Categorization Works

### Keyword Matching:
1. **Multi-word phrases** get **15 points** × weight
2. **Single keywords** get **10 points** × weight
3. **Case-insensitive** matching
4. **Highest score wins**

### Example:
```
Ticket: "Platform system crash during peak hours"

Matches:
- "platform" (10 points)
- "system" (10 points) 
- "crash" (10 points)
- Platform Issues weight: 1.2

Final Score: (10 + 10 + 10) × 1.2 = 36 points
Result: Platform Issues → Product/Tech Team
```

## 📊 Database Schema

### knowledge_base table:
```sql
CREATE TABLE knowledge_base (
    id INTEGER PRIMARY KEY,
    category VARCHAR NOT NULL,
    team VARCHAR NOT NULL,
    keywords TEXT NOT NULL,  -- JSON array of keywords
    description TEXT,
    weight FLOAT DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 🛠️ Management Commands

### View Current Knowledge Base:
```bash
python3 -c "
from services.knowledge_base_service import KnowledgeBaseService
kb = KnowledgeBaseService()
entries = kb.get_all_knowledge_base()
for entry in entries:
    print(f'{entry[\"category\"]} → {entry[\"team\"]} ({len(entry[\"keywords\"])} keywords)')
"
```

### Add Single Entry:
```bash
python3 -c "
from services.knowledge_base_service import KnowledgeBaseService
kb = KnowledgeBaseService()
kb.add_knowledge_base_entries([{
    'category': 'New Category',
    'team': 'Team Name',
    'keywords': ['keyword1', 'keyword2'],
    'description': 'Description'
}])
"
```

### Test Specific Ticket:
```bash
python3 -c "
from models import ZohoTicket
from services.categorization_service import CategorizationService
from datetime import datetime

ticket = ZohoTicket(
    id='TEST',
    subject='Your ticket subject',
    description='Your ticket description',
    status='Open',
    priority='High',
    created_time=datetime.now(),
    modified_time=datetime.now()
)

cs = CategorizationService()
category = cs.categorize_ticket(ticket)
team = cs.get_team_for_category(category)
print(f'Category: {category} → Team: {team}')
"
```

## 🎨 Dashboard Integration

The dashboard automatically uses the database knowledge base:

1. **Fetch Tickets** → Categorizes using database rules
2. **Filter Dropdowns** → Populated from database categories
3. **Team Stats** → Calculated from database team mappings
4. **Edit Category** → Updates use database categories
5. **Upload KB** → Updates database directly

## 🔄 Real-time Updates

- **No restart required** - Changes take effect immediately
- **Automatic reload** - Categorization service reloads rules from database
- **Live dashboard** - Filters and options update automatically
- **Persistent storage** - All changes saved to database

## 📈 Advanced Features

### Weighted Categories:
```python
# Higher weight = higher priority in categorization
{
    "category": "Critical Platform Issues",
    "weight": 1.5  # 50% higher priority
}
```

### Deactivate Categories:
```python
# Temporarily disable without deleting
kb.add_knowledge_base_entries([{
    "category": "Old Category",
    "is_active": False
}])
```

### Bulk Updates:
```python
# Replace entire knowledge base
kb.update_knowledge_base_from_data(new_entries)
```

## 🚨 Best Practices

### Keyword Selection:
- Use **specific phrases** for higher accuracy
- Include **common variations** and **synonyms**
- Test with **real ticket examples**
- **Avoid overlapping** keywords between categories

### Weight Tuning:
- Start with **weight = 1.0** for all categories
- Increase weight for **high-priority** categories
- Use **1.1-1.5** for important categories
- Use **0.8-0.9** for less important categories

### Testing:
- **Test new categories** with sample tickets
- **Monitor categorization** accuracy over time
- **Update keywords** based on real ticket patterns
- **Review team distribution** regularly

## 🎉 Benefits

✅ **No file management** - Everything in database  
✅ **Real-time updates** - Changes apply immediately  
✅ **Persistent storage** - Survives system restarts  
✅ **API integration** - Programmatic updates  
✅ **Automatic categorization** - Works with any ticket source  
✅ **Scalable** - Handle thousands of categories  
✅ **Audit trail** - Track changes over time  

Your knowledge base system is now fully database-driven and ready for production use! 🚀