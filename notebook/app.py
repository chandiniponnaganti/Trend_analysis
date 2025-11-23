# app.py — YouTube Trending Dashboard (Streamlit)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from io import StringIO

# === CONFIG ===
DATA_PATH = r"H:\excel_c\yt_trnd_analysis\output\youtube_cleaned.csv"   # <- your cleaned CSV

st.set_page_config(page_title="YouTube Trending — Dashboard", layout="wide", initial_sidebar_state="expanded")

# === DATA LOADER ===
@st.cache_data(show_spinner=False)
def load_data(path):
    df = pd.read_csv(path, low_memory=False, parse_dates=['publish_date','trending_date'])
    # ensure columns exist and basic fixes
    if 'trending_days' not in df.columns:
        df['trending_days'] = df.groupby('video_id')['trending_date'].transform(
            lambda x: x.dropna().nunique()
        ).fillna(0).astype(int)
    # enforce sentiment_label if missing
    if 'sentiment_label' not in df.columns:
        df['title_sentiment'] = 0.0
        df['sentiment_label'] = 'neutral'
    # coerce numeric columns (safe)
    for col in ['views','likes','dislikes','comment_count']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0
    # ensure publish_date/trending_date are datetimes (already parsed above, but safe)
    if 'publish_date' in df.columns:
        df['publish_date'] = pd.to_datetime(df['publish_date'], errors='coerce')
    else:
        df['publish_date'] = pd.NaT
    if 'trending_date' in df.columns:
        df['trending_date'] = pd.to_datetime(df['trending_date'], errors='coerce')
    else:
        df['trending_date'] = pd.NaT

    return df

df = load_data(DATA_PATH)

# === SIDEBAR (filters) ===
st.sidebar.header("Filters")

# date defaults for date_input must be date objects (not Timestamp)
min_pub = df['publish_date'].min()
max_pub = df['publish_date'].max()
# fallback to today if missing
if pd.isna(min_pub):
    min_pub = pd.Timestamp.now()
if pd.isna(max_pub):
    max_pub = pd.Timestamp.now()

min_date = min_pub.date()
max_date = max_pub.date()

date_range = st.sidebar.date_input("Publish date range", value=(min_date, max_date))

# country and category lists
countries = ["All"] + sorted(df['publish_country'].dropna().unique().tolist()) if 'publish_country' in df.columns else ["All"]
country = st.sidebar.selectbox("Country", countries)

cats = ["All"] + sorted(df['category_id'].dropna().astype(str).unique().tolist()) if 'category_id' in df.columns else ["All"]
category = st.sidebar.selectbox("Category ID", cats)

# compute safe max_views for slider
if 'views' in df.columns:
    max_views_val = df['views'].fillna(0).max()
    if pd.isna(max_views_val):
        max_views_val = 0
    try:
        max_views = int(max_views_val)
    except Exception:
        max_views = 0
else:
    max_views = 0

min_views = st.sidebar.slider("Minimum views", min_value=0, max_value=max_views, value=0, step=1000)

search = st.sidebar.text_input("Search title / channel")

# === APPLY FILTERS ===
df_view = df.copy()

# date filter (date_range can be a single date or tuple)
try:
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start = pd.to_datetime(date_range[0])
        end = pd.to_datetime(date_range[1])
    else:
        start = pd.to_datetime(date_range)
        end = start
    # include entire day for end
    end = end + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    df_view = df_view[(df_view['publish_date'] >= start) & (df_view['publish_date'] <= end)]
except Exception:
    # if anything fails, just skip date filtering
    pass

if country != "All":
    if 'publish_country' in df_view.columns:
        df_view = df_view[df_view['publish_country'] == country]

if category != "All":
    if 'category_id' in df_view.columns:
        df_view = df_view[df_view['category_id'].astype(str) == category]

# min views filter (views already coerced to int in loader)
if 'views' in df_view.columns:
    df_view = df_view[df_view['views'].fillna(0) >= int(min_views)]

if search:
    q = str(search).lower()
    mask_title = df_view['title'].str.contains(q, na=False, case=False) if 'title' in df_view.columns else False
    mask_channel = df_view['channel_title'].str.contains(q, na=False, case=False) if 'channel_title' in df_view.columns else False
    df_view = df_view[mask_title | mask_channel]

# === HEADER KPIs ===
st.title("YouTube Trending — Quick Dashboard")

