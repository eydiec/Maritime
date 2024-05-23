# Marine Time
[Website](https://marine-time.online) |  [Demo Video](https://www.youtube.com/watch?v=6bKpNwKqo4E)
![Marine Time Architecture](readme-img/architechture.png)
## Overview
***
A comprehensive platform providing daily port information and detailed market trend analytics from international indexes. The platform features an animated map built with Leaflet to visualize data over a rolling 12-month period.

## Features

- **Port Information**: 
  - Daily port congestion updates, on-berth ships
  - International indexes: WCI, FBX, BDI (weekly updates)
  - Taiwan indexes: Taiwan Ship Stock Index, Taiwan Export Value Changes (weekly updates)
  - Monthly ports operation status
- **Ship Industry Analytics**: Analyze detailed market trends from various international indexes.
- **Animated Map**: Visualize data trends over 12 months using a dynamic map.

## Technologies Used

- **Frontend**: Leaflet for interactive map visualization
- **Backend**: AWS Lambda, Flask, Docker
- **Data Storage**: Amazon S3, InfluxDB
- **Monitoring**: AWS CloudWatch, Prometheus, Telegraf

## Data Pipeline

- **Data Source**:
  - Maritime Port Bureau - Ports Operation Status <span style="font-size: smaller; color: gray;">(update frequency: daily, monthly)</span>
  - Drewry - World Container Index (WCI) <span style="font-size: smaller; color: gray;">(update frequency: weekly)</span>
  - Freightos - Freightos Baltic Index (FBX) <span style="font-size: smaller; color: gray;">(update frequency: weekly)</span>
  - Baltic Exchange - Baltic Dry Index (BDI) <span style="font-size: smaller; color: gray;">(update frequency: weekly)</span>
  - Taiwan Stock Exchange - Shipping Industry Index <span style="font-size: smaller; color: gray;">(update frequency: weekly)</span>
  - Ministry of Finance - Taiwan Export Value <span style="font-size: smaller; color: gray;">(update frequency: weekly)</span>
- **ETL**:
   - **Extract**: AWS Lambda (cron-based schedule + Selenium)
   - **Load**: Amazon S3
  - **Transform**: event-triggered AWS Lambda (Python) to write transformed data into InfluxDB. 
  

## Web Server

- **API Deployment**:
  - Deployed RESTful API using Flask on EC2 instances.
- **Load Balancing and Scaling**:
  - Utilized an Application Load Balancer (ALB) to distribute incoming traffic.
  - Implemented an Auto Scaling Group (ASG) to adjust the number of EC2 instances based on CPU utilization, ensuring scalability and preventing server overload.

## Monitoring

- **Real-Time Monitoring**:
  - Implemented real-time monitoring solutions using AWS CloudWatch, Prometheus, and Telegraf to ensure the system's performance and reliability by monitoring the server and database.
  ![monitor1](readme-img/monitor1.png)
  ![monitor2](readme-img/monitor2.png)
- **Data Integrity Checks**:
  - Conducted monthly data integrity checks by querying data from S3 and InfluxDB to ensure accuracy and consistency.

## Contact
Eydie Cheng

