🌤️ Weather Data Analysis and Visualization Project
Project Title

Parallel Weather Data Analysis and Visualization using MPI and Streamlit

Project Description

This project collects, analyzes, and visualizes weather data for multiple cities using parallel computing (MPI) and an interactive Streamlit dashboard. The system processes:

Historical Weather Data (Past 7 Days)

Current Weather Data (with Date and Time)

Forecast Weather Data (Next 7 Days)

All weather information is stored in a single combined CSV file (all_cities_weather.csv) and visualized using charts and tables.

Objectives

Use MPI for parallel weather data collection

Analyze weather data efficiently for multiple cities

Store all data in one structured CSV file

Visualize historical, current, and forecast weather trends

Provide interactive filtering and comparison

Technologies Used

C Programming

MPI (Message Passing Interface)

Weather API

libcurl

json-c

Python

Pandas

Streamlit

Plotly

Weather Parameters Analyzed

Temperature (°C)

Humidity (%)

Wind Speed (kph)

Weather Condition

Precipitation (mm)

Feels Like Temperature (°C)

Visibility (km)

UV Index

Pressure (mb)

Project Folder Structure

Weather_Data_Analysis/
│
├── pw.c # MPI-based weather data collection code
├── all_cities_weather.csv # Combined CSV for all cities
├── visualize_weather.py # Streamlit visualization code
├── README.md # Project documentation

CSV File Description

File Name: all_cities_weather.csv

History and Forecast rows contain date only

Current rows contain date with time

All cities and all weather types are stored in a single CSV

System Requirements

Linux Operating System

MPI (MPICH or OpenMPI)

Python 3.8 or above

Installation Steps
Install MPI and Required Libraries

sudo apt update
sudo apt install mpich libcurl4-openssl-dev libjson-c-dev

Install Python Packages

pip install pandas streamlit plotly

How to Run the Project
Step 1: Navigate to Project Folder

cd Weather_Data_Analysis

Step 2: Compile MPI Program

mpicc pw.c -o pw -lcurl -ljson-c

Step 3: Run MPI Program

mpirun -np 4 ./pw

This will generate the file: all_cities_weather.csv

Step 4: Run Streamlit Dashboard

streamlit run visualize_weather.py

Open the browser and visit: http://localhost:8501

Features of the Dashboard

City selection

Weather type selection (History / Current / Forecast / All)

Line charts for:

Temperature

Humidity

Wind Speed

UV Index

Bar chart for precipitation

Pie chart for weather condition distribution

Current weather displayed with date and time

CSV download option for filtered data

Advantages of the System

Faster processing using parallel computing

Supports multiple cities

Easy and interactive visualization

Single CSV for simplified data management

Real-time and future weather insights

Conclusion

This project demonstrates how MPI-based parallel processing combined with Streamlit visualization can efficiently analyze and present weather data. It provides clear insights into past trends, current conditions, and future forecasts using a single integrated system.
