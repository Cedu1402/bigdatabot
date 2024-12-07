#!/bin/bash
set -e

echo "ELASTICSEARCH_PASSWORD_MAIN: $ELASTICSEARCH_PASSWORD_MAIN"
echo "KIBANA_SYSTEM_PASSWORD: $KIBANA_SYSTEM_PASSWORD"

# Wait for Elasticsearch to be ready
until curl -s -u elastic:$ELASTICSEARCH_PASSWORD_MAIN http://elasticsearch:9200; do
  echo "Waiting for Elasticsearch to start..."
  sleep 5
done

# Change the password for the kibana_system user
curl -X POST "http://elasticsearch:9200/_security/user/kibana_system/_password" \
  -H "Content-Type: application/json" \
  -u elastic:$ELASTICSEARCH_PASSWORD_MAIN \
  -d '{
    "password": "'"$KIBANA_SYSTEM_PASSWORD"'"
  }'

echo "Password for kibana_system user has been updated successfully."
