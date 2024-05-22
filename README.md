# 🌤 Indoor/Outdoor Weather Monitor with M5stack IoT Device and Cloud Dashboard

Welcome to our project repository! This project involves implementing an indoor/outdoor weather monitor using M5stack IoT devices and sensors, integrated with a web dashboard deployed on the cloud. This solution provides real-time weather monitoring and forecasting, along with historical data visualization, all managed through Google Cloud services.

## 📑 Table of Contents
- [Project Overview](#project-overview)
- [Exciting Features](#exciting-features)
- [Hardware and Software Requirements](#hardware-and-software-requirements)
- [Setup and Deployment Instructions](#setup-and-deployment-instructions)
  - [1. Google Cloud Setup](#1-google-cloud-setup)
  - [2. Local Deployment](#2-local-deployment)
  - [3. Device Configuration](#3-device-configuration)
- [Project Structure](#project-structure)
- [Contributors](#contributors)
- [Video Demonstration](#video-demonstration)

## 🚀 Project Overview
This project utilizes the M5stack Core2 IoT device along with various sensors to monitor both indoor and outdoor weather conditions. The data is displayed on the device interface and a cloud-based dashboard built with Streamlit. All data is stored in Google Cloud's BigQuery, allowing for both real-time and historical data analysis.

## ⭐ Exciting Features
- **Indoor Monitoring:** 🌡️ Temperature, humidity, air quality, and presence detection.
- **Outdoor Monitoring:** 🌦️ Current weather conditions and forecasts using OpenWeatherMap API.
- **Cloud Integration:** ☁️ Data storage and retrieval using Google BigQuery.
- **Alerts and Notifications:** 🔊 Text-to-speech announcements for weather conditions and visual notifications when air quality is bad.
- **User Interfaces:** 💻 Local interface on the M5stack device and a cloud-based dashboard.
- **Historical Data Visualization:** 📊 Access and analyze past weather data on the Streamlit dashboard and on the M5Stack in a more simplistic way.

## 🛠 Hardware and Software Requirements
- **Hardware:**
  - **M5stack Core2 IoT Device:** A versatile and stackable IoT development kit. [More info](https://docs.m5stack.com/en/core/core2).
  - **ENVIII Sensor (Humidity & Temperature):** Measures indoor humidity and temperature. [Details here](https://shop.m5stack.com/products/env-iii-unit-with-temperature-humidity-air-pressure-sensor-sht30-qmp6988).
  - **Air Quality Sensor:** Monitors indoor air quality. [Further info](https://shop.m5stack.com/products/tvoc-eco2-gas-unit-sgp30).
  - **Motion Sensor:** Detects movement to trigger alerts or actions. [Learn more](https://shop.m5stack.com/products/pir-module).

<br>
<div align="center">
  <img src="https://shop.m5stack.com/cdn/shop/products/1_3f420584-fb2f-48c3-bd01-17f083de0880_1200x1200.jpg?v=1608513603" alt="Core2" width="200"/>
  <img src="https://shop.m5stack.com/cdn/shop/products/1_c0de294c-761b-45d0-9098-fe75effe7f49_1200x1200.jpg?v=1627863922" alt="Motion Sensor" width="200"/>
  <img src="https://shop.m5stack.com/cdn/shop/products/1_396ff532-f0ac-4eee-b102-cbc9afdd97c9_1200x1200.jpg?v=1598833693" alt="Air Sensor" width="200"/>
  <img src="https://shop.m5stack.com/cdn/shop/products/1_d5b646cb-fed3-4644-a881-937971cd87c3_1200x1200.jpg?v=1676450541" alt="Motion Sensor" width="200"/>
</div>
<br>

- **Software:**
  - Google Cloud Platform account
  - OpenWeatherMap API key
  - OpenAi API key for advice generation based on meteorological input
  - Python 3.8+
  - Required Python packages (see `requirements.txt`)

## 📦 Setup and Deployment Instructions

### 1. Google Cloud Setup
1. Create a Google Cloud project and enable the BigQuery and Text-to-Speech APIs.
2. Set up a BigQuery dataset and table for storing sensor and outdoor data.
3. Obtain the necessary credentials and save them as `google_credentials.json`.

### 2. Local Deployment
1. Clone this repository:
   ```sh
   git clone https://github.com/melvin2504/ProjectMeteo.git
   cd FlaskApp
2. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
3. Set up environment variables for Google Cloud and OpenWeatherMap in config.py.

### 3. Device Configuration
1. Connect the M5stack Core2 to [M5Flow](https://flow.m5stack.com/) and connect the sensors.
2. Customize the Micropython (`display.py`), change the Wi-Fi credentials, and the endpoints for your deployed service.
4. Upload the relevant code from M5Flow to the device.

## 🗂 Project Structure
- **main.py**: Entry point for the Flask application.
- **config.py**: Configuration file for API keys and other settings.
- **google_cloud_utils.py**: Functions for interacting with Google Cloud services.
- **openai_utils.py**: Functions for interacting with OpenAI services.
- **weather.py**: Functions for fetching and processing weather data.
- **requirements.txt**: List of required Python packages.
- **Dockerfile**: Instructions for building a Docker image of the application.

## 👥 Contributors
- Melvin Petracca (GitHub: @melvin2504) - Indoor monitoring and device interface.
- Laurent Sierro (GitHub: @Aztol) - Cloud dashboard and Google Cloud integration.

## 🎥 Video Demonstration
- Check out our [YouTube video demonstration](https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUJcmljayByb2xs) to see the project in action!
