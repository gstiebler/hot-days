# Temperature Analysis Web Application 🌡️

This Streamlit web application provides an interactive platform for analyzing historical temperature data for any location worldwide. Users can input coordinates and a date range to fetch and visualize temperature distributions, identify trends in cold and hot days, and view summary statistics.

**✨ Now available online at: [https://hot-days.streamlit.app/](https://hot-days.streamlit.app/) ✨**

## 📊 Features

* **Interactive Location Input**: Specify latitude and longitude for precise location analysis.
* **Custom Date Range**: Select start and end dates to analyze temperature data for specific periods.
* **Temperature Distribution Analysis**:
  * Visualizes the number of days with minimum temperatures below various thresholds (Cold Days Distribution).
  * Visualizes the number of days with maximum temperatures above various thresholds (Hot Days Distribution).
* **Summary Statistics**: Displays key metrics such as:
  * Total days analyzed
  * Coldest and hottest days (min/max temperatures)
  * Warmest minimum and coolest maximum temperatures
  * Average minimum and maximum temperatures
  * Overall temperature range
* **Data Visualization**: Uses Plotly to generate interactive line charts for temperature distributions.
* **Raw Data Viewing**: Option to view the fetched temperature data in a tabular format.
* **Data Download**: Allows users to download the analyzed temperature data as a CSV file.
* **Popular Locations**: Quick select buttons for popular cities around the world.
* **User-Friendly Interface**: Built with Streamlit for an intuitive user experience.
* **Error Handling**: Provides feedback for invalid inputs or data fetching issues.

## 🌐 Data Source

This application utilizes the [Open-Meteo API](https://open-meteo.com/), a free and open-source weather API providing global historical weather data.

## 🚀 How to Use

1. **Set Location**:
   * Enter the latitude (between -90 and 90) and longitude (between -180 and 180) for the desired location.
   * Alternatively, click on one of the "Popular Locations" in the sidebar.
2. **Select Date Range**:
   * Choose a "Start Date" and "End Date" for the analysis period. The start date must be before the end date.
3. **Analyze Data**:
   * Click the "🔍 Analyze Temperature Data" button.
4. **Explore Results**:
   * View the location information (coordinates, elevation, timezone).
   * Examine the "Temperature Distribution Analysis" charts for minimum and maximum temperatures.
   * Review the "Temperature Summary" statistics.
   * Optionally, expand "📋 View Raw Temperature Data" to see the raw data table and download it as a CSV.

## 🛠️ Setup and Installation

To run this application locally, you'll need Python installed. Follow these steps:

1. **Clone the repository (if applicable) or download the `app.py` file.**

2. **Create a virtual environment (recommended)**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required Python packages**:
   The application uses the following main libraries:
   * `streamlit`
   * `openmeteo-requests`
   * `pandas`
   * `requests-cache`
   * `retry-requests`
   * `plotly`
   * `numpy`

   You can install them using `uv` (which utilizes the `pyproject.toml` and `uv.lock` files if present, or can install packages directly):

   ```bash
   uv pip install streamlit openmeteo-requests pandas requests-cache retry-requests plotly numpy
   ```

   Alternatively, if a `requirements.txt` file is provided:

   ```bash
   uv pip install -r requirements.txt
   ```

## ▶️ Running the Application

Once the setup is complete, you can run the Streamlit application using the following command in your terminal:

```bash
streamlit run app.py
```

This will typically open the application in your default web browser.

## 💻 Technologies Used

* **Python**: Core programming language.
* **Streamlit**: For building the interactive web application.
* **Open-Meteo API**: For fetching historical weather data.
* **Pandas**: For data manipulation and analysis.
* **NumPy**: For numerical operations.
* **Plotly Express**: For creating interactive charts.
* **requests-cache & retry-requests**: For efficient and resilient API requests.

---

Feel free to contribute to this project or suggest new features!
