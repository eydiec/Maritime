# Marine Time
[Website](https://marine-time.online) |  [Introdcution Video](https://www.youtube.com/watch?v=6bKpNwKqo4E)
## Overview

A platform providing daily port information and detailed market trend analytics from international indexes. The platform features an animated map built with Leaflet to visualize data over a rolling 12-month period.
## Objective
Marine Time aims to gather comprehensive information about the shipping industry, bringing together a wealth of data and insights in one platform. 
This website is a heartfelt tribute to my beloved grandpa, who was a captain throughout his whole life and became an angel during the development.
Through this endeavor, I honor his memory and his enduring influence on my life.

## Table of Contents

- [Overview](#overview)
- [Objective](#objective)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Demo](#demo)
- [Introduction Video](#introduction-video)
- [Architecture](#architecture)
  - [Component Specification](#component-specification)
- [Data Pipeline Details](#data-pipeline-details)
- [Web Server Details](#web-server-details)
- [Monitoring](#monitoring)
- [Deployment](#deployment)
- [Contact](#contact)



## Features

- **Port Information Visualization**: 
  - Daily port congestion and on-berth ships update
  - International indexes: WCI, FBX, BDI (weekly updates)
  - Taiwan indexes: Taiwan Ship Stock Index, Taiwan Export Value Changes (weekly updates)
  - Monthly ports operation status
- **Ship Industry Analytics**: Analyze detailed market trends from various international indexes.
- **Animated Map**: Visualize data trends over 12 months using a dynamic map.

## Technologies Used

- **Frontend**: Leaflet, Grafana, Matplotlib
- **Programming Languages**: Python, JavaScript
- **Framework**: Flask
- **Tools**: Docker, Selenium
- **Database**: InfluxDB
- **Monitoring**: AWS CloudWatch, Prometheus, Telegraf
- **Cloud Service (AWS)**: EC2, Lambda, ALB, ASG, CloudWatch, S3, Route53

## Demo

## Introduction Video
[Introdcution Video](https://www.youtube.com/watch?v=6bKpNwKqo4E)

## Architecture
![Marine Time Architecture](readme-img/architechture.png)
Here's a brief overview of Marine Time's architecture:
### Component Specification
- **InfluxDB**: CPU: 2 vCPUs, Memory: 4 GB
- **Grafana**: CPU: 1 vCPU, Memory: 2 GB
- **Python Application**: CPU: 1 vCPU, Memory: 2 GB
- **Prometheus**: CPU: 1 vCPU, Memory: 2 GB
- **Node Exporter**: CPU: 0.5 vCPU, Memory: 0.5 GB
- **Telegraf**: CPU: 0.5 vCPU, Memory: 0.5 GB


## Data Pipeline Details

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

## Web Server Details

- **API Deployment**:
  - Deployed RESTful API using Flask on EC2 instances
- **Load Balancing and Scaling**:
  - Application Load Balancer (ALB) to distribute incoming traffic
  - Auto Scaling Group (ASG) to adjust EC2 instances based on CPU utilization

## Monitoring

- **Real-Time Monitoring**:
  - Implemented real-time monitoring solutions using AWS CloudWatch, Prometheus, and Telegraf to ensure the system's performance and reliability by monitoring the server and database.
  ![monitor1](readme-img/monitor1.png)
  ![monitor2](readme-img/monitor2.png)
- **Data Integrity Checks**:
  - Conducted monthly data integrity checks by querying data from S3 and InfluxDB to ensure accuracy and consistency.

## Deployment


## Contact
[Eydie Cheng](mailto:eydie.cheng@gmail.com)

