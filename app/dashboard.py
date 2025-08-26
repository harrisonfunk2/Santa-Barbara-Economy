import streamlit as st           
import pandas as pd             
from pathlib import Path     

st.set_page_config(
    page_title="Santa Barbara Economic Trends",
    page_icon="📈",
    layout="wide",
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@st.cache_data(show_spinner=False)
def load_merged() -> pd.DataFrame:
    """
    Read housing/income/population CSVs, normalize their time keys to 'year' (int),
    merge them on 'year', and compute some handy derived columns.
    """
    housing = pd.read_csv(DATA_DIR / "housing_prices.csv")
    income = pd.read_csv(DATA_DIR / "median_income.csv")
    population = pd.read_csv(DATA_DIR / "population.csv")

    housing["year"] = pd.to_datetime(housing["date"]).dt.year
    housing = housing.drop(columns=["date"]) 

    income["year"] = income["year"].astype(int)
    population["year"] = population["year"].astype(int)

    merged = (
        housing.merge(income, on="year", how="inner")
               .merge(population, on="year", how="inner")
               .sort_values("year")
               .reset_index(drop=True)
    )

    def to_index(s: pd.Series) -> pd.Series:
        return (s / s.iloc[0]) * 100

    merged["HPI_idx"]    = to_index(merged["housing_price_index"])
    merged["Income_idx"] = to_index(merged["median_income"])
    merged["Pop_idx"]    = to_index(merged["population"])

    merged["HPI_yoy_pct"]    = merged["housing_price_index"].pct_change() * 100
    merged["Income_yoy_pct"] = merged["median_income"].pct_change() * 100
    merged["Pop_yoy_pct"]    = merged["population"].pct_change() * 100

    return merged

df = load_merged()

st.sidebar.header("Controls")

min_year, max_year = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider(
    "Year range",
    min_value=min_year, max_value=max_year,
    value=(max(min_year, max_year - 10), max_year), 
    step=1,
)

view_mode = st.sidebar.radio(
    "Value scale",
    options=["Raw values", "Indexed (first year = 100)"],
    index=0,
)

show_yoy = st.sidebar.checkbox("Show YoY % chart", value=True)

series_options = {
    "Housing Price Index": ("housing_price_index", "HPI_idx", "HPI_yoy_pct"),
    "Median Income (USD)": ("median_income", "Income_idx", "Income_yoy_pct"),
    "Population (people)": ("population", "Pop_idx", "Pop_yoy_pct"),
}
selected_labels = st.sidebar.multiselect(
    "Series to display",
    options=list(series_options.keys()),
    default=list(series_options.keys()),  
)

mask = (df["year"] >= year_range[0]) & (df["year"] <= year_range[1])
dfv = df.loc[mask].copy()

dfv["year_dt"] = pd.to_datetime(dfv["year"], format="%Y")

st.title("Santa Barbara County — Economic Trends")

latest = dfv.iloc[-1]  
prev   = dfv.iloc[-2] if len(dfv) >= 2 else None

col1, col2, col3 = st.columns(3)
hpi_val = latest["housing_price_index"]
hpi_delta = None if prev is None else f"{latest['HPI_yoy_pct']:+.1f}% YoY"
col1.metric("HPI (index points)", f"{hpi_val:.1f}", hpi_delta)

inc_val = latest["median_income"]
inc_delta = None if prev is None else f"{latest['Income_yoy_pct']:+.1f}% YoY"
col2.metric("Median Income (USD)", f"${inc_val:,.0f}", inc_delta)

pop_val = latest["population"]
pop_delta = None if prev is None else f"{latest['Pop_yoy_pct']:+.1f}% YoY"
col3.metric("Population", f"{pop_val:,.0f}", pop_delta)

st.caption(f"Showing {year_range[0]}–{year_range[1]} (latest = {int(latest['year'])})")

plot_rows = []
for label in selected_labels:
    raw_col, idx_col, yoy_col = series_options[label]
    y_col = raw_col if view_mode == "Raw values" else idx_col
    for _, r in dfv.iterrows():
        plot_rows.append({
            "year_dt": r["year_dt"],  
            "value": r[y_col], 
            "series": label,          
        })
plot_df = pd.DataFrame(plot_rows)

st.subheader("Trend")
st.line_chart(
    plot_df,
    x="year_dt",
    y="value",
    color="series",
    height=400,
)

if show_yoy:
    yoy_rows = []
    for label in selected_labels:
        raw_col, idx_col, yoy_col = series_options[label]
        for _, r in dfv.iterrows():
            yoy_rows.append({
                "year_dt": r["year_dt"],
                "value": r[yoy_col],
                "series": label,
            })
    yoy_df = pd.DataFrame(yoy_rows)

    st.subheader("Year-over-Year % Change")
    st.line_chart(
        yoy_df,
        x="year_dt",
        y="value",
        color="series",
        height=320,
    )

with st.expander("See merged data"):
    st.dataframe(dfv[["year", "housing_price_index", "median_income", "population",
                      "HPI_idx", "Income_idx", "Pop_idx",
                      "HPI_yoy_pct", "Income_yoy_pct", "Pop_yoy_pct"]], use_container_width=True)