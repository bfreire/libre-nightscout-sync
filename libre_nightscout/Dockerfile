ARG BUILD_FROM
FROM $BUILD_FROM

# Install required packages
RUN apk add --no-cache python3 py3-pip

# Set up the app directory
WORKDIR /app

# Create data directory with correct permissions
RUN mkdir -p /data && \
    chown -R root:root /data

# Copy your application
COPY requirements.txt .
COPY libre_nightscout_sync.py .
COPY run.sh .

# Install Python requirements
RUN pip3 install -r requirements.txt

# Make run script executable
RUN chmod a+x run.sh

# Set proper permissions
RUN chmod -R 755 /app

WORKDIR /data

CMD [ "/app/run.sh" ] 