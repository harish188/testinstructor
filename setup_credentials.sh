#!/bin/bash

echo "🔧 Setting up Zoho-ClickUp Integration Credentials"
echo "=================================================="

echo "📝 Please enter your API credentials:"
echo ""

# Zoho credentials
read -p "Zoho Client ID: " ZOHO_CLIENT_ID
read -p "Zoho Client Secret: " ZOHO_CLIENT_SECRET
read -p "Zoho Refresh Token: " ZOHO_REFRESH_TOKEN
read -p "Zoho Organization ID: " ZOHO_ORG_ID

echo ""

# ClickUp credentials
read -p "ClickUp API Token: " CLICKUP_TOKEN
read -p "ClickUp Team ID: " CLICKUP_TEAM_ID

echo ""

# ClickUp List IDs
echo "📋 ClickUp List IDs for each category:"
read -p "Platform Issues List ID: " PLATFORM_LIST_ID
read -p "Facilities List ID: " FACILITIES_LIST_ID
read -p "Session Timing List ID: " SESSION_LIST_ID
read -p "QA Reports List ID: " QA_LIST_ID
read -p "Student Portal List ID: " STUDENT_LIST_ID
read -p "Instructor Issues List ID: " INSTRUCTOR_LIST_ID

echo ""
echo "🚀 Setting Firebase environment variables..."

# Set all environment variables
firebase functions:config:set \
  zoho.client_id="$ZOHO_CLIENT_ID" \
  zoho.client_secret="$ZOHO_CLIENT_SECRET" \
  zoho.refresh_token="$ZOHO_REFRESH_TOKEN" \
  zoho.organization_id="$ZOHO_ORG_ID" \
  clickup.api_token="$CLICKUP_TOKEN" \
  clickup.team_id="$CLICKUP_TEAM_ID" \
  clickup.platform_list_id="$PLATFORM_LIST_ID" \
  clickup.facilities_list_id="$FACILITIES_LIST_ID" \
  clickup.session_list_id="$SESSION_LIST_ID" \
  clickup.qa_list_id="$QA_LIST_ID" \
  clickup.student_list_id="$STUDENT_LIST_ID" \
  clickup.instructor_list_id="$INSTRUCTOR_LIST_ID"

echo ""
echo "✅ Configuration complete!"
echo ""
echo "🚀 Now deploying Cloud Functions..."
firebase deploy --only functions

echo ""
echo "🎉 Setup complete! Your Zoho-ClickUp integration is now live!"
echo "🌐 Dashboard: https://zoho-clickup-automation.web.app"