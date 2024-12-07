#!/bin/bash
set -e

# Wait for Elasticsearch to be ready
until curl -s http://elasticsearch:9200 -u elastic:$ELASTICSEARCH_PASSWORD; do
  echo "Waiting for Elasticsearch to start..."
  sleep 5
done

# Create Kibana system role
curl -X POST "http://elasticsearch:9200/_security/role/kibana_system" \
  -H "Content-Type: application/json" \
  -u elastic:$ELASTICSEARCH_PASSWORD_MAIN \
  -d '{
    "cluster": ["monitor"],
    "indices": [
      {
        "names": [".kibana*", "kibana_sample_data*"],
        "privileges": ["all"]
      }
    ]
  }'

# Create Kibana system user
curl -X POST "http://elasticsearch:9200/_security/user/kibana_system" \
  -H "Content-Type: application/json" \
  -u elastic:$ELASTICSEARCH_PASSWORD_MAIN \
  -d '{
    "password": "'$ELASTICSEARCH_PASSWORD'",
    "roles": ["kibana_system"],
    "full_name": "Kibana System User"
  }'

echo "Elasticsearch setup complete!"