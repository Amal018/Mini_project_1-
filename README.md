# Mini_project_1: IMDB_Data_Scrap
IMDb 2024 Movie Dashboard

This mini project is a data visualization dashboard built using Streamlit. It allows you to explore and analyze IMDb movie data from 2024 across various genres such as Action, Adventure, Animation, Biography, and Crime.

Objective:
- Build an interactive dashboard using Streamlit
- Clean and preprocess real-world movie data
- Visualize key metrics like ratings, vote counts, durations, and genre-wise distributions
- Provide filtering options for users to explore data based on their preferences

Features:
- Visual tabs showing:
  - Top 10 movies by rating and vote count
  - Genre distribution bar chart
  - Average movie duration by genre
  - Average vote count per genre
  - Histogram of rating distribution
  - Top-rated movie in each genre
  - Pie chart showing vote distribution among genres
  - Duration extremes (shortest and longest movies)
  - Heatmap of average ratings by genre
  - Scatter plot showing the relationship between ratings and vote counts

- Filter section with:
  - Genre selection
  - Minimum rating slider
  - Minimum vote count slider
  - Duration filter (under 2 hrs, 2–3 hrs, over 3 hrs)

Files Included:
- Multiple CSV files for different genres (e.g., imdb_action_movies_2024.csv)
- app.py – Streamlit dashboard script
- data_view.py – Python script to load and print cleaned data
- README.md – Project documentation

How to Run:
1. Clone this repository and navigate into the folder:
   git clone https://github.com/your-username/imdb-2024-dashboard.git

2. Install required packages:
   pip install streamlit pandas matplotlib seaborn plotly

3. Start the Streamlit app:
   streamlit run app.py

4. (Optional) View the dataset directly in terminal:
   python data_view.py

Data Columns:
- Movie Title
- Genre
- Rating
- Vote Count
- Duration (in minutes)

Note:
Ensure that all the CSV files are present in the correct paths as specified in the code.

License:
This is a simple educational project. You may use or modify it freely.
