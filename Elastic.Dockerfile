FROM docker.elastic.co/kibana/kibana:8.10.2

# Copy the setup script into the container
COPY ./kibana_user_setup.sh /usr/local/bin/kibana_user_setup.sh

# Set the correct permissions
RUN chmod +x /usr/local/bin/kibana_user_setup.sh

# Execute the setup script and then start the Kibana container
CMD ["/bin/sh", "-c", "/usr/local/bin/kibana_user_setup.sh && /usr/local/bin/docker-entrypoint.sh eswrapper"]
