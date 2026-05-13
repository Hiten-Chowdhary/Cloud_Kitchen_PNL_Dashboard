# Cloud Kitchen PNL Dashboard

This project is a Streamlit-based analytical dashboard created to explore and monitor the profitability and operational performance of cloud kitchen stores across different cities, revenue cohorts, and time periods.

The dashboard focuses on simplifying Kitchen PNL analysis and variance tracking through interactive filters, KPI summaries, cohort-level comparisons, and visual analysis.

---

# Objective

The main objective of this dashboard is to provide an easy-to-use reporting interface for:

- Kitchen level profitability tracking
- EBITDA performance analysis
- Revenue cohort analysis
- Variance monitoring
- Store-wise performance comparison
- Monthly operational trend analysis

The dashboard is designed from a business operations perspective rather than only a visualization perspective.

---

# Features Implemented

## Common Filters
- Month filter
- City filter
- Store filter
- Revenue Cohort filter

These filters dynamically update all dashboards and visualizations.

---

# Kitchen Level PNL Dashboard

This section focuses on operational profitability analysis.

### Included:
- EBITDA range slider
- EBITDA Category filter
- EBITDA Cohort filter
- CM Cohort filter
- Kitchen level operational table
- Conditional highlighting for:
  - Negative EBITDA
  - High variance percentage
- Kitchen snapshot pivot table
- Revenue by Store chart
- Monthly Revenue and EBITDA trend chart

---

# Variance Level PNL Dashboard

This section focuses on identifying operational variance patterns across revenue cohorts and months.

### Included:
- Variance bucket categorization
- Variance heatmap
- Average variance percentage matrix
- Store count matrix by cohort

Variance percentage is calculated using:

```text
Variance % = (Variance / Net Revenue) * 100
