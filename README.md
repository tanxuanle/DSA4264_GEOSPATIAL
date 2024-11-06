# DSA4264 Geospatial Project

This project focuses on geospatial data analysis to identify and optimize public transportation routes. Follow the instructions below to set up the project and run the necessary analysis.

## Setup Instructions

### 1. Create a Data Directory
- Inside the project root directory, create an empty folder called `data`.
- Download the dataset from [Google Drive](https://drive.google.com/drive/folders/1hhqKJhRUdCg1Lh-ODvrJPe6umx-dGW7o?usp=drive_link) and save it into the `data` folder.

### 2. Configure Environment Variables
- Create an `.env` file in the project root directory.
- Store your **LTA API key** and **OneMap API key** in the `.env` file:
  
  ```plaintext
  LTA_API_KEY=your_lta_api_key_here
  OneMap_api_key=your_onemap_api_key_here
### 3. Generate Required Datasets
- Open and run `datasets.ipynb` to obtain all necessary datasets for the analysis.
  - Ensure that all cells execute successfully to avoid missing data.

### 4. Run the Analysis
- Open and run `Analysis.ipynb` to perform the data analysis.
  - This notebook contains all steps to analyze and visualize the transportation route data.

### 5. Generate the Dashboard  
- Open and run `dashboard.ipynb` to prepare the dashboard data.
- In the terminal, run the following command to launch the dashboard:
  
  ```bash
  streamlit run dashboard.py

---

Ensure all dependencies are installed in the virtual environment before running the notebooks. 
