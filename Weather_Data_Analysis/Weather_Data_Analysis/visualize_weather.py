import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ============================
# App Configuration
# ============================
st.set_page_config(page_title="🌤️ Weather Data Analysis", layout="wide")

# ============================
# Load and Clean Data
# ============================
@st.cache_data
def load_data():
    df = pd.read_csv("all_cities_weather.csv")

    # Standardize column names
    df.columns = df.columns.str.strip().str.title()

    # Clean text values
    df = df.applymap(lambda x: x.strip().title() if isinstance(x, str) else x)

    # Convert Date column to datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Fill missing or invalid current dates with system time
    current_time = datetime.now()
    df.loc[(df["Type"].str.lower() == "current") & (df["Date"].isna()), "Date"] = current_time

    # Create display-friendly formatted date
    df["Display_Date"] = df["Date"].dt.strftime("%Y-%m-%d %H:%M")

    return df


df = load_data()

# ============================
# Title Section
# ============================
st.markdown(
    "<h1 style='text-align:center; color:#1E90FF; font-size:45px;'>🌤️ Weather Data Analysis Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h4 style='text-align:center; color:#555;'>Analyze Historical, Current, and Forecast Weather Data</h4>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ============================
# Filters
# ============================
col1, col2 = st.columns([1, 1])
with col1:
    selected_city = st.selectbox("🏙️ Select City", sorted(df["City"].unique()))
with col2:
    weather_types = ["History", "Forecast", "Current", "All Types"]
    selected_type = st.selectbox("🌦️ Select Weather Type", weather_types, index=2)

# ============================
# Filter Data
# ============================
filtered_df = df[df["City"].str.lower() == selected_city.lower()].copy()

if selected_type == "All Types":
    show_df = filtered_df
else:
    show_df = filtered_df[filtered_df["Type"].str.lower() == selected_type.lower()]

# ============================
# Display Data
# ============================
st.markdown(f"### 🌍 City: **{selected_city.title()}** — Weather Type: **{selected_type}**")

if show_df.empty:
    st.warning("⚠️ No data available for the selected filters.")
else:
    st.divider()
    st.subheader("Weather Snapshot")

    latest_row = show_df.sort_values("Date").iloc[-1]
    st.write(f"**Date:** {latest_row['Display_Date']}")

    # Display key metrics
    cols = st.columns(6)
    cols[0].metric("🌡️ Temp (°C)", f"{latest_row['Temp(C)']:.1f}")
    cols[1].metric("💧 Humidity (%)", f"{latest_row['Humidity(%)']:.0f}")
    cols[2].metric("🌬️ Wind (Kph)", f"{latest_row['Wind(Kph)']:.1f}")
    cols[3].metric("☀️ UV Index", f"{latest_row['Uv']:.1f}")
    cols[4].metric("🌧️ Precip (mm)", f"{latest_row['Precip(Mm)']:.1f}")
    cols[5].metric("🌈 Condition", latest_row['Condition'])

    st.divider()
    st.subheader("📋 Detailed Weather Data")

    # Show all available columns
    display_cols = [
        "City", "Type", "Display_Date", "Temp(C)", "Feelslike(°C)",
        "Humidity(%)", "Wind(Kph)", "Condition", "Precip(Mm)",
        "Visibility(Km)", "Uv", "Pressure(Mb)"
    ]
    existing_cols = [col for col in display_cols if col in show_df.columns]
    st.dataframe(show_df[existing_cols], width='stretch', height=400)

    # ============================
    # Grouped Multi-Chart Dashboard
    # ============================
    st.divider()
    st.subheader("📊 Weather Trends Overview")

    # Chart 1: Temperature & Feels Like
    st.markdown("#### 🌡️ Temperature & Feels Like")
    fig1 = go.Figure()
    if "Temp(C)" in show_df.columns:
        fig1.add_trace(go.Scatter(x=show_df["Date"], y=show_df["Temp(C)"],
                                  mode='lines+markers', name='Temp (°C)'))
    if "Feelslike(°C)" in show_df.columns:
        fig1.add_trace(go.Scatter(x=show_df["Date"], y=show_df["Feelslike(°C)"],
                                  mode='lines+markers', name='Feels Like (°C)'))
    fig1.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="°C")
    st.plotly_chart(fig1, width='stretch')

    # Chart 2: Humidity & Precipitation
    st.markdown("#### 💧 Humidity & Precipitation")
    fig2 = go.Figure()
    if "Humidity(%)" in show_df.columns:
        fig2.add_trace(go.Scatter(x=show_df["Date"], y=show_df["Humidity(%)"],
                                  mode='lines+markers', name='Humidity (%)'))
    if "Precip(Mm)" in show_df.columns:
        fig2.add_trace(go.Bar(x=show_df["Date"], y=show_df["Precip(Mm)"],
                              name='Precipitation (mm)', opacity=0.6))
    fig2.update_layout(barmode='overlay', template="plotly_dark",
                       xaxis_title="Date", yaxis_title="Value")
    st.plotly_chart(fig2, width='stretch')

    # Chart 3: Wind Speed & Visibility
    col3a, col3b = st.columns(2)
    with col3a:
        st.markdown("#### 🌬️ Wind Speed (Kph)")
        if "Wind(Kph)" in show_df.columns:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=show_df["Date"], y=show_df["Wind(Kph)"],
                                      mode='lines+markers', name='Wind (Kph)'))
            fig3.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Kph")
            st.plotly_chart(fig3, width='stretch')
    with col3b:
        st.markdown("#### 👁️ Visibility (Km)")
        if "Visibility(Km)" in show_df.columns:
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=show_df["Date"], y=show_df["Visibility(Km)"],
                                      mode='lines+markers', name='Visibility (Km)'))
            fig4.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Km")
            st.plotly_chart(fig4, width='stretch')

    # Chart 4: UV Index & Pressure
    col4a, col4b = st.columns(2)
    with col4a:
        st.markdown("#### ☀️ UV Index")
        if "Uv" in show_df.columns:
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(x=show_df["Date"], y=show_df["Uv"],
                                      mode='lines+markers', name='UV Index'))
            fig5.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Index")
            st.plotly_chart(fig5, width='stretch')
    with col4b:
        st.markdown("#### 📊 Pressure (Mb)")
        if "Pressure(Mb)" in show_df.columns:
            fig6 = go.Figure()
            fig6.add_trace(go.Scatter(x=show_df["Date"], y=show_df["Pressure(Mb)"],
                                      mode='lines+markers', name='Pressure (Mb)'))
            fig6.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Mb")
            st.plotly_chart(fig6, width='stretch')

    # ============================
    # Condition Distribution (Pie)
    # ============================
    st.divider()
    st.subheader("🌦️ Weather Condition Distribution")
    if selected_type == "All Types":
        col_a, col_b = st.columns(2)
        fig_cond = go.Figure(data=[go.Pie(labels=show_df["Condition"], hole=0.3)])
        fig_cond.update_layout(title=f"Weather Conditions - {selected_city.title()}", template="plotly_dark")
        col_a.plotly_chart(fig_cond, width='stretch')

        fig_type = go.Figure(data=[go.Pie(labels=filtered_df["Type"], hole=0.3)])
        fig_type.update_layout(title=f"Data Type Distribution - {selected_city.title()}", template="plotly_dark")
        col_b.plotly_chart(fig_type, width='stretch')
    else:
        fig_cond = go.Figure(data=[go.Pie(labels=show_df["Condition"], hole=0.3)])
        fig_cond.update_layout(title=f"Condition Distribution - {selected_city.title()} ({selected_type})",
                               template="plotly_dark")
        st.plotly_chart(fig_cond, width='stretch')

# ============================
# Footer
# ============================
st.markdown("---")
st.markdown("<p style='text-align:center;'> 🌦️ Weather Data Visualizer 🌦️ </p>", unsafe_allow_html=True)

