import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Cloud Kitchen Dashboard",
    layout="wide"
)

st.title("Cloud Kitchen PNL Dashboard")

st.write(
    "Interactive dashboard for analyzing kitchen level "
    "profitability and variance performance."
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    data = pd.read_excel(
        "Kittchen PNL Data.xlsx",
        header=1
    )

    return data


df = load_data()

# --------------------------------------------------
# MONTH SORTING
# --------------------------------------------------

df["MONTH_DATE"] = pd.to_datetime(
    df["MONTH"],
    format="%b-%Y"
)

df = df.sort_values("MONTH_DATE")

# --------------------------------------------------
# NUMERIC CONVERSION
# --------------------------------------------------

numeric_columns = [
    "ORDER COUNT",
    "CART SALES",
    "DISCOUNT",
    "NET REVENUE",
    "IDEAL FOOD COST",
    "GROSS MARGIN",
    "KITCHEN EBITDA",
    "VARIANCE"
]

for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# --------------------------------------------------
# VARIANCE PERCENTAGE
# --------------------------------------------------

df["VARIANCE_PERCENT"] = (
    df["VARIANCE"] /
    df["NET REVENUE"]
) * 100

# --------------------------------------------------
# TOP FILTERS
# --------------------------------------------------

st.markdown("---")

filter1, filter2, filter3, filter4 = st.columns(4)

with filter1:

    selected_month = st.multiselect(
        "Month",
        options=df["MONTH"].drop_duplicates(),
        default=df["MONTH"].drop_duplicates()
    )

with filter2:

    selected_city = st.multiselect(
        "City",
        options=sorted(df["CITY"].unique()),
        default=sorted(df["CITY"].unique())
    )

with filter3:

    selected_store = st.multiselect(
        "Store",
        options=sorted(df["STORE"].unique()),
        default=sorted(df["STORE"].unique())
    )

with filter4:

    selected_revenue = st.multiselect(
        "Revenue Cohort",
        options=sorted(df["REVENUE COHORT"].unique()),
        default=sorted(df["REVENUE COHORT"].unique())
    )

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_df = df[
    (df["MONTH"].isin(selected_month)) &
    (df["CITY"].isin(selected_city)) &
    (df["STORE"].isin(selected_store)) &
    (df["REVENUE COHORT"].isin(selected_revenue))
]

filtered_df = filtered_df.copy()

# --------------------------------------------------
# EMPTY DATA CHECK
# --------------------------------------------------

if filtered_df.empty:

    st.warning(
        "No data available for selected filters."
    )

    st.stop()

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

st.markdown("---")

total_revenue = filtered_df["NET REVENUE"].sum()

total_ebitda = filtered_df["KITCHEN EBITDA"].sum()

total_orders = filtered_df["ORDER COUNT"].sum()

avg_variance = filtered_df["VARIANCE_PERCENT"].mean()

total_stores = filtered_df["STORE"].nunique()

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:

    st.metric(
        "Total Revenue",
        f"₹ {total_revenue:,.0f}"
    )

with kpi2:

    st.metric(
        "Total EBITDA",
        f"₹ {total_ebitda:,.0f}"
    )

with kpi3:

    st.metric(
        "Total Orders",
        f"{total_orders:,.0f}"
    )

with kpi4:

    st.metric(
        "Average Variance %",
        f"{avg_variance:.2f}%"
    )

with kpi5:

    st.metric(
        "Store Count",
        total_stores
    )

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "Kitchen Level PNL",
    "Variance Level PNL",
    "Store Analysis"
])

# ==================================================
# TAB 1
# ==================================================

