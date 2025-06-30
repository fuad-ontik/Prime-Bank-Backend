#!/bin/bash
echo "🚀 Starting Flask app for testing..."
python3 app/main.py &

# Wait for the server to start
sleep 5

BASE_URL="http://localhost:8080"

# List of endpoints to test
declare -a ENDPOINTS=(
  "/" 
  "/api/dashboard"
  "/api/action-items"
  "/api/action-items/123"  # dummy post_id
  "/api/ai-overview"
  "/api/ai-overview/complaints"
  "/api/ai-overview/inquiries"
  "/api/ai-overview/praise"
  "/api/ai-overview/suggestions"
  "/api/bank-mentions"
  "/api/kpi"
  "/api/geolocation"
  "/api/scraping-status"
  "/api/sentiment-analysis"
  "/api/sentiment-analysis/emotions"
  "/api/sentiment-analysis/categories"
  "/api/sentiment-analysis/sentiments"
  "/api/sentiment-analysis/top-posts"
  "/api/summary"
  "/api/search?q=test"
  "/api/dashboard-ai-overview"
  "/api/full-data/posts/1"      # <-- Add this line
  "/api/full-data/comments/1"   # <-- Add this line
  "/api/full-data/1"
)

# Function to test each endpoint
test_endpoint() {
  URL="$1"
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$URL")

  if [ "$STATUS" -eq 200 ]; then
    echo "✅ $URL passed (HTTP $STATUS)"
  else
    echo "❌ $URL failed (HTTP $STATUS)"
  fi
}

# Loop through and test each endpoint
echo "🔍 Testing endpoints..."
for ep in "${ENDPOINTS[@]}"; do
  test_endpoint "$ep"
done

# Cleanup
kill %1
