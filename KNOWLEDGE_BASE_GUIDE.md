# 📚 Knowledge Base Enhanced System Guide

## 🎯 Overview

The system now uses a comprehensive knowledge base with 18 categories and 5 teams, based on your reference knowledge base. You can upload CSV files to update categorization rules in real-time.

## 📊 Categories & Team Mappings

| **Category** | **Team** | **Description** |
|-------------|----------|-----------------|
| Platform Issues | Product/Tech | Technical platform infrastructure issues |
| Facilities | Facilities | Physical equipment and venue issues |
| Session Timing Issues | Curriculum/Content | Session scheduling and timing problems |
| Tech QA Report Issue | Product/Tech | Quality assurance and technical reports |
| Other On-Ground Issues | Facilities | Physical/logistical issues |
| Student Portal | Product/Tech | Student portal specific issues |
| Scheduling Issue | Curriculum/Content | General scheduling problems |
| Session Handling Issues | Instructor | Session conduct and management |
| Learning Portal Issues | Product/Tech | General portal access issues |
| Feature Flags / Roles Adding | Product/Tech | User roles and permissions |
| Content Access | Curriculum/Content | Learning content accessibility |
| Portal Access | Product/Tech | General portal login issues |
| Content Bundle | Curriculum/Content | Curriculum packages and bundles |
| Quiz Issues | Curriculum/Content | Assessments and evaluations |
| Instructor Categories Adding | Instructor | Instructor role management |
| Units Unlock | Curriculum/Content | Course progression issues |
| Data mismatching in lookers studio | DA Team | Analytics and reporting issues |

## 🎨 Team Color Coding

- 🔵 **Product/Tech** - Light blue background
- 🟢 **Curriculum/Content** - Light green background
- 🟠 **Instructor** - Light orange background
- 🟣 **Facilities** - Light purple background
- 🟡 **DA Team** - Light yellow background

## 📁 CSV Knowledge Base Format

### Required Columns:
```csv
category,team,keywords,description
Platform Issues,Product/Tech,"platform,system,technical,bug,error,crash,server,database,api,integration","Technical issues with the platform infrastructure"
Facilities,Facilities,"facilities,room,equipment,hardware,projector,wifi,internet,network,venue,location","Physical facilities and equipment issues"
```

### Upload Process:
1. **Prepare CSV** - Use the exact format above
2. **Click "Upload KB"** - Purple button in dashboard header
3. **Select File** - Choose your CSV file
4. **Review Current KB** - See existing categories in modal
5. **Upload & Update** - System updates categorization rules
6. **Auto Re-categorize** - Existing tickets are re-processed

## 🔍 Enhanced Categorization Logic

### Keyword Matching:
- **Multi-word keywords** get higher weight (15 points)
- **Single keywords** get medium weight (10 points)
- **Exact phrase matches** are prioritized
- **Case-insensitive** matching throughout

### Example Categorizations:
```
"Platform system crash" → Platform Issues (Product/Tech)
"Projector not working in Room 101" → Facilities (Facilities)
"Session timing delay" → Session Timing Issues (Curriculum/Content)
"QA testing report shows bugs" → Tech QA Report Issue (Product/Tech)
"Student portal login issues" → Student Portal (Product/Tech)
"Quiz assessment not calculating" → Quiz Issues (Curriculum/Content)
"Data mismatching in Looker Studio" → Data mismatching in lookers studio (DA Team)
```

## 🚀 How to Use

### 1. Start the System:
```bash
cd zoho-clickup-automation
source venv/bin/activate
python main.py server
```

### 2. Access Dashboard:
- Open: http://localhost:8000
- Enable Preview Mode (default)
- Click "Fetch Tickets" to load 10 sample tickets

### 3. Upload Knowledge Base:
- Click "Upload KB" button
- Select your CSV file with categories
- Review current knowledge base
- Click "Upload & Update"
- System automatically re-categorizes existing tickets

### 4. Filter and Manage:
- Use Category dropdown (18 options)
- Use Team dropdown (5 teams)
- Click team stat cards for quick filtering
- Edit categories manually if needed
- Select and sync to ClickUp

## 📊 Sample Data

The system includes 10 realistic sample tickets covering all major categories:

1. **Platform Issues** - System crashes and technical problems
2. **Facilities** - Equipment failures and venue issues
3. **Session Timing** - Scheduling delays and timing problems
4. **Tech QA** - Bug reports and quality issues
5. **Student Portal** - Student-specific access problems
6. **Session Handling** - Instructor management issues
7. **Quiz Issues** - Assessment and scoring problems
8. **Data Analytics** - Looker Studio reporting issues
9. **Content Bundle** - Curriculum access problems
10. **Instructor Categories** - Role and permission requests

## 🔧 Customization

### Adding New Categories:
1. Update your CSV file with new categories
2. Include relevant keywords for each category
3. Assign appropriate team
4. Upload via dashboard

### Modifying Keywords:
1. Edit the keywords column in CSV
2. Use comma-separated values
3. Include both single words and phrases
4. Upload to update matching rules

### Team Assignments:
- Ensure team names match exactly
- Use consistent naming (e.g., "Product/Tech", "Curriculum/Content")
- Dashboard will automatically update team stats

## 🎯 Best Practices

### CSV Preparation:
- Use descriptive keywords that appear in actual tickets
- Include variations and synonyms
- Test with sample data before uploading
- Keep descriptions concise but informative

### Categorization Accuracy:
- Review auto-categorized tickets before syncing
- Use "Edit Category" for manual adjustments
- Monitor categorization patterns over time
- Update knowledge base based on new ticket types

### Team Management:
- Ensure ClickUp list IDs are configured for each category
- Map categories to appropriate teams in your organization
- Use filters to review team workloads
- Balance ticket distribution across teams

## 🚨 Troubleshooting

### Upload Issues:
- Ensure CSV format is correct
- Check for special characters in keywords
- Verify team names match exactly
- Review file encoding (use UTF-8)

### Categorization Problems:
- Check keyword relevance to actual ticket content
- Add more specific keywords for better matching
- Review and adjust category descriptions
- Test with sample tickets before production

### Performance:
- Large knowledge bases may slow categorization
- Optimize keywords for common ticket patterns
- Remove redundant or unused categories
- Monitor system performance with real data

## 📈 Analytics

The dashboard provides real-time insights:
- **Total tickets** processed
- **Team distribution** with counts
- **Category breakdown** in filters
- **Success rates** for each team
- **Processing history** with timestamps

This enhanced system provides professional-grade ticket categorization with full customization capabilities through CSV knowledge base management! 🎉