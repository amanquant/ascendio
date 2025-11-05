import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- DATA: load from Excel ---
list1_df = pd.read_excel('list1.xlsx')  # Companies
list2_df = pd.read_excel('list2.xlsx')  # Sector/Company Extended
list3_df = pd.read_excel('list3.xlsx')  # People / Relations

st.title("🔎 FinGPT Company & Sector Analytics Engine")
st.markdown(
    "*Conversational search: ask about a company, info type (EBIT, emp, sector, management, ownership, extended analytics, contacts, full overview, M&A, etc.)*"
)

# -- 1. User Inputs --
company_list = list1_df['company'].dropna().unique()
company_name = st.selectbox("Select company to analyze", company_list)

info_type = st.text_input(
    "What info do you want? (e.g. ebit, emp, sector analytics, ownership, M&A, contacts, full overview)"
)

if st.button("Search / Analyze"):
    # -- 2. Core Lookups --
    company_row = list1_df[list1_df['company'] == company_name]
    sector_row = list2_df[list2_df['Company name'] == company_name]
    
    if company_row.empty:
        st.error('Company not found in database!')
    else:
        # ---- Company Overview (list1) ----
        st.subheader(f"Company Overview: {company_name}")
        show_cols = ['company','Nace','ebit','emp','Sector','name','title','name owner','ownership %']
        st.table(company_row[show_cols].T)

        # ---- Extended Analytics (list2) ----
        if not sector_row.empty and (
            any(x in info_type.lower() for x in [
                'sector','extended','overview','ebitda','ebit','emp','m&a','clients','capital','acquired','ownership'
            ])
        ):
            st.markdown(f"---\n**Extended Sector/Company Data**")
            sector_cols = [
                'Sector','Location','ebitda','ebit','emp','ST debt','New hires','Dep who hired the most',
                'Average new employee pay','Last quarter new clients','n of acquired','% of diversified',
                '% of consolidation','is the company been acquired by a PE Fund',
                'is planning a m&a operation','is planning a capital increase'
            ]
            st.table(sector_row[sector_cols].T)

            # --- Plotly Bar Chart: EBIT vs EBITDA vs EMP ---
            chart_metrics = ['ebit', 'ebitda', 'emp']
            chart_vals = [sector_row[m].iloc[0] if m in sector_row.columns else None for m in chart_metrics]
            fig = go.Figure(data=[
                go.Bar(
                    x=chart_metrics,
                    y=chart_vals,
                    marker_color=["royalblue","green","grey"],
                    text=[f"{v:,}" for v in chart_vals],
                    textposition="auto"
                )
            ])
            fig.update_layout(
                title="EBIT / EBITDA / Employees",
                yaxis_title="Value",
                xaxis_title="Metric"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # --- Special fields analytics ---
            st.markdown("**Strategic Actions:**")
            if sector_row['is planning a m&a operation'].iloc[0]:
                st.info("Company is planning an M&A operation.")
            if sector_row['is planning a capital increase'].iloc[0]:
                st.info("Company is planning a capital increase.")
            if sector_row['is the company been acquired by a PE Fund'].iloc[0]:
                st.warning("Acquired by Private Equity Fund.")

        # ---- Ownership Info (list1) ----
        if 'ownership' in info_type.lower() or 'full' in info_type.lower():
            st.markdown("**Ownership**")
            st.write(f"-- Name owner: {company_row['name owner'].iloc[0]}")
            st.write(f"-- Ownership %: {company_row['ownership %'].iloc[0]}")

        # ---- Contact & Person relationships (list3) ----
        if 'contact' in info_type.lower() or 'relation' in info_type.lower() or 'full' in info_type.lower():
            with st.expander("Show Person/Contact Relations"):
                # Find all persons linked to this company (exact and in 'Companies')
                persons_direct = list3_df[list3_df['Main Company'] == company_name]
                persons_indirect = list3_df[list3_df['Companies'].apply(lambda x: company_name in str(x))]
                persons = pd.concat([persons_direct, persons_indirect]).drop_duplicates()
                if persons.empty:
                    st.write("No contacts or relations found.")
                else:
                    contact_cols = ['Tax code','Born in','Current roles','Companies','Main Company','Relation','Profile of relation']
                    st.table(persons[contact_cols])
