import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- DATA: load from Excel ---
list1_df = pd.read_excel('list1.xlsx')  # Companies
list2_df = pd.read_excel('list2.xlsx')  # Sectors
list3_df = pd.read_excel('list3.xlsx')  # Contacts

# --- APP LAYOUT ---
st.title("🔎 FinGPT Company & Sector Analytics Engine")

st.markdown("*Conversational search: ask about a company, info type (Revenue, EBITDA, Sector, Contacts, etc), and get analytics instantly!*")

# -- 1. User Inputs --
company_list = list1_df['company'].dropna().unique()
company_name = st.selectbox("Select company to analyze", company_list)

info_type = st.text_input(
    "What info do you want? (e.g. EBITDA, revenue, sector analytics, contacts, full overview)"
)

if st.button("Search / Analyze"):
    # Find company row
    company_data = list1_df[list1_df['company'] == company_name]
    if company_data.empty:
        st.error('Company not found in database.')
    else:
        # Display company details
        st.subheader(f"Company Overview: {company_name}")
        st.write(company_data.T)
        
        # Analytics: EBITDA, Revenue, or full overview
        sector_name = company_data['sector'].iloc[0]
        sector_data = list2_df[list2_df['sector'] == sector_name]
        
        # Core financials:
        if any(x in info_type.lower() for x in ['ebitda', 'revenue', 'full', 'overview']):
            st.markdown("**Financials**")
            for col in ['revenue', 'ebitda']:
                if col in company_data.columns:
                    val = company_data[col].iloc[0]
                    st.metric(label=col.capitalize(), value=val)
            # Add more columns if you have them

        # Sector analytics
        if ('sector' in info_type.lower()) or ('compare' in info_type.lower()) or ('overview' in info_type.lower()):
            st.markdown(f"---\n**Sector: {sector_name}**")
            
            if not sector_data.empty:
                st.write(sector_data.T)
                # Sector vs Company chart
                fig, ax = plt.subplots()
                bars = []
                labels = []
                for k in ['avg_revenue', 'avg_ebitda']:
                    if k in sector_data.columns and k.replace("avg_", "") in company_data.columns:
                        sector_val = sector_data[k].iloc[0]
                        company_val = company_data[k.replace("avg_", "")].iloc[0]
                        labels.extend([f"Sector Avg {k.replace('avg_', '').capitalize()}", f"{company_name} {k.replace('avg_', '').capitalize()}"])
                        bars.extend([sector_val, company_val])
                ax.bar(labels, bars, color=['gray', 'royalblue']*len(bars)//2)
                ax.set_ylabel("Value (mln)")
                st.pyplot(fig)
            else:
                st.write("_No sector data available._")
        
        # Peer comparison within sector
        if ('peer' in info_type.lower()) or ('full' in info_type.lower()) or ('overview' in info_type.lower()):
            st.markdown(f"---\n**Peer Comparison in {sector_name}**")
            sector_peers = list1_df[list1_df['sector'] == sector_name].sort_values(by='revenue', ascending=False)
            st.dataframe(sector_peers[['company', 'revenue', 'ebitda']])
        
        # Contact info
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
