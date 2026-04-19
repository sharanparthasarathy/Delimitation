# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# Set page configuration
st.set_page_config(
    page_title="Seat Allocation Model: India",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# DATA
# ------------------------------
@st.cache_data
def load_data():
    data = {
        "State": [
            "Uttar Pradesh", "Maharashtra", "Bihar", "West Bengal", "Madhya Pradesh",
            "Tamil Nadu", "Rajasthan", "Karnataka", "Gujarat", "Andhra Pradesh",
            "Odisha", "Telangana", "Kerala", "Jharkhand", "Assam",
            "Punjab", "Chhattisgarh", "Haryana", "Delhi", "Jammu & Kashmir"
        ],
        "Population_crores": [
            23.98, 12.44, 12.41, 9.13, 8.53,
            7.72, 7.85, 6.75, 6.80, 5.45,
            4.63, 3.74, 3.56, 3.59, 3.56,
            3.12, 2.94, 2.81, 1.98, 1.36
        ],
        "GDP_lakh_crore": [
            18.0, 32.0, 7.5, 12.5, 13.0,
            22.5, 12.0, 20.5, 21.0, 12.0,
            8.0, 12.5, 10.0, 5.5, 5.0,
            6.0, 5.0, 8.5, 11.0, 2.5
        ],
        "Current_Seats": [
            80, 48, 40, 42, 29,
            39, 25, 28, 26, 25,
            21, 17, 20, 14, 14,
            13, 11, 10, 7, 5
        ]
    }
    df = pd.DataFrame(data)
    # Normalize names for mapping
    return df

df_raw = load_data()

# Helper functions for allocation
def allocate_population_based(df, total_seats):
    total_pop = df["Population_crores"].sum()
    seats = (df["Population_crores"] / total_pop) * total_seats
    seats = seats.round().astype(int)
    # Adjust to match total_seats exactly
    diff = total_seats - seats.sum()
    if diff != 0:
        idx = seats.sub(seats.min()).nlargest(abs(diff)).index
        seats[idx] += np.sign(diff)
    return seats

def allocate_gdp_based(df, total_seats):
    total_gdp = df["GDP_lakh_crore"].sum()
    seats = (df["GDP_lakh_crore"] / total_gdp) * total_seats
    seats = seats.round().astype(int)
    diff = total_seats - seats.sum()
    if diff != 0:
        idx = seats.sub(seats.min()).nlargest(abs(diff)).index
        seats[idx] += np.sign(diff)
    return seats

def allocate_hybrid(df, total_seats, weight_pop):
    weight_gdp = 1 - weight_pop
    pop_share = df["Population_crores"] / df["Population_crores"].sum()
    gdp_share = df["GDP_lakh_crore"] / df["GDP_lakh_crore"].sum()
    hybrid_share = weight_pop * pop_share + weight_gdp * gdp_share
    seats = hybrid_share * total_seats
    seats = seats.round().astype(int)
    diff = total_seats - seats.sum()
    if diff != 0:
        idx = seats.sub(seats.min()).nlargest(abs(diff)).index
        seats[idx] += np.sign(diff)
    return seats

# Fairness metric: Gini-like index (0=perfect equality, 1=max inequality)
def fairness_index(seats, population):
    representation = seats / population
    representation = representation / representation.mean()
    # Simplified variance-based inequality measure
    gini = np.abs(representation - 1).mean()
    return min(gini, 1.0)

# ------------------------------
# SIDEBAR CONTROLS
# ------------------------------
st.sidebar.title("⚙️ Allocation Parameters")
model_choice = st.sidebar.selectbox(
    "Select Allocation Model",
    ["Population-based", "GDP-based", "Hybrid (Weighted)"]
)

total_seats = st.sidebar.slider(
    "Total Number of Lok Sabha Seats",
    min_value=100, max_value=1000, value=543, step=10
)

hybrid_weight = 0.5
if model_choice == "Hybrid (Weighted)":
    hybrid_weight = st.sidebar.slider(
        "Weight on Population (GDP weight = 1 - this)",
        min_value=0.0, max_value=1.0, value=0.7, step=0.05
    )

# Scenario simulation section
st.sidebar.markdown("---")
st.sidebar.subheader("📈 Scenario Simulation")
sim_state = st.sidebar.selectbox("Select state to modify", df_raw["State"])
pop_growth = st.sidebar.number_input(f"Population growth for {sim_state} (%)", min_value=-30.0, max_value=50.0, value=0.0, step=2.0)
gdp_growth = st.sidebar.number_input(f"GDP growth for {sim_state} (%)", min_value=-30.0, max_value=100.0, value=0.0, step=5.0)

# Apply scenario changes
df = df_raw.copy()
idx = df[df["State"] == sim_state].index[0]
df.loc[idx, "Population_crores"] *= (1 + pop_growth/100)
df.loc[idx, "GDP_lakh_crore"] *= (1 + gdp_growth/100)

# Compute allocations based on model
if model_choice == "Population-based":
    seats = allocate_population_based(df, total_seats)
    model_name = "Population-based Allocation"
elif model_choice == "GDP-based":
    seats = allocate_gdp_based(df, total_seats)
    model_name = "GDP-based Allocation"
else:
    seats = allocate_hybrid(df, total_seats, hybrid_weight)
    model_name = f"Hybrid Allocation (Pop Weight = {hybrid_weight:.2f})"

df["Allocated_Seats"] = seats
df["Current_Seats"] = df_raw["Current_Seats"]
df["Seat_Change"] = df["Allocated_Seats"] - df["Current_Seats"]

# ------------------------------
# MAIN PAGE
# ------------------------------
st.title("🏛️ India Parliamentary Seat Allocation: Population vs GDP Models")
st.markdown("""
This interactive tool compares different models of seat allocation in India's Lok Sabha. 
Explore the trade-offs between **demographic representation (one person, one vote)** and 
**economic performance (GDP-based allocation)**.
""")

# Key metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Seats", total_seats)
with col2:
    st.metric("Population (Total, Cr)", f"{df['Population_crores'].sum():.1f}")
with col3:
    st.metric("GDP (Total, Lakh Cr)", f"{df['GDP_lakh_crore'].sum():.1f}")
with col4:
    # Fairness index for current vs allocated
    current_rep = df["Current_Seats"] / df["Population_crores"]
    allocated_rep = df["Allocated_Seats"] / df["Population_crores"]
    fairness_current = fairness_index(df["Current_Seats"], df["Population_crores"])
    fairness_alloc = fairness_index(df["Allocated_Seats"], df["Population_crores"])
    st.metric("Fairness Index (lower=more equal)", f"{fairness_alloc:.3f}", delta=f"{fairness_alloc - fairness_current:.3f}")

# ------------------------------
# VISUALIZATIONS
# ------------------------------
st.subheader(f"📊 Seat Allocation Comparison: {model_name}")

# Bar chart comparing current vs allocated
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=df["State"], y=df["Current_Seats"], name="Current Seats", marker_color='steelblue'))
fig_bar.add_trace(go.Bar(x=df["State"], y=df["Allocated_Seats"], name=f"{model_name}", marker_color='coral'))
fig_bar.update_layout(barmode='group', xaxis_tickangle=-45, height=500, title="Seats per State")
st.plotly_chart(fig_bar, use_container_width=True)

