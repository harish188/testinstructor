# 🚀 Vercel Deployment Guide

## Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/harish188/testinstructor)

## Manual Deployment Steps

### 1. Fork/Clone Repository
```bash
git clone https://github.com/harish188/testinstructor.git
cd testinstructor
```

### 2. Deploy to Vercel

**Option A: Using Vercel CLI**
```bash
npm i -g vercel
vercel --prod
```

**Option B: Using Vercel Dashboard**
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import from GitHub: `harish188/testinstructor`
4. Configure environment variables (see below)
5. Deploy!

### 3. Environment Variables

Set these in your Vercel project settings:

```env
# Zoho Desk API
ZOHO_CLIENT_ID=your_zoho_client_id
ZOHO_CLIENT_SECRET=your_zoho_client_secret
ZOHO_REFRESH_TOKEN=your_zoho_refresh_token
ZOHO_ORGANIZATION_ID=your_org_id

# ClickUp API
CLICKUP_API_TOKEN=your_clickup_api_token
CLICKUP_TEAM_ID=your_team_id

# ClickUp List IDs
LEARNING_PORTAL_LIST_ID=list_id_1
FEATURE_FLAGS_LIST_ID=list_id_2
CONTENT_ACCESS_LIST_ID=list_id_3
PORTAL_ACCESS_LIST_ID=list_id_4
CONTENT_BUNDLE_LIST_ID=list_id_5
QUIZ_ISSUES_LIST_ID=list_id_6
UNITS_UNLOCK_LIST_ID=list_id_7
INSTRUCTOR_LIST_ID=list_id_8
GROOMING_CHECK_LIST_ID=list_id_9

# App Config
DATABASE_URL=sqlite:///./automation.db
LOG_LEVEL=INFO
SYNC_INTERVAL_HOURS=1
MAX_RETRIES=3
```

## 🎯 Expected Deployment URL

Your app will be available at:
`https://your-project-name.vercel.app`

## 🔧 Features Available

- ✅ Web Dashboard
- ✅ API Endpoints
- ✅ Ticket Categorization
- ✅ Real-time Sync
- ✅ Knowledge Base Management

## 📊 Test Your Deployment

1. Visit your Vercel URL
2. Click "Fetch Tickets" (Preview Mode)
3. Verify categorization works
4. Test API endpoints at `/docs`

## 🛠️ Troubleshooting

**Database Issues:**
- Vercel uses serverless functions
- Database resets on each deployment
- Consider using external database for production

**Environment Variables:**
- Set all required variables in Vercel dashboard
- Check logs in Vercel Functions tab

**API Limits:**
- Vercel has execution time limits (10s for Hobby plan)
- Consider upgrading for production use