with tab1:

    st.subheader("Kitchen Level PNL")

    col1, col2, col3 = st.columns(3)

    with col1:

        ebitda_range = st.slider(
            "Select EBITDA Range",
            min_value=int(filtered_df["KITCHEN EBITDA"].min()),
            max_value=int(filtered_df["KITCHEN EBITDA"].max()),
            value=(
                int(filtered_df["KITCHEN EBITDA"].min()),
                int(filtered_df["KITCHEN EBITDA"].max())
            )
        )

    with col2:

        selected_ebitda_category = st.multiselect(
            "EBITDA Category",
            options=sorted(df["EBITDA CATEGORY"].unique()),
            default=sorted(df["EBITDA CATEGORY"].unique())
        )

    with col3:

        selected_ebitda_cohort = st.multiselect(
            "EBITDA Cohort",
            options=sorted(df["EBITDA COHORT"].unique()),
            default=sorted(df["EBITDA COHORT"].unique())
        )

    selected_cm = st.multiselect(
        "CM Cohort",
        options=sorted(df["CM COHORT"].unique()),
        default=sorted(df["CM COHORT"].unique())
    )

    kitchen_df = filtered_df[
        (filtered_df["EBITDA CATEGORY"].isin(selected_ebitda_category)) &
        (filtered_df["EBITDA COHORT"].isin(selected_ebitda_cohort)) &
        (filtered_df["CM COHORT"].isin(selected_cm)) &
        (
            filtered_df["KITCHEN EBITDA"].between(
                ebitda_range[0],
                ebitda_range[1]
            )
        )
    ]

    if kitchen_df.empty:

        st.warning(
            "No Kitchen PNL data available."
        )

    else:

        display_columns = [
            "MONTH",
            "CITY",
            "STORE",
            "ORDER COUNT",
            "NET REVENUE",
            "GROSS MARGIN",
            "KITCHEN EBITDA",
            "VARIANCE_PERCENT",
            "REVENUE COHORT",
            "CM COHORT",
            "EBITDA CATEGORY",
            "EBITDA COHORT"
        ]

        display_df = kitchen_df[
            display_columns
        ].copy()

        display_df = display_df.rename(
            columns={
                "VARIANCE_PERCENT": "VARIANCE %"
            }
        )

        def highlight_ebitda(val):

            if val < 0:
                return "background-color: #ffcccc"

            return ""

        def highlight_variance(val):

            if val > 5:
                return "background-color: #fff3cd"

            return ""

        styled_df = display_df.style.map(
            highlight_ebitda,
            subset=["KITCHEN EBITDA"]
        ).map(
            highlight_variance,
            subset=["VARIANCE %"]
        )

        st.dataframe(
            styled_df,
            width="stretch"
        )

        st.markdown("---")

        st.subheader("Kitchen Snapshot")

        snapshot_table = pd.pivot_table(
            kitchen_df,
            values=[
                "NET REVENUE",
                "GROSS MARGIN",
                "KITCHEN EBITDA"
            ],
            index="STORE",
            columns="MONTH",
            aggfunc="sum"
        )

        snapshot_table = snapshot_table.round(2)

        st.dataframe(
            snapshot_table,
            width="stretch"
        )

        st.markdown("---")

        chart1, chart2 = st.columns(2)

        with chart1:

            revenue_chart = px.bar(
                kitchen_df.groupby(
                    "STORE",
                    as_index=False
                )["NET REVENUE"].sum(),
                x="STORE",
                y="NET REVENUE",
                title="Revenue by Store"
            )

            st.plotly_chart(
                revenue_chart,
                use_container_width=True
            )

        with chart2:

            monthly_summary = kitchen_df.groupby(
                ["MONTH", "MONTH_DATE"],
                as_index=False
            )[[
                "NET REVENUE",
                "KITCHEN EBITDA"
            ]].sum()

            monthly_summary = monthly_summary.sort_values(
                "MONTH_DATE"
            )

            trend_chart = px.line(
                monthly_summary,
                x="MONTH",
                y=[
                    "NET REVENUE",
                    "KITCHEN EBITDA"
                ],
                markers=True,
                title="Monthly Revenue and EBITDA Trend"
            )

            st.plotly_chart(
                trend_chart,
                use_container_width=True
            )

# ==================================================
# TAB 2
# ==================================================

with tab2:

    st.subheader("Variance Level PNL")

    variance_bins = [0, 2, 3, 5, float("inf")]

    variance_labels = [
        "Var <2%",
        "Var 2%-3%",
        "Var 3%-5%",
        "Var >5%"
    ]

    kitchen_df["VARIANCE BUCKET"] = pd.cut(
        kitchen_df["VARIANCE_PERCENT"],
        bins=variance_bins,
        labels=variance_labels
    )

    selected_variance = st.multiselect(
        "Variance Category",
        options=variance_labels,
        default=variance_labels
    )

    variance_df = kitchen_df[
        kitchen_df["VARIANCE BUCKET"].isin(
            selected_variance
        )
    ]

    if variance_df.empty:

        st.warning(
            "No variance data available."
        )

    else:

        st.subheader(
            "Variance Heatmap"
        )

        heatmap_df = pd.pivot_table(
            variance_df,
            values="VARIANCE_PERCENT",
            index="REVENUE COHORT",
            columns="MONTH",
            aggfunc="mean"
        )

        heatmap_df = heatmap_df.round(2)

        heatmap_chart = px.imshow(
            heatmap_df,
            text_auto=True,
            aspect="auto",
            title="Average Variance Percentage Heatmap",
            labels=dict(
                color="Variance %"
            )
        )

        st.plotly_chart(
            heatmap_chart,
            use_container_width=True
        )

        st.subheader(
            "Average Variance % by Revenue Cohort"
        )

        heatmap_display = (
            heatmap_df.astype(str) + "%"
        )

        st.dataframe(
            heatmap_display,
            width="stretch"
        )

        st.subheader(
            "Store Count by Revenue Cohort"
        )

        store_count = pd.pivot_table(
            variance_df,
            values="STORE",
            index="REVENUE COHORT",
            columns="MONTH",
            aggfunc="count"
        )

        st.dataframe(
            store_count,
            width="stretch"
        )

# ==================================================
# TAB 3
# ==================================================

with tab3:

    st.subheader(
        "Top and Bottom Performing Stores"
    )

    store_summary = kitchen_df.groupby(
        "STORE",
        as_index=False
    )[[
        "NET REVENUE",
        "KITCHEN EBITDA"
    ]].sum()

    top_stores = store_summary.sort_values(
        "NET REVENUE",
        ascending=False
    ).head(10)

    st.write("Top 10 Stores by Revenue")

    top_chart = px.bar(
        top_stores,
        x="STORE",
        y="NET REVENUE"
    )

    st.plotly_chart(
        top_chart,
        use_container_width=True
    )

    bottom_stores = store_summary.sort_values(
        "NET REVENUE",
        ascending=True
    ).head(10)

    st.write("Bottom 10 Stores by Revenue")

    bottom_chart = px.bar(
        bottom_stores,
        x="STORE",
        y="NET REVENUE"
    )

    st.plotly_chart(
        bottom_chart,
        use_container_width=True
    )

    st.markdown("---")

    csv = kitchen_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Filtered Data",
        data=csv,
        file_name="filtered_kitchen_data.csv",
        mime="text/csv"
    )