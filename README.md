# Zoho to ClickUp Automation System

A sophisticated automation agent that fetches tickets from Zoho Desk, intelligently categorizes them, and routes them to appropriate ClickUp lists with team assignments.

## Features

- 🔄 Automated ticket fetching from Zoho Desk
- 🧠 Smart categorization with ML-like rules
- 🎯 Team-based routing to ClickUp
- 📊 Real-time dashboard with analytics
- 🔍 Duplicate detection and merging
- 📝 Comprehensive logging and audit trail
- ⚡ Retry mechanisms and error handling
- 🕐 Scheduled and manual execution

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API credentials

# Run the application
python main.py
```

## Architecture

- **Backend**: FastAPI with async processing
- **Frontend**: Modern React dashboard
- **Database**: SQLite for logging and state
- **Scheduler**: APScheduler for automated runs
- **APIs**: Zoho Desk API, ClickUp API

## Team Mappings

| Category | Team | ClickUp List |
|----------|------|--------------|
| Learning Portal Issues | Product/Tech | `LEARNING_PORTAL_LIST_ID` |
| Feature Flags / Roles | Product/Tech | `FEATURE_FLAGS_LIST_ID` |
| Content Access | Product/Tech | `CONTENT_ACCESS_LIST_ID` |
| Portal Access | Product/Tech | `PORTAL_ACCESS_LIST_ID` |
| Content Bundle | Curriculum | `CONTENT_BUNDLE_LIST_ID` |
| Quiz Issues | Curriculum | `QUIZ_ISSUES_LIST_ID` |
| Units Unlock | Curriculum | `UNITS_UNLOCK_LIST_ID` |
| Instructor Categories | Instructor | `INSTRUCTOR_LIST_ID` |
| Grooming Check Issues | Instructor | `GROOMING_CHECK_LIST_ID` |