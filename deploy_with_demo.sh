#!/bin/bash

echo "🚀 Deploying Zoho-ClickUp Integration with Demo Data"
echo "===================================================="

echo "🔧 Setting up demo environment variables..."

# Set demo environment variables for Firebase Functions
firebase functions:config:set \
  zoho.client_id="demo_zoho_client_12345" \
  zoho.client_secret="demo_zoho_secret_67890" \
  zoho.refresh_token="demo_zoho_refresh_abcdef" \
  zoho.organization_id="demo_org_123456789" \
  clickup.api_token="demo_clickup_token_xyz789" \
  clickup.team_id="demo_team_456" \
  clickup.platform_list_id="demo_platform_list_123" \
  clickup.facilities_list_id="demo_facilities_list_456" \
  clickup.session_list_id="demo_session_list_789" \
  clickup.qa_list_id="demo_qa_list_101" \
  clickup.student_list_id="demo_student_list_202" \
  clickup.instructor_list_id="demo_instructor_list_303"

echo "✅ Demo environment variables set!"
echo ""

echo "🚀 Deploying to Firebase..."
firebase deploy

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "🌐 Your live demo app:"
echo "   Dashboard: https://zoho-clickup-automation.web.app"
echo "   API: https://us-central1-zoho-clickup-automation.cloudfunctions.net/api"
echo ""
echo "🎯 Demo Features:"
echo "   ✅ Mock Zoho tickets (6 realistic examples)"
echo "   ✅ Intelligent categorization"
echo "   ✅ Simulated ClickUp task creation"
echo "   ✅ Full sync workflow demonstration"
echo "   ✅ Real-time API testing"
echo ""
echo "📝 Note: This runs in demo mode with mock data."
echo "   To use real APIs, replace demo credentials with actual ones."