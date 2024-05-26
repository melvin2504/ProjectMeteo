# 🌤 Indoor/Outdoor Weather Monitor with M5stack IoT Device and Cloud Dashboard
<img src="images/mainimage1.jpg" alt="Description of the image" style="width: 100%;">
Welcome to our project repository ! This project involves implementing an indoor/outdoor weather monitor using M5stack IoT devices and sensors, integrated with a web dashboard deployed on the cloud. This solution provides real-time weather monitoring and forecasting, along with historical data visualization, all managed through Google Cloud services.

## 👥 Contributors
- Melvin Petracca (GitHub: @melvin2504) - Indoor monitoring and device interface.
- Laurent Sierro (GitHub: @Aztol) - Cloud dashboard and Google Cloud integration.

## 📑 Table of Contents
- [Project Overview](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#-project-overview)
- [Exciting Features](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#-exciting-features)
- [Hardware and Software Requirements](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#-hardware-and-software-requirements)
- [Setup and Deployment Instructions](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#-setup-and-deployment-instructions)
  - [Google Cloud Deployment Instructions](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#-google-cloud-deployment-instructions)
  - [Device Configuration](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#-device-configuration)
- [Project Structure](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#-project-structure)
- [Dashboard Overview](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#%EF%B8%8F-dashboard-overview)
- [3D Printing Your M5Stack Core2 Holder](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#%EF%B8%8F-3d-printing-your-m5stack-core2-holder)
- [Video Demonstration](https://github.com/melvin2504/ProjectMeteo/blob/main/README.md#-video-demonstration)

## 🚀 Project Overview
This project utilizes the M5stack Core2 IoT device along with various sensors to monitor both indoor and outdoor weather conditions. The data is displayed on the device interface and a cloud-based dashboard built with Streamlit. All data is stored in Google Cloud's BigQuery, allowing for both real-time and historical data analysis.

## ⭐ Exciting Features
- **Indoor Monitoring:** 🌡️ Temperature, humidity, air quality, and presence detection.
- **Outdoor Monitoring:** 🌦️ Current weather conditions and forecasts using OpenWeatherMap API.
- **Cloud Integration:** ☁️ Data storage and retrieval using Google BigQuery.
- **Alerts and Notifications:** 🔊 Text-to-speech announcements for weather conditions when you pass next to it and visual notifications when air quality is bad.
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

### 🌍 Google Cloud Deployment Instructions

Deploying the application on Google Cloud allows you to utilize powerful cloud-based services for handling data processing, storage, and web hosting. Follow these detailed steps to get your application running on Google Cloud.

#### Step 1: Set Up Google Cloud Project
1. **Create a Google Cloud Project**:
   - Visit the [Google Cloud Console](https://console.cloud.google.com/).
   - Click on "IAM & Admin" in the left menu and then "Create a Project".
   - Enter a project name and select a billing account if necessary. Click 'Create'.

2. **Enable APIs**:
   - In the search bar at the top of the Google Cloud Console, search for "BigQuery API" and "Text-to-Speech API".
   - Enable both APIs for your project.

3. **Create BigQuery Dataset**:
   - Navigate to the BigQuery service.
   - In the BigQuery console, click on your project name and select "Create Dataset".
   - Provide a dataset ID and set other configurations as needed, then click 'Create'.

#### Step 2: Obtain Google Cloud Credentials
1. **Create Service Account**:
   - Go to "IAM & Admin" > "Service accounts".
   - Click "Create Service Account", name it, and grant it project-level roles like BigQuery Admin, and Text-to-Speech User.
   - Click 'Create'.

2. **Create and Download Credentials**:
   - In the service accounts list, click on the newly created service account.
   - Go to "Keys" tab and click on "Add Key" > "Create new key".
   - Choose JSON and download the key file. This is your `google_credentials.json`. This will be usefull for a local use.

#### Step 3: Deploy Application Using Google Cloud Run
1. **Containerize Your Application**:
   - Set up environment variables for Google Cloud and OpenWeatherMap in config.py.
   - Ensure your project has a `Dockerfile` which includes all necessary instructions to build the image.
   - Build your container image using Google Cloud Build or your local machine.
     ```sh
     git clone https://github.com/melvin2504/ProjectMeteo.git
     cd ProjectMeteo
     cd FlaskApp
     docker build -t eu.gcr.io/your-project-id/flaskapp:latest .
     ```

3. **Push the Container to Container Registry**:
   - Tag your built image appropriately for Google Container Registry.
   - Use `gcloud` commands to push the image to Google Cloud. For example:
     ```sh
     gcloud auth configure-docker
     docker push eu.gcr.io/your-project-id/flaskapp
     ```

4. **Deploy to Cloud Run**:
   - Select your image from Container Registry, configure the service settings.
   - Click 'Create' to deploy. Cloud Run will provide a URL to access your deployed application.

#### Step 4: Accessing the Application
- Once deployed, access the application via the URL provided by Cloud Run. It will be the endpoint to use in your Micropython code for your M5Stack in order to use backend services.

By following these steps, you'll have a robust deployment of your weather monitoring application running on Google Cloud, leveraging its powerful services for scalability and performance.

#### Step 1: Deploy Dashboard Using Google Cloud Run
1. **Containerize Your Application**:
   - Set up endpoints variables in `streamlit_app.py`.
   - Ensure your project has a `Dockerfile` which includes all necessary instructions to build the image.
   - Build your container image using Google Cloud Build or your local machine.
     ```sh
     git clone https://github.com/melvin2504/ProjectMeteo.git
     cd ProjectMeteo
     cd StreamlitApp
     docker build -t eu.gcr.io/your-project-id/streamlit:latest .
     ```
2. **Push the Container to Container Registry**:
   - Tag your built image appropriately for Google Container Registry.
   - Use `gcloud` commands to push the image to Google Cloud. For example:
     ```sh
     gcloud auth configure-docker
     docker push eu.gcr.io/your-project-id/streamlit
     ```
3. **Deploy to Cloud Run**:
   - Select your image from Container Registry, configure the service settings.
   - Click 'Create' to deploy. Cloud Run will provide a URL to access your deployed application.

### 📱 Device Configuration
1. Connect the M5stack Core2 to [M5Flow](https://flow.m5stack.com/) and connect the sensors.
2. Customize the Micropython (`M5Stack/display.py`), change the Wi-Fi credentials, and the endpoints for your deployed service.
4. Upload the relevant code from M5Flow to the device.

## 🗂 Project Structure
### FlaskApp
- **main.py**: Entry point for the Flask application.
- **config.py**: Configuration file for API keys and other settings.
- **google_cloud_utils.py**: Functions for interacting with Google Cloud services.
- **openai_utils.py**: Functions for interacting with OpenAI services.
- **weather.py**: Functions for fetching and processing weather data.
- **requirements.txt**: List of required Python packages.
- **Dockerfile**: Instructions for building a Docker image of the application.
### Icons
- All the graphical elements needed for the interface of the M5Stack and Streamlit App. You will need to upload them through [M5Flow](https://flow.m5stack.com/) in order to store them in the Core2 memory.
### M5Stack
- Micropython code to upload on the device.
### StreamlitApp
- Python code of the streamlit interface.
### images
- Images of my personal M5Stack used for the readme.
### 3DStand
- STL file in order to 3D print the holder.

## 🌥️ Dashboard Overview

### Welcome Page

![Current Weather](/images/current_weather.PNG)

The welcome page of the dashboard, provides an overview of the current weather conditions and indoor data. It displays:
- The date and day of the week.
- A weather forecast for the upcoming days with icons representing different weather conditions.
- Current outdoor weather, including temperature and cloud conditions.
- Current indoor data, such as indoor temperature, humidity, Total Volatile Organic Compounds (TVOC) level, and equivalent CO2 (eCO2) level.

**Note:** For a better experience, use the dashboard in dark mode.


### Graphs Page

The graphs page contains several visual representations of weather data collected over time. Below are the graphs in the order they appear:

![Heatmap of Max Outdoor Humidity](/images/graphics_1.PNG)
The "Heatmap of Max Outdoor Humidity" shows the maximum outdoor humidity levels across different hours of the day for the past week.

![Indoor Temperature](/images/graphics_2.PNG)
This graph depicts the indoor temperature variations (minimum, average, and maximum) recorded every 3 hours over the last 7 days.

![Outdoor Temperature](/images/graphics_3.PNG)
Similar to the indoor temperature graph, this one shows the outdoor temperature variations (minimum, average, and maximum) recorded every 3 hours over the last 7 days.

![Indoor Conditions Over Time](/images/graphics_4.PNG)
The "Indoor Conditions Over Time" graph tracks the indoor humidity percentage, CO2 levels (in ppm), and TVOC levels (in ppb) over a specified period.

![Heatmap of Max Outdoor Temperature](/images/graphics_5.PNG)
Lastly, the "Heatmap of Max Outdoor Temperature" displays the maximum outdoor temperature across different hours of the day for the past week.

## 🖨️ 3D Printing Your M5Stack Core2 Holder
<br>
<div align="center">
  <img src="images/standfront.jpg" alt="Core2holder" width="300"/>
  <img src="images/standback.jpg" alt="Core2holder" width="300"/>
  <img src="images/standside.jpg" alt="Core2holder" width="300"/>
</div>
<br>
To enhance your experience with the M5Stack Core2, you have the option to print a custom 3D holder. This stand not only secures your device but also positions it for optimal interaction and visibility.

### Get the 3D Model
You can find a suitable 3D model for the M5Stack Core2 stand by visiting this [Cults3D page](https://cults3d.com/fr/mod%C3%A8le-3d/gadget/m5stack-core-stand). The page features a specifically designed stand that accommodates the M5Stack Core2 perfectly.

### Download the STL File
The STL file for the 3D model is available in `3DStand/STAND_M5STACK.stl`

### Printing Instructions
Once you have downloaded the STL file, you can use any standard 3D printer to create the holder. Make sure to adjust your printer settings according to the material you choose and the recommendations provided by the STL file’s creator. Optimal settings ensure the best fit and durability of the holder.

### Assembly
After printing, you can place your Core2 on the holder and attach the sensor to the back of the holder using double-sided adhesive tape. Additionally, there are two areas at the back where you can insert magnets to enhance the stability of your M5Stack. However, avoid using neodymium magnets! ⚠️ Neodymium magnets are extremely powerful and can interfere with electronic components, potentially damaging the circuitry of your device.

This custom holder is an excellent way to enhance the usability of your M5Stack Core2 device, making it easy to interact with and adding an extra layer of stability and protection.

## 🎥 Video Demonstration
- Check out our [YouTube video demonstration](https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUJcmljayByb2xs) to see the project in action!
