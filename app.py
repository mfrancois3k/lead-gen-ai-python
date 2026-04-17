"""
app.py — LeadOptimizer AI  |  Streamlit Dashboard
Run locally:  streamlit run app.py
Deploy free:  https://share.streamlit.io
"""

import os, sys, time
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

sys.path.insert(0, os.path.dirname(__file__))
from core.scraper  import scrape_yellow_pages
from core.verifier import verify_domain, verify_email_domain
from core.ai_agent import score_lead

st.set_page_config(page_title="LeadOptimizer AI", page_icon="🚀",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.hero { background: linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%);
        padding:2rem 2.5rem; border-radius:14px; margin-bottom:1.8rem;
        color:#fff; text-align:center; }
.hero h1 { margin:0 0 .4rem; font-size:2.2rem; }
.hero p  { margin:0; opacity:.85; font-size:1rem; }
div.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%);
    color:white; border:none; border-radius:8px;
    padding:.55rem 2rem; font-weight:700; font-size:1rem; }
</style>""", unsafe_allow_html=True)

st.markdown("""<div class="hero">
    <h1>🚀 LeadOptimizer AI</h1>
    <p>Scrape · Verify · Score 500+ local service leads per day — powered by GPT-4o</p>
</div>""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("OpenAI API Key", type="password",
                            placeholder="sk-…",
                            help="Required for AI lead scoring.")
    if api_key:
        st.success("API key saved ✅", icon="🔑")
    st.divider()
    st.subheader("🎯 Ideal Customer Profile")
    icp_criteria = st.text_area("Describe your target customer", height=210,
        value=("Local service business (plumber, HVAC, roofer, landscaper) that:\n"
               "- Has been operating for 2+ years\n"
               "- Has a website (even a basic one)\n"
               "- Serves residential customers\n"
               "- Has 4+ star reviews online\n"
               "- Located in a metro area (100k+ population)\n"
               "- Does NOT yet have a structured lead generation system"))
    st.divider()
    st.subheader("🔧 Pipeline Options")
    check_domain = st.checkbox("Check domain health",     value=True)
    check_email  = st.checkbox("Verify email MX records", value=True)
    ai_scoring   = st.checkbox("Enable GPT-4o scoring",   value=True)
    st.divider()
    st.caption("Stack: Python · Streamlit · GPT-4o · BeautifulSoup · httpx")

for key in ("leads_df", "results_df"):
    if key not in st.session_state:
        st.session_state[key] = None

