ouTube Trending Video Analysis
Interactive Dashboard using Streamlit | Data Cleaning | Sentiment Analysis

This project analyzes YouTube Trending Videos using end-to-end data preprocessing, exploratory analysis, sentiment scoring, and an interactive Streamlit Dashboard for visualization.

🚀 Project Features
🔹 1. Data Cleaning

Removed duplicates


Parsed dates correctly

Cleaned text columns (titles, tags, channels)

Normalized boolean columns

🔹 2. Exploratory Data Analysis

Top trending categories

Likes vs views relationship

Trending duration per video

Region-wise insights (if applicable)

🔹 3. Sentiment Analysis

Using VADER (NLTK):

Generated compound sentiment score

Classified titles into:

Positive

Neutral

Negative

🔹 4. Interactive Streamlit Dashboard

Users can explore:

📈 Category-wise views

🔥 Trending duration

😀 Sentiment distribution

🔍 Search videos by title

🏆 Top videos by popularity metrics

🧰 Tech Stack
Layer	Tools
Language	Python
Data Processing	Pandas, NumPy
Visualization	Matplotlib, Seaborn, Altair
Sentiment Analysis	NLTK, VADER
Dashboard	Streamlit
Deployment	GitHub + Streamlit Cloud
📂 Project Structure
📦 Trend_analysis
 ┣ 📂 data
 ┃ ┗ youtube.csv
 ┣ 📂 notebook
 ┃ ┗ 01_data_cleaning.ipynb
 ┣ 📄 dashboard.py
 ┣ 📄 requirements.txt
 ┣ 📄 README.md

▶️ Run the Dashboard Locally
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Run Streamlit
streamlit run dashboard.py

🌐 Deploying to Streamlit Cloud

Push project to GitHub

Visit: https://share.streamlit.io

Select the GitHub repo

Set the entry file:

dashboard.py


Deploy 🚀

📊 Example Insights

Most Trending Category: Entertainment

Most Positive Titles: Music, Motivation, Vlogs

Negative Sentiments: News, Political content

Highest engagement: Comedy + Vlogs

🤝 Contributing

Feel free to fork this repo and submit a pull request for improvements.

📬 Contact

Chandini Ponnaganti
📧 chandiniponnaganti@gmail.com

🔗 GitHub: https://github.com/chandiniponnaganti
