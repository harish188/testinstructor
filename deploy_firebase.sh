#!/bin/bash

echo "🔥 Firebase Deployment Script"
echo "=============================="

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

echo "✅ Firebase CLI found"

# Check if user is logged in
if ! firebase projects:list &> /dev/null; then
    echo "🔐 Please login to Firebase..."
    firebase login
fi

echo "✅ Firebase authentication verified"

# Run tests
echo "🧪 Running setup tests..."
python3 test_firebase_setup.py

# Deploy
echo "🚀 Deploying to Firebase..."
firebase deploy

echo "🎉 Deployment complete!"
echo ""
echo "🌐 Your app is now live at:"
echo "   https://zoho-clickup-automation.web.app"
echo ""
echo "📊 Firebase Console:"
echo "   https://console.firebase.google.com/project/zoho-clickup-automation"