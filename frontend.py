import streamlit as st
import requests

st.set_page_config(
    page_title="IBM Sovereign Advisor",
    page_icon="≡ƒöÉ",
    layout="wide"
)

# Sidebar
st.sidebar.title("IBM Sovereign Advisor")
st.sidebar.markdown("""
### Intelligent Deployment Advisor

This platform helps customers choose between:

- Vault Enterprise
- HCP Vault Dedicated

Based on:
- Geography
- Compliance
- Workload Type
- Operational Ownership
- Growth Plans
- Data Residency
""")

st.sidebar.success("Prototype v1.0")

# Main Page
st.title("≡ƒöÉ IBM Sovereign Advisor")
st.subheader("AI-driven Infrastructure Recommendation Platform")

st.markdown(
    "Analyze customer requirements and recommend the right Vault deployment model."
)

# Form
with st.form("advisor_form"):

    col1, col2 = st.columns(2)

    with col1:
        geo = st.selectbox(
            "Geography",
            ["India", "US", "Europe", "Middle East"]
        )

        compliance = st.selectbox(
            "Compliance Requirements",
            ["High", "Medium", "Low"]
        )

        workload = st.selectbox(
            "Workload Type",
            ["Banking", "Healthcare", "Retail", "Government", "Technology"]
        )

    with col2:
        ownership = st.selectbox(
            "Operational Ownership",
            ["Customer Managed", "Managed Service"]
        )

        growth = st.selectbox(
            "Growth Plans",
            ["Startup Scale", "Mid-size Growth", "Enterprise Scale"]
        )

        data_residency = st.selectbox(
            "Data Residency Requirement",
            ["Strict", "Flexible"]
        )

    submitted = st.form_submit_button("Generate Recommendation")


if submitted:
    payload = {
        "geo": geo,
        "compliance": compliance,
        "workload": workload,
        "ownership": ownership,
        "growth": growth,
        "data_residency": data_residency
    }

    try:
        with st.spinner("Analyzing requirements..."):
            response = requests.post("http://api:8000/recommend",
                json=payload
            )

            result = response.json()

        st.divider()

        st.success("Recommendation Generated")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Recommended Product",
                result["recommendation"]
            )

        with col2:
            st.metric(
                "Confidence Score",
                "92%"
            )

        st.subheader("Why this recommendation?")
        st.info(result["reason"])

        st.subheader("Referenced Documentation")
        for doc in result["documents"]:
            st.write(f"Γ£à {doc}")

        st.subheader("Terraform Architecture Template")
        st.code(result["terraform"], language="hcl")

    except Exception as e:
        st.error(f"Error: {e}")

