# 🏛️ India Parliamentary Seat Allocation Model

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://delimitation-order.streamlit.app/)

An interactive data science tool that explores different models for allocating Lok Sabha seats to Indian states, comparing population-based, GDP-based, and hybrid allocation approaches.

## 🌐 Live Demo

Access the live application here: [https://delimitation-order.streamlit.app/](https://delimitation-order.streamlit.app/)

## 📋 Overview

This application visualizes and compares how different seat allocation models would impact parliamentary representation across Indian states. It allows users to:

- Compare **Population-based**, **GDP-based**, and **Hybrid** allocation models
- Adjust total number of Lok Sabha seats (100-1000)
- Simulate population and GDP growth scenarios for individual states
- Visualize seat distribution changes through interactive charts
- Analyze gainers and losers under different allocation models
- Download results for further analysis

## 🎯 Key Features

### Allocation Models
- **Population-based**: Strict "one person, one vote" principle
- **GDP-based**: Rewards economic productivity
- **Hybrid**: Weighted combination of population and GDP metrics

### Interactive Controls
- Adjustable total seat count (100-1000 seats)
- Customizable population/GDP weights for hybrid model
- Real-time scenario simulation for any state
- Population and GDP growth modifiers (-30% to +100%)

### Visualizations
- Comparative bar charts (Current vs. Allocated seats)
- Interactive pie charts with seat share distribution
- Top 5 gainers and losers analysis
- Fairness index metrics

### Data Features
- Real-time seat reallocation calculations
- CSV export functionality
- Ethical and political analysis section

## 📊 Data Sources

The application uses illustrative data for 28 Indian states including:
- Current Lok Sabha seat allocation (based on 2019 distribution)
- Population estimates (in crores)
- GDP figures (in lakh crores)

*Note: Data is for demonstration purposes and based on recent estimates.*

## 🛠️ Technology Stack

- **Frontend/UI**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly Express, Plotly Graph Objects
- **Hosting**: Streamlit Community Cloud

## 📁 Project Structure
