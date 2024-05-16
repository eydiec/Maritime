# Use base image
FROM umihico/aws-lambda-selenium-python:3.12.2-selenium4.20.0-chrome124.0.6367.91

# Install Python packages
RUN pip install selenium python-dotenv influxdb-client

# Selenium script
COPY main.py ./

# Set the CMD to your handler (could be the file name)

CMD [ "main.handler" ]