# Two columns for pie charts
col_left, col_right = st.columns(2)
with col_left:
    fig_pie_current = px.pie(df, values="Current_Seats", names="State", title="Current Seat Share", hole=0.3)
    st.plotly_chart(fig_pie_current, use_container_width=True)
with col_right:
    fig_pie_alloc = px.pie(df, values="Allocated_Seats", names="State", title=f"{model_name} Seat Share", hole=0.3)
    st.plotly_chart(fig_pie_alloc, use_container_width=True)

# Comparison: gainers and losers
df_gainers = df.nlargest(5, "Seat_Change")[["State", "Seat_Change", "Current_Seats", "Allocated_Seats"]]
df_losers = df.nsmallest(5, "Seat_Change")[["State", "Seat_Change", "Current_Seats", "Allocated_Seats"]]

st.subheader("📈 Top 5 Gainers & Losers")
col_gain, col_loss = st.columns(2)
with col_gain:
    st.markdown("**🏆 Gainers (more seats)**")
    st.dataframe(df_gainers.style.format({"Seat_Change": "{:+.0f}"}), use_container_width=True)
with col_loss:
    st.markdown("**📉 Losers (fewer seats)**")
    st.dataframe(df_losers.style.format({"Seat_Change": "{:+.0f}"}), use_container_width=True)

