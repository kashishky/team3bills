# Team 3 - Congressional Bills Data Project

This repository contains our full workflow for collecting, cleaning, and exploring congressional bill data from the 118th session.

## Overview

1. **Raw Scraping (`scrape.py`)**  
   - We used Python’s `requests` and `BeautifulSoup` libraries to pull data from a public website that tracks U.S. congressional bills.
   - The script outputs a CSV (`congress_118_bills.csv`) with the raw data, including bill numbers, titles, sponsors, committees, cosponsors, vote info, and more.

2. **Preprocessing (`preprocessing.ipynb`)**  
   - This notebook merges multiple cleaning steps (equivalent to the old `baseclean.py`, `Program1 step4.py`, and `PJ1_Clark.ipynb`).
   - It reads the raw `congress_118_bills.csv`, applies data cleansing, manages missing values, drops low-variance columns, label-encodes categorical features as needed, etc.
   - The output is `final_congress_bills_data.csv`, a dataset used for further analysis and modeling.

3. **EDA & Feature Engineering (`eda_featureeng.ipynb`)**  
   - This notebook takes the final cleaned dataset and explores it:
     - Summary statistics & distributions
     - Advanced visualizations (e.g., bar charts, histograms, parallel coordinates, etc.)
     - Feature engineering steps such as PCA, K-means clustering, sponsor/committee analysis, and more.

## Background on Scraping
We scraped our data from a government website that displays details about bills in Congress (e.g., sponsors, cosponsors, committees, voting info). The `scrape.py` script systematically checks bill pages for a range of bill prefixes (`hr`, `s`, `hres`, `sres`, `hjres`, `sjres`) and tries to parse each one.  

### Key Points:
- We rely on HTML structure to extract each bill’s metadata, sponsor info, committees, and any available votes.  
- We carefully handle missing or irregular data (not every bill has a recorded vote, not every sponsor is available, etc.).

## File Descriptions

- **`scrape.py`**: Contains the code used for collecting data from the public government site. It outputs `congress_118_bills.csv` after finishing.  
- **`congress_118_bills.csv`**: The raw scraped data. This is our starting point for preprocessing.  
- **`preprocessing.ipynb`**:
  - Loads `congress_118_bills.csv` and performs data cleaning.
  - Fixes formats for dates, vote results, subject columns, and more.
  - Drops or transforms columns with near-zero variance.
  - Encodes categorical features if needed.
  - Outputs the **`final_congress_bills_data.csv`** file.  
- **`final_congress_bills_data.csv`**: The fully processed dataset, used for modeling/analysis.  
- **`eda_featureeng.ipynb`**:
  - Reads the **`final_congress_bills_data.csv`**.
  - Performs in-depth EDA and advanced feature engineering steps (PCA, clustering, visualization, etc.).
  - Provides advanced insights and can be used as an input for ML models.

## How to Run

1. **Clone or download** this repo.  
2. **Install dependencies** (e.g., `pip install requests beautifulsoup4 pandas matplotlib seaborn scikit-learn`) if you don’t already have them.  
3. **Scraping** (optional if you just want to see final data):
   1. Run `python scrape.py`.
   2. This creates `congress_118_bills.csv`.  
4. **Preprocessing**:  
   1. Open and run all cells in **`preprocessing.ipynb`**.  
   2. This notebook loads `congress_118_bills.csv`, cleans and transforms data, and saves **`final_congress_bills_data.csv`**.  
5. **EDA & Feature Engineering**:  
   1. Open **`eda_featureeng.ipynb`** and run the cells.  
   2. This will produce visualizations, summary stats, PCA/clustering results, and more.  
