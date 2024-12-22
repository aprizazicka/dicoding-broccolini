import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import matplotlib.ticker as mticker

sns.set(style='dark')

# Functions to process the data
def create_daily_sharing_df(df):
    daily_sharing_df = df.resample(rule='D', on='dteday').agg({"cnt": "sum"}).reset_index()
    daily_sharing_df.rename(columns={"cnt": "sharing_count"}, inplace=True)
    return daily_sharing_df

def create_sum_sharing_bike_df(df):
    sum_sharing_bike_df = df_cleaned.groupby(['yr', 'mnth']).agg({'cnt': 'sum'}).reset_index()
    sum_sharing_bike_df.rename(columns={"cnt": "sharing_count"}, inplace=True)
    return sum_sharing_bike_df

def create_sum_sharing_year_df(df):
    sum_sharing_year_df = df.groupby("yr").cnt.sum().sort_values(ascending=False).reset_index()
    sum_sharing_year_df.rename(columns={"cnt": "sharing_count"}, inplace=True)
    return sum_sharing_year_df

def create_season_df(df):
    season_df = df.groupby("season").cnt.sum().reset_index()
    season_df.rename(columns={"cnt": "sharing_count"}, inplace=True)
    season_df = season_df.sort_values(by="sharing_count", ascending=False).reset_index(drop=True)
    return season_df

def create_weather_df(df):
    weather_df = df.groupby("weathersit").cnt.sum().reset_index()
    weather_df.rename(columns={"cnt": "sharing_count"}, inplace=True)
    weather_df = weather_df.sort_values(by="sharing_count", ascending=False).reset_index(drop=True)
    return weather_df

def create_customer_df(df):
    customer_df = df[['casual', 'registered']].sum().reset_index()
    customer_df.columns = ['User Type', 'Total Count']
    return customer_df

def create_hour_df(df):
    hour_df=df_cleaned.groupby(by="hr").agg({"cnt": "sum"}).reset_index()
    return hour_df

# Load data
df_cleaned = pd.read_csv("df_cleaned.csv")
df_cleaned["dteday"] = pd.to_datetime(df_cleaned["dteday"])

# Sort and reset index for clean processing
df_cleaned.sort_values(by="dteday", inplace=True)
df_cleaned.reset_index(drop=True, inplace=True)

# Get min and max dates for filtering
min_date = df_cleaned["dteday"].min()
max_date = df_cleaned["dteday"].max()

# Sidebar for date range selection
with st.sidebar:
    st.image("bike-sharing-logos.png") 
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

# Filter data based on date input
main_df = df_cleaned[(df_cleaned["dteday"] >= start_date) & 
                     (df_cleaned["dteday"] <= end_date)]

# Create required DataFrames
daily_sharing_df = create_daily_sharing_df(main_df)
sum_sharing_year_df = create_sum_sharing_year_df(main_df)
sum_sharing_bike_df = create_sum_sharing_bike_df(main_df)
season_df = create_season_df(main_df)
weather_df = create_weather_df(main_df)
customer_df = create_customer_df(main_df)
sum_sharing_hour_df = create_hour_df(main_df)

# Streamlit header
st.header('Bike Sharing Dashboard 🚲')

col1, col2 = st.columns(2)

# Total Daily Sharing Metric
with col1:
    total_daily_sharing = daily_sharing_df.sharing_count.sum()
    st.metric("Total Penyewa", value=f"{total_daily_sharing:,}")

# Menemukan nilai maksimum
with col2:
    max_row = sum_sharing_hour_df.loc[sum_sharing_hour_df["cnt"].idxmax()]
    max_hour = int(max_row["hr"])  # Convert to int for better readability
    max_value = int(max_row["cnt"])  # Convert to int for better readability
# Streamlit metric untuk menampilkan jam dengan jumlah penyewaan maksimum
    st.metric(
    label="Jam dengan Penyewaan Maksimum",
    value=f"{max_hour}:00",
    delta=f"{max_value:,} Penyewaan")

# Daily Sharing Plot
st.header("Jumlah Penyewaan Sepeda per Bulan Berdasarkan Tahun")

# Creating a line plot
fig, ax = plt.subplots(figsize=(12, 6))
for year in sum_sharing_bike_df['yr'].unique():
    data_year = sum_sharing_bike_df[sum_sharing_bike_df['yr'] == year]
    ax.plot(data_year['mnth'], data_year['sharing_count'], marker='o', label=f"Tahun {2011 + year}")

ax.set_title("Jumlah Penyewaan Sepeda per Bulan Berdasarkan Tahun", fontsize=14)
ax.set_xlabel("Bulan (mnth)", fontsize=12)
ax.set_ylabel("Total Penyewaan Sepeda (sharing_count)", fontsize=12)
ax.set_xticks(range(1, 13))
ax.set_xticklabels([f"Bulan {i}" for i in range(1, 13)])
ax.legend(title="Tahun", fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.6)
st.pyplot(fig)

# Total Sharing Count by Year
st.subheader("Total Jumlah Penyewa Pper Tahun")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=sum_sharing_year_df, x="yr", y="sharing_count", palette="Blues_d", ax=ax)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Total Penyewa", fontsize=12)
ax.set_title("Total Penyewa per Tahun", fontsize=14)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
st.pyplot(fig)

# Best Season and Weather
st.subheader("Jumlah Penyewaan Berdasarkan Season dan Weather")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))

sns.barplot(x="sharing_count", y="season", data=season_df, palette="Blues_r", ax=ax[0])
ax[0].set_title("Season Terbaik", fontsize=14)
ax[0].set_xlabel("Jumlah Penyewa", fontsize=12)

sns.barplot(x="sharing_count", y="weathersit", data=weather_df, palette="Blues_r", ax=ax[1])
ax[1].set_title("Weather Terbaik", fontsize=14)
ax[1].set_xlabel("Jumlah Penyewa", fontsize=12)
ax[1].yaxis.tick_right()
st.pyplot(fig)

# Streamlit header
st.subheader("Perbandingan Penyewa Casual dan Registered")

# Create a bar plot with casual and registered customer
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=customer_df, x="User Type", y="Total Count", palette="Blues_d", ax=ax)

# Add title and labels
ax.set_title("Casual and Registered User Count", fontsize=16)
ax.set_ylabel("Total Count", fontsize=12)
ax.set_xlabel("User Type", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
st.pyplot(fig)

# Membuat line chart
st.subheader("Total Penyewaan Sepeda Berdasarkan Jam")
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(
    data=sum_sharing_hour_df,
    x="hr",
    y="cnt",
    marker="o",
    linewidth=2,
    label="Jumlah Penyewaan",
    color="#9694FF",
    ax=ax
)

# Menambahkan judul dan label
ax.set_title("Total Penyewaan Sepeda Berdasarkan Jam", fontsize=14)
ax.set_xlabel("Jam (hr)", fontsize=12)
ax.set_ylabel("Total Penyewaan Sepeda (cnt)", fontsize=12)
ax.set_xticks(range(0, 24))
ax.set_xticklabels([f"{i}" for i in range(0, 24)])  # Label jam
ax.legend(fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.7)
st.pyplot(fig)

# Footer
st.caption('Copyright (c) Dicoding 2024 - Apriza Zicka Rizquina')