# ------------------------------
# INSIGHTS PANEL
# ------------------------------
st.subheader("💡 Key Insights")
insights = []
if model_choice == "GDP-based":
    gainer = df.loc[df["Seat_Change"].idxmax(), "State"]
    loser = df.loc[df["Seat_Change"].idxmin(), "State"]
    insights.append(f"🔹 **{gainer}** gains the most seats under GDP-based allocation (+{df['Seat_Change'].max():.0f}).")
    insights.append(f"🔹 **{loser}** loses the most seats ({df['Seat_Change'].min():.0f}).")
    insights.append("🔹 GDP-based model rewards economically productive states like Maharashtra, Tamil Nadu, Gujarat.")
    insights.append("🔹 High-population but lower-GDP states (Bihar, UP) see significant seat reductions.")
elif model_choice == "Population-based":
    gainer = df.loc[df["Seat_Change"].idxmax(), "State"]
    insights.append(f"🔹 Population-based model closely follows current allocation (minimal changes).")
    insights.append(f"🔹 **{gainer}** would gain slightly if total seats increased.")
    insights.append("🔹 This model upholds 'one person, one vote' principle strictly.")
else:
    gainer = df.loc[df["Seat_Change"].idxmax(), "State"]
    insights.append(f"🔹 Hybrid model (pop weight={hybrid_weight:.2f}) balances population and economic output.")
    insights.append(f"🔹 **{gainer}** benefits from hybrid weighting.")
    if hybrid_weight > 0.7:
        insights.append("🔹 Higher population weight keeps representation closer to democratic ideals.")
    else:
        insights.append("🔹 Lower population weight favors economically stronger states.")

for ins in insights[:4]:
    st.markdown(ins)

# ------------------------------
# ETHICAL & POLITICAL ANALYSIS
# ------------------------------
with st.expander("📜 Ethical & Political Analysis: Population vs GDP-based Allocation"):
    st.markdown("""
    **The Democratic Principle: One Person, One Vote**  
    - Population-based allocation is the global norm for democratic legislatures.  
    - It ensures every citizen's vote carries equal weight, regardless of economic contribution.  
    - This prevents marginalization of poorer regions.

    **Arguments for GDP-based Allocation**  
    ✅ Rewards states for economic productivity and good governance.  
    ✅ Could incentivize development-oriented policies.  
    ✅ Reflects changing economic realities (e.g., high-growth states contribute more to national treasury).  

    **Arguments Against GDP-based Allocation**  
    ❌ Violates equal representation – a citizen in a poor state gets less voice.  
    ❌ Risks creating an economic elite class dominating parliament.  
    ❌ Could worsen regional inequality and political instability.  

    **India’s Delimitation Context**  
    - The Constitution freezes seat allocation until 2026 to encourage population control.  
    - Southern states with better economic and demographic indicators fear losing seats to northern states.  
    - A hybrid model (population + GDP) is occasionally proposed as a compromise.  

    *This tool is for educational exploration – no model is inherently right or wrong; each reflects different values.*
    """)

# ------------------------------
# DOWNLOAD RESULTS
# ------------------------------
csv = df[["State", "Population_crores", "GDP_lakh_crore", "Current_Seats", "Allocated_Seats", "Seat_Change"]].copy()
csv.columns = ["State", "Population (Cr)", "GDP (Lakh Cr)", "Current Seats", "Allocated Seats", "Change"]
csv_str = csv.to_csv(index=False)
st.download_button(
    label="📥 Download Results as CSV",
    data=csv_str,
    file_name=f"seat_allocation_{model_name.replace(' ', '_')}.csv",
    mime="text/csv"
)

# ------------------------------
# FOOTNOTE
# ------------------------------
st.caption("Note: Seat allocation uses proportional rounding to match total seats exactly. GDP and population data are illustrative based on recent estimates. Scenario simulation modifies the selected state's metrics in real-time.")
