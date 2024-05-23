# Marine Time
![Marine Time Architecture](<img width="832" alt="architechture" src="https://github.com/eydiec/Maritime/assets/137089509/dc1f353d-54fb-4c4a-b5be-68007fcef873">
)
## Overview
A comprehensive platform providing daily port information and detailed market trend analytics from international indexes. The platform features an animated map built with Leaflet to visualize data over a rolling 12-month period.

## Features
- **Port Information**: 
  - Daily port congestion updates, on-berth ships
  - International indexes: WCI, FBX, BDI (weekly updates)
  - Taiwan indexes: 台灣航運指數, Taiwan Export Value Changes (weekly updates)
  - Monthly port operation status
- **Market Trend Analytics**: Analyze detailed market trends from various international indexes.
- **Animated Map**: Visualize data trends over 12 months using a dynamic map.

## Technologies Used
- **Frontend**: Leaflet for interactive map visualization
- **Backend**: AWS Lambda, Flask, Docker
- **Data Storage**: Amazon S3, InfluxDB
- **Monitoring**: AWS CloudWatch, Prometheus, Telegraf

## Data Pipeline
1. **Data Collection**:
   - Utilized AWS Lambda with a cron-based schedule to automate daily, weekly, and monthly data collection.
   - Stored collected data in Amazon S3.

2. **Data Transformation**:
   - Implemented a second Lambda function triggered by events to handle data transformation.
   - Wrote transformed data into InfluxDB.
   - Processed over 250K data entries to ensure efficient time series data processing.

3. **Modularity and Scalability**:
   - Leveraged Docker to build Lambda image layers, enhancing the modularity and scalability of the data processing pipeline.

## Web Server
- **API Deployment**:
  - Deployed RESTful API using Flask on EC2 instances.
- **Load Balancing and Scaling**:
  - Utilized an Application Load Balancer (ALB) to distribute incoming traffic.
  - Implemented an Auto Scaling Group (ASG) to adjust the number of EC2 instances based on CPU utilization, ensuring scalability and preventing server overload.

## Monitoring
- **Real-Time Monitoring**:
  - Implemented real-time monitoring solutions using AWS CloudWatch, Prometheus, and Telegraf to ensure the system's performance and reliability by monitoring the server and database.
- **Data Integrity Checks**:
  - Conducted monthly data integrity checks by querying data from S3 and InfluxDB to ensure accuracy and consistency.

## Getting Started

