import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Cloud Kitchen PNL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #f2ede4; }

    .dash-title {
        background: #1a1a1a;
        color: #fff;
        padding: 12px 20px;
        font-size: 18px;
        font-weight: 600;
        letter-spacing: 0.4px;
        border-radius: 4px;
        margin-bottom: 16px;
    }

    .filter-panel {
        background: #fdf6e3;
        border: 1px solid #e8d8a0;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }

    .section-label {
        background: #1a1a1a;
        color: white;
        font-size: 12px;
        font-weight: 600;
        padding: 5px 12px;
        display: inline-block;
        border-radius: 3px;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .inline-warn {
        background: #fff8e1;
        border-left: 3px solid #f0a500;
        padding: 8px 12px;
        font-size: 13px;
        border-radius: 0 4px 4px 0;
        color: #5a4000;
    }

    .inline-info {
        background: #e8f4fd;
        border-left: 3px solid #2196f3;
        padding: 8px 12px;
        font-size: 13px;
        border-radius: 0 4px 4px 0;
        color: #1a3a4a;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        border-radius: 6px 6px 0 0;
        gap: 2px;
        padding: 4px 6px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #aaa;
        font-size: 13px;
        font-weight: 500;
        padding: 6px 16px;
        border-radius: 4px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #f0a500 !important;
        color: #1a1a1a !important;
        font-weight: 600;
    }

    div[data-testid="stMetric"] {
        background: #fff;
        border: 1px solid #ddd6c8;
        border-radius: 6px;
        padding: 12px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 20px !important;
        font-weight: 700;
    }

    .stMultiSelect [data-baseweb="select"] {
        background: #fffdf5;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #ddd6c8;
        border-radius: 4px;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    hr {
        border: none;
        border-top: 1px solid #ddd6c8;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data():

    df = pd.read_excel("Kittchen PNL Data.xlsx", header=1)

    for col in [
        "ORDER COUNT",
        "CART SALES",
        "DISCOUNT",
        "NET REVENUE",
        "IDEAL FOOD COST",
        "GROSS MARGIN",
        "KITCHEN EBITDA",
        "VARIANCE"
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    mo = {
        "Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
        "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12
    }

    def sort_key(m):
        try:
            p = m.split("-")
            return int(p[1]) * 100 + mo.get(p[0], 0)
        except:
            return 0

    df["_msort"] = df["MONTH"].apply(sort_key)

    df = df.sort_values("_msort")

    df["GM%"] = (
        df["GROSS MARGIN"] / df["NET REVENUE"] * 100
    ).round(2)

    df["CM"] = df["GROSS MARGIN"]

    df["CM%"] = df["GM%"]

    df["EBITDA%"] = (
        df["KITCHEN EBITDA"] / df["NET REVENUE"] * 100
    ).round(2)

    df["VARIANCE%"] = (
        df["VARIANCE"] / df["IDEAL FOOD COST"] * 100
    ).round(2)

    df["REV_BUCKET"] = pd.cut(
        df["NET REVENUE"],
        bins=[0, 1500000, 2500000, 3500000, 4500000, float("inf")],
        labels=[
            "Below INR 15 lacs",
            "INR 15 to 25 lacs",
            "INR 25 to 35 lacs",
            "INR 35 to 45 lacs",
            "Above INR 45 lacs"
        ]
    )

    df["VAR_BUCKET"] = pd.cut(
        df["VARIANCE%"],
        bins=[-np.inf, 2, 3, 5, np.inf],
        labels=[
            "(a) Var < 2%",
            "(b) Var 2% to 3%",
            "(c) Var 3% to 5%",
            "(d) Var > 5%"
        ]
    )

    return df


df = load_data()

all_months = (
    df.drop_duplicates("MONTH")
    .sort_values("_msort")["MONTH"]
    .tolist()
)

st.markdown(
    '<div class="dash-title">☁ Cloud Kitchen PNL Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="filter-panel">', unsafe_allow_html=True)

a, b, c, d, e = st.columns(5)

with a:
    months = st.multiselect(
        "Month",
        all_months,
        default=all_months
    )

with b:
    cities = st.multiselect(
        "City",
        sorted(df["CITY"].unique()),
        default=sorted(df["CITY"].unique())
    )

with c:
    stores = st.multiselect(
        "Store",
        sorted(df["STORE"].unique()),
        default=sorted(df["STORE"].unique())
    )

with d:
    rev_cohort = st.multiselect(
        "Revenue Cohort",
        sorted(df["REVENUE COHORT"].unique()),
        default=sorted(df["REVENUE COHORT"].unique())
    )

with e:
    status_filter = st.multiselect(
        "Status",
        list(df["STATUS"].unique()),
        default=list(df["STATUS"].unique())
    )

st.markdown('</div>', unsafe_allow_html=True)

base = df[
    df["MONTH"].isin(months) &
    df["CITY"].isin(cities) &
    df["STORE"].isin(stores) &
    df["REVENUE COHORT"].isin(rev_cohort) &
    df["STATUS"].isin(status_filter)
].copy()

if base.empty:
    st.markdown(
        '<div class="inline-warn">⚠ Nothing to show — try relaxing the filters.</div>',
        unsafe_allow_html=True
    )
    st.stop()

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.metric(
        "Net Revenue",
        f"₹ {base['NET REVENUE'].sum()/1e7:.2f} Cr"
    )

with m2:
    st.metric(
        "Total EBITDA",
        f"₹ {base['KITCHEN EBITDA'].sum()/1e5:.1f} L"
    )

with m3:
    st.metric(
        "Avg EBITDA %",
        f"{base['EBITDA%'].mean():.1f}%"
    )

with m4:
    st.metric(
        "Avg GM %",
        f"{base['GM%'].mean():.1f}%"
    )

with m5:
    neg = base[
        base["KITCHEN EBITDA"] < 0
    ]["STORE"].nunique()

    st.metric(
        "–ve EBITDA Stores",
        f"{neg} / {base['STORE'].nunique()}"
    )

st.markdown("---")

tab1, tab2 = st.tabs([
    "  Dashboard 1 · Kitchen Level PNL  ",
    "  Dashboard 2 · Variance Level PNL  "
])

with tab1:

    st.markdown(
        '<span class="section-label">Kitchen Level PNL</span>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)

    left, mid, right = st.columns(3)

    with left:
        emin = int(base["KITCHEN EBITDA"].min())
        emax = int(base["KITCHEN EBITDA"].max())

        ebitda_rng = st.slider(
            "EBITDA Range (Rs.)",
            emin,
            emax,
            (emin, emax),
            step=5000
        )

    with mid:
        rmin = int(base["NET REVENUE"].min())
        rmax = int(base["NET REVENUE"].max())

        rev_rng = st.slider(
            "Net Revenue Range (Rs.)",
            rmin,
            rmax,
            (rmin, rmax),
            step=10000
        )

    with right:
        cmin = int(base["CM"].min())
        cmax = int(base["CM"].max())

        cm_rng = st.slider(
            "CM Range (Rs.)",
            cmin,
            cmax,
            (cmin, cmax),
            step=10000
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)

    fa, fb, fc, fd, fe = st.columns(5)

    with fa:
        zone_filter = st.multiselect(
            "Zone",
            sorted(df["ZONE MAPPING"].unique()),
            default=sorted(df["ZONE MAPPING"].unique()),
            key="zone"
        )

    with fb:
        ebitda_cat = st.multiselect(
            "EBITDA Category",
            sorted(df["EBITDA CATEGORY"].unique()),
            default=sorted(df["EBITDA CATEGORY"].unique()),
            key="ecat"
        )

    with fc:
        ebitda_cohort = st.multiselect(
            "EBITDA Cohort",
            sorted(df["EBITDA COHORT"].unique()),
            default=sorted(df["EBITDA COHORT"].unique()),
            key="ecoh"
        )

    with fd:
        cm_cohort = st.multiselect(
            "CM Cohort",
            sorted(df["CM COHORT"].unique()),
            default=sorted(df["CM COHORT"].unique()),
            key="cmcoh"
        )

    with fe:
        d1_months = st.multiselect(
            "Month",
            all_months,
            default=all_months,
            key="d1m"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    kdf = base[
        base["ZONE MAPPING"].isin(zone_filter) &
        base["EBITDA CATEGORY"].isin(ebitda_cat) &
        base["EBITDA COHORT"].isin(ebitda_cohort) &
        base["CM COHORT"].isin(cm_cohort) &
        base["MONTH"].isin(d1_months) &
        base["KITCHEN EBITDA"].between(ebitda_rng[0], ebitda_rng[1]) &
        base["NET REVENUE"].between(rev_rng[0], rev_rng[1]) &
        base["CM"].between(cm_rng[0], cm_rng[1])
    ].copy()

    if kdf.empty:

        st.markdown(
            '<div class="inline-warn">⚠ No records for this filter combination.</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f'<div class="inline-info">Showing <b>{len(kdf)}</b> records · '
            f'<b>{kdf["STORE"].nunique()}</b> stores · '
            f'<b>{kdf["MONTH"].nunique()}</b> months</div>',
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        snap = kdf.groupby(
            ["STORE", "MONTH"],
            as_index=False
        ).agg(
            net_rev=("NET REVENUE", "sum"),
            gm_pct=("GM%", "mean"),
            cm_pct=("CM%", "mean"),
            ebitda=("KITCHEN EBITDA", "sum"),
            ebitda_pct=("EBITDA%", "mean")
        )

        msort = {
            m: i for i, m in enumerate(all_months)
        }

        active_months = sorted(
            snap["MONTH"].unique(),
            key=lambda x: msort.get(x, 99)
        )

        parts = []

        for m in active_months:

            s = snap[
                snap["MONTH"] == m
            ][[
                "STORE",
                "net_rev",
                "gm_pct",
                "cm_pct",
                "ebitda",
                "ebitda_pct"
            ]].copy()

            s.columns = [
                "STORE",
                (m, "Net Rev"),
                (m, "GM%"),
                (m, "CM%"),
                (m, "EBITDA"),
                (m, "EBITDA%")
            ]

            parts.append(
                s.set_index("STORE")
            )

        if parts:

            pivot = pd.concat(parts, axis=1)

            pivot.columns = pd.MultiIndex.from_tuples(
                pivot.columns
            )

            flat = pivot.reset_index().copy()

            flat.columns = [
                f"{b} . {a}" if b else a
                for a, b in flat.columns
            ]

            for col in flat.columns:

                if col == "STORE":
                    continue

                if "%" in col:
                    flat[col] = flat[col].apply(
                        lambda x: f"{x:.1f}%"
                        if pd.notna(x) else "-"
                    )

                elif "Net Rev" in col:
                    flat[col] = flat[col].apply(
                        lambda x: f"Rs.{x/100000:.1f}L"
                        if pd.notna(x) else "-"
                    )

                elif "EBITDA" in col:
                    flat[col] = flat[col].apply(
                        lambda x: f"Rs.{x:,.0f}"
                        if pd.notna(x) else "-"
                    )

            def flag_negative(row):

                out = [""] * len(row)

                for i, col in enumerate(flat.columns):

                    if "EBITDA" in col and "%" not in col:

                        try:
                            if float(
                                row[col]
                                .replace("Rs.","")
                                .replace(",","")
                            ) < 0:

                                out[i] = (
                                    "background-color: #ffe0e0; "
                                    "color: #b00000; "
                                    "font-weight: 500"
                                )

                        except:
                            pass

                return out

            st.dataframe(
                flat.style.apply(flag_negative, axis=1),
                width="stretch",
                height=420
            )

        dl_col, info_col = st.columns([1, 3])

        with dl_col:
            st.download_button(
                "Download Kitchen PNL",
                kdf.to_csv(index=False).encode(),
                "kitchen_pnl.csv",
                "text/csv"
            )

        with info_col:

            top3 = (
                kdf.groupby("STORE")["KITCHEN EBITDA"]
                .sum()
                .nlargest(3)
                .index
                .tolist()
            )

            bot3 = (
                kdf.groupby("STORE")["KITCHEN EBITDA"]
                .sum()
                .nsmallest(3)
                .index
                .tolist()
            )

            st.markdown(
                f'<div class="inline-info">Best EBITDA: {", ".join(top3)} '
                f'&nbsp;·&nbsp; Watch list: {", ".join(bot3)}</div>',
                unsafe_allow_html=True
            )

        monthly = kdf.groupby("MONTH").agg(
            Stores=("STORE", "nunique"),
            Revenue=("NET REVENUE", "sum"),
            EBITDA=("KITCHEN EBITDA", "sum"),
            ebitda_pct=("EBITDA%", "mean"),
            gm_pct=("GM%", "mean")
        ).reindex([
            m for m in all_months
            if m in kdf["MONTH"].values
        ])

        monthly["Net Revenue"] = monthly["Revenue"].map(
            lambda x: f"Rs.{x/100000:.1f}L"
        )

        monthly["EBITDA (Rs.)"] = monthly["EBITDA"].map(
            lambda x: f"Rs.{x:,.0f}"
        )

        monthly["EBITDA %"] = monthly["ebitda_pct"].map(
            lambda x: f"{x:.1f}%"
        )

        monthly["GM %"] = monthly["gm_pct"].map(
            lambda x: f"{x:.1f}%"
        )

        out = monthly[
            [
                "Stores",
                "Net Revenue",
                "EBITDA (Rs.)",
                "EBITDA %",
                "GM %"
            ]
        ].reset_index()

        out.columns = ["Month"] + list(out.columns[1:])

        st.dataframe(
            out,
            width="stretch",
            hide_index=True
        )

with tab2:

    st.markdown(
        '<span class="section-label">Variance Level PNL</span>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)

    vcol, mcol = st.columns([2, 3])

    with vcol:

        var_cats = [
            "(a) Var < 2%",
            "(b) Var 2% to 3%",
            "(c) Var 3% to 5%",
            "(d) Var > 5%"
        ]

        sel_vbuckets = st.multiselect(
            "Variance Category",
            var_cats,
            default=var_cats
        )

    with mcol:

        var_months = st.multiselect(
            "Month",
            all_months,
            default=all_months,
            key="vm"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    vdf = base[
        base["VAR_BUCKET"].isin(sel_vbuckets) &
        base["MONTH"].isin(var_months)
    ].copy()

    if vdf.empty:

        st.markdown(
            '<div class="inline-warn">⚠ No variance data for the selected filters.</div>',
            unsafe_allow_html=True
        )

    else:

        v_months = [
            m for m in all_months
            if m in vdf["MONTH"].unique()
        ]

        v1 = pd.pivot_table(
            vdf,
            values="VARIANCE%",
            index="REVENUE COHORT",
            columns="MONTH",
            aggfunc="mean"
        ).reindex(columns=v_months)

        v1.index.name = "Revenue Category"

        grand_avg = (
            vdf.groupby("MONTH")["VARIANCE%"]
            .mean()
        )

        v1_display = pd.concat([
            v1,
            pd.DataFrame(
                [grand_avg.reindex(v_months).values],
                columns=v_months,
                index=["Grand Total"]
            )
        ])

        def pct_fmt(x):
            return "-" if pd.isna(x) else f"{x:.1f}%"

        st.dataframe(
            v1_display.style
            .format(pct_fmt)
            .set_properties(**{"text-align": "center"})
            .apply(
                lambda r: [
                    "font-weight:bold; background:#f5f0e0"
                    if r.name == "Grand Total"
                    else ""
                    for _ in r
                ],
                axis=1
            ),
            width="stretch"
        )

        dl, _ = st.columns([1, 4])

        with dl:
            st.download_button(
                "Download",
                v1_display.to_csv().encode(),
                "variance_avg_pct.csv",
                "text/csv",
                key="dlv1"
            )

        rev_order = [
            "Below INR 15 lacs",
            "INR 15 to 25 lacs",
            "INR 25 to 35 lacs",
            "INR 35 to 45 lacs",
            "Above INR 45 lacs"
        ]

        v2 = pd.pivot_table(
            vdf,
            values="STORE",
            index="REV_BUCKET",
            columns="MONTH",
            aggfunc=pd.Series.nunique,
            fill_value=0
        )

        v2 = v2.reindex(
            index=[
                r for r in rev_order
                if r in v2.index
            ],
            columns=v_months
        ).fillna(0).astype(int)

        v2.index.name = "Revenue Category"

        grand_count = (
            vdf.groupby("MONTH")["STORE"]
            .nunique()
            .reindex(v_months)
            .fillna(0)
            .astype(int)
        )

        v2_display = pd.concat([
            v2,
            pd.DataFrame(
                [grand_count.values],
                columns=v_months,
                index=["Grand Total"]
            )
        ])

        st.dataframe(
            v2_display.style
            .set_properties(**{"text-align": "center"})
            .apply(
                lambda r: [
                    "font-weight:bold; background:#f5f0e0"
                    if r.name == "Grand Total"
                    else ""
                    for _ in r
                ],
                axis=1
            ),
            width="stretch"
        )

st.markdown("---")

st.markdown(
    '<div style="text-align:center;font-size:11px;color:#aaa;">'
    'Cloud Kitchen PNL · Internal Ops Dashboard · Cache refreshes every 5 min'
    '</div>',
    unsafe_allow_html=True
)
