import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- DATA: load from Excel ---
list1_df = pd.read_excel('list1.xlsx')  # Companies
list2_df = pd.read_excel('list2.xlsx')  # Sectors
list3_df = pd.read_excel('list3.xlsx')  # Contacts

st.title("🔎 FinGPT Company & Sector Analytics Engine")
st.markdown(
    "*Conversational search: ask about a company, info type (Revenue, EBITDA, Sector, Contacts, etc), and get analytics instantly!*"
)

# -- 1. User Inputs --
company_list = list1_df['company'].dropna().unique()
company_name = st.selectbox("Select company to analyze", company_list)

info_type = st.text_input(
    "What info do you want? (e.g. EBITDA, revenue, sector analytics, contacts, full overview)"
)

if st.button("Search / Analyze"):
    company_data = list1_df[list1_df['company'] == company_name]
    if company_data.empty:
        st.error('Company not found in database.')
    else:
        st.subheader(f"Company Overview: {company_name}")
        st.write(company_data.T)

        # --- Core financials ---
        sector_name = company_data['sector'].iloc[0]
        sector_data = list2_df[list2_df['sector'] == sector_name]

        if any(x in info_type.lower() for x in ['ebitda', 'revenue', 'full', 'overview']):
            st.markdown("**Financials**")
            for col in ['revenue', 'ebitda']:
                if col in company_data.columns:
                    val = company_data[col].iloc[0]
                    st.metric(label=col.capitalize(), value=val)

        # --- Sector analytics ---
        if ('sector' in info_type.lower()) or ('compare' in info_type.lower()) or ('overview' in info_type.lower()):
            st.markdown(f"---\n**Sector: {sector_name}**")
            if not sector_data.empty:
                st.write(sector_data.T)

                # Sector vs Company chart with Plotly
                bars = []
                labels = []
                colors = []

                for k in ['avg_revenue', 'avg_ebitda']:
                    if k in sector_data.columns and k.replace("avg_", "") in company_data.columns:
                        sector_val = sector_data[k].iloc[0]
                        company_val = company_data[k.replace("avg_", "")].iloc[0]
                        metric_name = k.replace('avg_', '').capitalize()
                        labels.extend([f"Sector Avg {metric_name}", f"{company_name} {metric_name}"])
                        bars.extend([sector_val, company_val])
                        colors.extend(['grey', 'royalblue'])

                fig = go.Figure(data=[
                    go.Bar(
                        x=labels,
                        y=bars,
                        marker_color=colors,
                        text=[f"{v:,}" for v in bars],
                        textposition="auto"
                    )
                ])
                fig.update_layout(yaxis_title="Value (mln)", title="Company vs Sector Comparison")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("_No sector data available._")

        # --- Peer comparison within sector ---
        if ('peer' in info_type.lower()) or ('full' in info_type.lower()) or ('overview' in info_type.lower()):
            st.markdown(f"---\n**Peer Comparison in {sector_name}**")
            sector_peers = list1_df[list1_df['sector'] == sector_name].sort_values(by='revenue', ascending=False)
            st.dataframe(sector_peers[['company', 'revenue', 'ebitda']])

            # Optional: Plotly bar chart for peer revenues
            fig_peers = go.Figure(
                data=[
                    go.Bar(
                        x=sector_peers['company'],
                        y=sector_peers['revenue'],
                        marker_color='royalblue',
                        text=[f"{v:,}" for v in sector_peers['revenue']],
                        textposition="auto"
                    )
                ]
            )
            fig_peers.update_layout(
                xaxis_title="Company",
                yaxis_title="Revenue",
                title=f"Revenue Comparison among {sector_name} Peers"
            )
            st.plotly_chart(fig_peers, use_container_width=True)

        # --- Contact info ---
        if 'contact' in info_type.lower() or 'full' in info_type.lower():
            st.markdown("---")
            with st.expander("Show Company Contacts"):
                contacts = list3_df[list3_df['company'] == company_name]
                if contacts.empty:
                    st.write("No contacts found.")
                else:
                    for idx, row in contacts.iterrows():
                        st.write(f"**{row['name']}** ({row['role']})")
                        st.write(f"Email: {row['email']}")
                        st.write("---")