SCORE_COLOURS = {
    "Hot":  "background-color:#dcfce7; color:#14532d",
    "Warm": "background-color:#fef9c3; color:#713f12",
    "Cold": "background-color:#f3f4f6; color:#374151",
}
def _colour_score(val): return SCORE_COLOURS.get(val, "")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📤 Load Leads", "⚡ Verify & Score", "📊 Results & Export"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Load Leads
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col_upload, col_scrape = st.columns(2, gap="large")

    with col_upload:
        st.subheader("📁 Upload CSV")
        st.caption("Supported columns: Business Name, Phone, Website, Email, Address.")
        uploaded = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            st.session_state.leads_df = df
            st.success(f"✅ Loaded **{len(df):,}** leads from file.")
            st.dataframe(df.head(10), use_container_width=True)
        st.divider()
        if st.button("📋 Use Sample Data (20 leads)"):
            sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_leads.csv")
            df = pd.read_csv(sample_path)
            st.session_state.leads_df = df
            st.success(f"✅ Loaded **{len(df)}** sample leads.")
            st.rerun()
        if st.session_state.leads_df is not None and not uploaded:
            st.info(f"Current dataset: **{len(st.session_state.leads_df):,}** leads loaded.")

    with col_scrape:
        st.subheader("🌐 Scrape Yellow Pages")
        st.caption("Pull fresh leads directly from YellowPages.com.")
        niche = st.selectbox("Select niche", ["Plumbers","HVAC Contractors","Roofers",
            "Landscapers","Electricians","Painters","General Contractors",
            "Pest Control","Pool Service","Garage Door Repair"])
        location    = st.text_input("Target location", value="Dallas, TX")
        max_results = st.slider("Max results", 10, 100, 25, step=5)
        if st.button("🔍 Scrape Now", type="primary"):
            with st.spinner(f"Scraping {niche} in {location}…"):
                leads = scrape_yellow_pages(niche, location, max_results)
            if leads:
                df = pd.DataFrame(leads)
                st.session_state.leads_df = df
                st.success(f"✅ Found **{len(df)}** listings!")
                st.dataframe(df, use_container_width=True)
            else:
                st.error("No results returned. Try a different niche or location.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Verify & Score
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    if st.session_state.leads_df is None:
        st.info("👆 Go to **Load Leads** first to upload a CSV or scrape new leads.")
    else:
        df = st.session_state.leads_df.copy()
        n  = len(df)
        st.subheader(f"⚡ Ready to process {n:,} leads")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads",    f"{n:,}")
        m2.metric("Domain Check",   "✅ On" if check_domain else "⏭ Off")
        m3.metric("Email MX Check", "✅ On" if check_email  else "⏭ Off")
        m4.metric("AI Scoring",     "GPT-4o" if (ai_scoring and api_key) else "Demo mode")
        st.divider()
        if ai_scoring and not api_key:
            st.warning("⚠️ No API key — running in **demo mode** (scores are simulated).")

        if st.button("🚀 Run Full Pipeline", type="primary", use_container_width=True):
            progress_bar = st.progress(0.0, text="Starting…")
            status_text  = st.empty()
            results: list[dict] = []

            for idx, row in df.iterrows():
                pct  = (idx + 1) / n
                name = row.get("Business Name", f"Lead #{idx+1}")
                progress_bar.progress(pct, text=f"Processing {idx+1}/{n}: {name}")
                status_text.caption(f"🔍 Verifying: **{name}**")
                result = row.to_dict()

                if check_domain:
                    website = str(row.get("Website", ""))
                    if website and website not in ("N/A", "nan"):
                        d = verify_domain(website)
                        result["Domain_Live"]   = "✅ Live" if d["domain_live"] else "❌ Down"
                        result["Domain_Status"] = str(d["status_code"] or d.get("error", ""))
                    else:
                        result["Domain_Live"]   = "⚠️ No website"
                        result["Domain_Status"] = ""

                if check_email:
                    email = str(row.get("Email", ""))
                    if email and email not in ("N/A", "nan"):
                        e = verify_email_domain(email)
                        result["Email_MX"] = "✅ Valid" if e["mx_valid"] else f"❌ {e['error']}"
                    else:
                        result["Email_MX"] = "⚠️ No email"

                if ai_scoring and api_key:
                    try:
                        scored = score_lead(row.to_dict(), icp_criteria, api_key)
                        result["AI_Score"]   = scored["score"]
                        result["Confidence"] = f"{scored['confidence']:.0%}"
                        result["Reason"]     = scored["reason"]
                    except Exception as exc:
                        result["AI_Score"]   = "Error"
                        result["Confidence"] = "0%"
                        result["Reason"]     = str(exc)
                else:
                    demo = ["Hot","Hot","Warm","Warm","Cold","Warm","Hot","Cold"]
                    result["AI_Score"]   = demo[idx % len(demo)]
                    result["Confidence"] = f"{np.random.uniform(0.65, 0.95):.0%}"
                    result["Reason"]     = "Demo mode — add your OpenAI key for real AI scoring."

                results.append(result)
                time.sleep(0.04)

            progress_bar.progress(1.0, text="✅ Pipeline complete!")
            status_text.empty()
            results_df = pd.DataFrame(results)
            st.session_state.results_df = results_df

            hot  = int((results_df["AI_Score"] == "Hot").sum())
            warm = int((results_df["AI_Score"] == "Warm").sum())
            cold = int((results_df["AI_Score"] == "Cold").sum())
            st.balloons()
            st.success(f"🎉 Done! **{hot} Hot** · **{warm} Warm** · **{cold} Cold** — switch to **Results & Export**.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Results & Export
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    if st.session_state.results_df is None:
        st.info("⚡ Run the pipeline in **Verify & Score** to see results here.")
    else:
        df    = st.session_state.results_df
        total = len(df)
        hot   = int((df["AI_Score"] == "Hot").sum())
        warm  = int((df["AI_Score"] == "Warm").sum())
        cold  = int((df["AI_Score"] == "Cold").sum())

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🔥 Hot Leads",  hot,  f"{hot/total:.0%} of total")
        k2.metric("🟡 Warm Leads", warm, f"{warm/total:.0%} of total")
        k3.metric("🔵 Cold Leads", cold, f"{cold/total:.0%} of total")
        k4.metric("📋 Total",      total)
        st.divider()

        score_filter = st.multiselect("Filter by score:", ["Hot","Warm","Cold"],
                                      default=["Hot","Warm","Cold"])
        filtered = df[df["AI_Score"].isin(score_filter)]
        st.dataframe(filtered.style.map(_colour_score, subset=["AI_Score"]),
                     use_container_width=True, height=420)
        st.divider()

        ex1, ex2 = st.columns(2)
        with ex1:
            st.download_button("⬇️ Download Filtered Results (CSV)",
                filtered.to_csv(index=False).encode("utf-8"),
                "leadoptimizer_results.csv", "text/csv", use_container_width=True)
        with ex2:
            st.download_button("🔥 Download Hot Leads Only",
                df[df["AI_Score"]=="Hot"].to_csv(index=False).encode("utf-8"),
                "hot_leads.csv", "text/csv", use_container_width=True)

        st.divider()
        st.subheader("📈 Score Distribution")
        chart_data = df["AI_Score"].value_counts().rename_axis("Score").reset_index(name="Count")
        chart = (alt.Chart(chart_data)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Score:N", sort=["Hot","Warm","Cold"], axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Count:Q", axis=alt.Axis(tickMinStep=1)),
                color=alt.Color("Score:N", scale=alt.Scale(
                    domain=["Hot","Warm","Cold"],
                    range=["#16a34a","#d97706","#6b7280"]), legend=None),
                tooltip=["Score","Count"])
            .properties(height=320))
        st.altair_chart(chart, use_container_width=True)
