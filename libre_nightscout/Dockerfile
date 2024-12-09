ARG BUILD_FROM
FROM $BUILD_FROM

# Install required packages
RUN apk add --no-cache python3 py3-pip

# Copy your application
WORKDIR /app
COPY requirements.txt .
COPY libre_nightscout_sync.py .
COPY run.sh .

# Install Python requirements
RUN pip3 install -r requirements.txt

# Make run script executable
RUN chmod a+x run.sh

CMD [ "./run.sh" ] 