# safe KPI values when df_view is empty
total_videos = int(len(df_view))
unique_channels = int(df_view['channel_title'].nunique()) if 'channel_title' in df_view.columns and not df_view.empty else 0
avg_trending_days = f"{df_view['trending_days'].mean():.1f}" if not df_view['trending_days'].dropna().empty else "0.0"
top_country = "N/A"
if 'publish_country' in df_view.columns and not df_view['publish_country'].dropna().empty:
    try:
        top_country = df_view['publish_country'].mode().iloc[0]
    except Exception:
        top_country = df_view['publish_country'].dropna().iloc[0] if not df_view['publish_country'].dropna().empty else "N/A"

dominant_sentiment = "N/A"
if 'sentiment_label' in df_view.columns and not df_view['sentiment_label'].dropna().empty:
    try:
        dominant_sentiment = df_view['sentiment_label'].mode().iloc[0]
    except Exception:
        dominant_sentiment = df_view['sentiment_label'].dropna().iloc[0]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total videos (rows)", total_videos)
col2.metric("Unique channels", unique_channels)
col3.metric("Avg trending days", avg_trending_days)
col4.metric("Top country", top_country)
col5.metric("Dominant sentiment", dominant_sentiment)

st.markdown("---")

# === LAYOUT: Top charts row ===
left_col, center_col, right_col = st.columns((1.2,1.5,1))

# A) Top categories by avg views (interactive)
with left_col:
    st.subheader("Top categories (avg views)")
    if 'category_id' in df_view.columns and not df_view.empty:
        top_cat = df_view.groupby('category_id', as_index=False)['views'].mean().sort_values('views', ascending=False).head(10)
        fig_cat = px.bar(top_cat, x='views', y='category_id', orientation='h',
                         labels={'views':'Avg views','category_id':'Category ID'}, title="")
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No category data to show.")

# B) Trending volume over time
with center_col:
    st.subheader("Trending videos over time (publish_date)")
    if not df_view.empty and not df_view['publish_date'].dropna().empty:
        ts = df_view.groupby(pd.Grouper(key='publish_date', freq='W'))['video_id'].nunique().reset_index(name='count')
        fig_ts = px.line(ts, x='publish_date', y='count', markers=True, title="")
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.info("No time-series data to show for selected filters.")

# C) Country counts
with right_col:
    st.subheader("Trending videos by country")
    if 'publish_country' in df_view.columns and not df_view.empty:
        country_counts = df_view['publish_country'].value_counts().reset_index()
        country_counts.columns = ['country','count']
        fig_c = px.bar(country_counts.head(10), x='count', y='country', orientation='h', title="")
        st.plotly_chart(fig_c, use_container_width=True)
    else:
        st.info("No country data to show.")

st.markdown("---")

# === MIDDLE ROW ===
s1, s2 = st.columns((1,1))

# Sentiment donut + distribution
with s1:
    st.subheader("Sentiment breakdown")
    if 'sentiment_label' in df_view.columns and not df_view.empty:
        counts = df_view['sentiment_label'].value_counts().reindex(['positive','neutral','negative']).fillna(0)
        fig_pie = px.pie(names=counts.index, values=counts.values, title="", hole=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No sentiment data to show.")

# Trending days histogram
with s2:
    st.subheader("Trending days distribution")
    if not df_view.empty and 'trending_days' in df_view.columns:
        fig_hist = px.histogram(df_view, x='trending_days', nbins=20, title="")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No trending days data to show.")

st.markdown("---")

# === BOTTOM: Scatter, table & download ===
st.subheader("Views vs Trending Days (hover to see title/channel)")
if not df_view.empty:
    fig_scatter = px.scatter(df_view, x='trending_days', y='views',
                             hover_data=[c for c in ['title','channel_title','publish_date'] if c in df_view.columns],
                             title="")
    # use log scale for y if there are positive values
    try:
        fig_scatter.update_yaxes(type='log')
    except Exception:
        pass
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("No points to plot for selected filters.")

st.markdown("### Top videos (filtered)")
table_cols = ['title','channel_title','publish_date','publish_country','category_id','views','likes','dislikes','comment_count','trending_days','sentiment_label']
table_cols = [c for c in table_cols if c in df_view.columns]
if not df_view.empty and table_cols:
    df_table = df_view[table_cols].sort_values('views', ascending=False).reset_index(drop=True)
    st.dataframe(df_table.head(200), use_container_width=True)

    # Download filtered data
    csv = df_table.to_csv(index=False)
    st.download_button("Download filtered CSV", csv, file_name="youtube_filtered.csv", mime="text/csv")
else:
    st.info("No table data to show for selected filters.")

st.markdown("---")
st.caption("Tip: use the filters on the left to drill into specific countries, categories, date ranges or search titles.")
