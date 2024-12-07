#!/bin/bash
set -e

echo "Waiting for Elasticsearch to be ready..."
while ! curl -k -s -u elastic:$ELASTICSEARCH_PASSWORD_MAIN http://elasticsearch:9200 >/dev/null; do
  sleep 5
  echo "Waiting for Elasticsearch to be ready..."
done

# Attempt to change password with detailed error handling
response=$(curl -k -s -w "%{http_code}" -X POST "http://elasticsearch:9200/_security/user/kibana_system/_password" \
  -H "Content-Type: application/json" \
  -u elastic:$ELASTICSEARCH_PASSWORD_MAIN \
  -d "{\"password\": \"$KIBANA_SYSTEM_PASSWORD\"}")

http_code=$(echo "$response" | tail -c 4)

if [ "$http_code" -eq 200 ]; then
  echo "Password for kibana_system user updated successfully."
else
  echo "Failed to update kibana_system password. HTTP Status: $http_code"
  echo "Response: $response"
  exit 1
fi