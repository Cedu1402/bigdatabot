FROM docker.elastic.co/kibana/kibana:8.15.5

# Switch to root user to ensure we can change permissions
USER root

# Copy the setup script into the container
COPY ./kibana_user_setup.sh /usr/local/bin/kibana_user_setup.sh

# Set the correct permissions
RUN chmod +x /usr/local/bin/kibana_user_setup.sh

USER kibana

# Execute the setup script and then start the Kibana container
CMD ["/bin/sh", "-c", "/usr/local/bin/kibana_user_setup.sh && /bin/tini -- /usr/local/bin/kibana"]