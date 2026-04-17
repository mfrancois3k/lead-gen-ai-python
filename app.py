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
from core.scraper   import scrape_yellow_pages
from core.verifier  import verify_domain, verify_email_domain
from core.ai_agent  import score_lead

st.set_page_config(page_title="LeadOptimizer AI", page_icon="🚀",
                   layout="wide", initial_sidebar_state="expanded")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hero */
.hero{background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%);
      padding:2rem 2.5rem;border-radius:14px;margin-bottom:1.5rem;
      color:#fff;text-align:center;}
.hero h1{margin:0 0 .3rem;font-size:2.1rem;}
.hero p{margin:0;opacity:.85;font-size:.95rem;}

/* Step headers */
.step-row{display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;}
.badge{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;
       justify-content:center;font-size:.8rem;font-weight:700;flex-shrink:0;margin-top:1px;}
.badge-active{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;}
.badge-done{background:#16a34a;color:#fff;}
.badge-idle{background:#e5e7eb;color:#9ca3af;}
.step-title{font-weight:600;font-size:.9rem;color:#1f2937;line-height:1.2;}
.step-sub{font-size:.75rem;color:#9ca3af;margin-top:1px;}

/* Feature list box */
.feat-box{background:linear-gradient(135deg,#eef2ff,#f5f3ff);
          border:1px solid #c7d2fe;border-radius:10px;padding:10px 12px;}
.feat-row{display:flex;align-items:center;gap:8px;font-size:.78rem;
          color:#3730a3;padding:3px 0;}

/* Primary CTA button */
div.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,#4f46e5,#7c3aed)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:700!important;font-size:.95rem!important;padding:.6rem 1.5rem!important;}

/* Score table colours */
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
for k in ("leads_df", "results_df"):
    if k not in st.session_state:
        st.session_state[k] = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🚀 LeadOptimizer AI")
    st.caption("Follow the 3 steps below to get started")
    st.divider()

    # ── STEP 1: API Key ───────────────────────────────────────────────────────
    api_key   = st.session_state.get("api_key", "")
    step1done = len(api_key) > 10

    b1 = "badge-done" if step1done else "badge-active"
    n1 = "✓" if step1done else "1"
    st.markdown(f"""
    <div class="step-row">
      <div class="badge {b1}">{n1}</div>
      <div>
        <div class="step-title">Get Your API Key</div>
        <div class="step-sub">Powers the GPT-4o scoring engine</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.link_button("🔗 OpenAI — Get a free API key",
                   "https://platform.openai.com/api-keys",
                   use_container_width=True)

    raw_key = st.text_input("API Key", type="password",
                            placeholder="Paste your key  sk-...",
                            label_visibility="collapsed",
                            value=api_key)
    if raw_key:
        st.session_state["api_key"] = raw_key
        api_key   = raw_key
        step1done = len(api_key) > 10

    if step1done:
        st.success("✅ Key saved — move to Step 2", icon="🔑")

    st.divider()

    # ── STEP 2: Load Leads ────────────────────────────────────────────────────
    step2done = st.session_state.leads_df is not None
    b2 = "badge-done" if step2done else ("badge-active" if step1done else "badge-idle")
    n2 = "✓" if step2done else "2"
    st.markdown(f"""
    <div class="step-row">
      <div class="badge {b2}">{n2}</div>
      <div>
        <div class="step-title">Load Your Leads</div>
        <div class="step-sub">Upload a CSV or scrape Yellow Pages</div>
      </div>
    </div>""", unsafe_allow_html=True)

    if step1done:
        uploaded = st.file_uploader("CSV file", type="csv",
                                    label_visibility="collapsed")
        if uploaded:
            st.session_state.leads_df = pd.read_csv(uploaded)
            st.success(f"✅ {uploaded.name} loaded ({len(st.session_state.leads_df)} rows)")

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("🌐 Scrape Yellow Pages", use_container_width=True):
                st.session_state["goto_scrape"] = True
        with c2:
            if st.button("📋 Sample leads", use_container_width=True):
                p = os.path.join(os.path.dirname(__file__), "data", "sample_leads.csv")
                st.session_state.leads_df = pd.read_csv(p)
                st.rerun()

        if step2done and not uploaded:
            n = len(st.session_state.leads_df)
            st.success(f"✅ {n} leads loaded — move to Step 3")
    else:
        st.caption("_Complete Step 1 first_")

    st.divider()

    # ── STEP 3: Run the Pipeline ──────────────────────────────────────────────
    step3ready = step1done and step2done
    b3 = "badge-active" if step3ready else "badge-idle"
    st.markdown(f"""
    <div class="step-row">
      <div class="badge {b3}">3</div>
      <div>
        <div class="step-title">Run the Pipeline</div>
        <div class="step-sub">Switch to "Verify & Score" → click the button</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="feat-box">
      <div class="feat-row">🔍 Checks every domain is live</div>
      <div class="feat-row">📧 Validates email MX records</div>
      <div class="feat-row">🤖 GPT-4o scores each lead Hot / Warm / Cold</div>
      <div class="feat-row">⬇️ Download results as CSV instantly</div>
    </div>""", unsafe_allow_html=True)

    if step3ready:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("⚡ Head to the **Verify & Score** tab and hit **Run Full Pipeline**", icon="👆")

    st.divider()

    # ── ADVANCED SETTINGS (collapsible) ───────────────────────────────────────
    with st.expander("⚙️ Advanced Settings"):
        icp_criteria = st.text_area("🎯 Ideal Customer Profile", height=180,
            value=("Local service business (plumber, HVAC, roofer, landscaper) that:\n"
                   "- Has been operating for 2+ years\n"
                   "- Has a website (even a basic one)\n"
                   "- Serves residential customers\n"
                   "- Has 4+ star reviews online\n"
                   "- Located in a metro area (100k+ population)\n"
                   "- Does NOT yet have a lead generation system"))
        st.markdown("**Pipeline options**")
        check_domain = st.checkbox("Check domain health",     value=True)
        check_email  = st.checkbox("Verify email MX records", value=True)
        ai_scoring   = st.checkbox("Enable GPT-4o scoring",   value=True)
    
    # persist icp + options even outside expander scope
    if "icp_criteria" not in dir(): icp_criteria = ""
    if "check_domain" not in dir(): check_domain = True
    if "check_email"  not in dir(): check_email  = True
    if "ai_scoring"   not in dir(): ai_scoring   = True

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""<div class="hero">
  <h1>🚀 LeadOptimizer AI</h1>
  <p>Scrape · Verify · Score 500+ local service leads per day — powered by GPT-4o</p>
</div>""", unsafe_allow_html=True)

# ── State-driven landing if not ready ────────────────────────────────────────
if not step1done:
    st.info("👈 **Step 1:** Paste your OpenAI API key in the sidebar to get started.", icon="🔑")
    st.stop()

if not step2done:
    st.info("👈 **Step 2:** Upload a CSV or click 'Sample leads' in the sidebar.", icon="📂")
    st.stop()

# ── Tabs (only shown when steps 1 & 2 are done) ───────────────────────────────
tab1, tab2, tab3 = st.tabs(["📤 Load Leads", "⚡ Verify & Score", "📊 Results & Export"])

SCORE_COLOURS = {
    "Hot":  "background-color:#dcfce7;color:#14532d",
    "Warm": "background-color:#fef9c3;color:#713f12",
    "Cold": "background-color:#f3f4f6;color:#374151",
}
def _colour_score(val): return SCORE_COLOURS.get(val, "")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Load Leads
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col_up, col_sc = st.columns(2, gap="large")

    with col_up:
        st.subheader("📁 Manage Your Lead List")
        df_cur = st.session_state.leads_df
        if df_cur is not None:
            st.success(f"✅ **{len(df_cur):,}** leads currently loaded")
            st.dataframe(df_cur.head(8), use_container_width=True)
        up2 = st.file_uploader("Replace with a new CSV", type="csv")
        if up2:
            st.session_state.leads_df = pd.read_csv(up2)
            st.rerun()

    with col_sc:
        st.subheader("🌐 Scrape Yellow Pages")
        st.caption("Pull fresh leads for any niche + city.")
        niche = st.selectbox("Niche", ["Plumbers","HVAC Contractors","Roofers",
            "Landscapers","Electricians","Painters","General Contractors",
            "Pest Control","Pool Service","Garage Door Repair"])
        location    = st.text_input("Location", value="Dallas, TX")
        max_results = st.slider("Max results", 10, 100, 25, 5)
        if st.button("🔍 Scrape Now", type="primary"):
            with st.spinner(f"Scraping {niche} in {location}…"):
                leads = scrape_yellow_pages(niche, location, max_results)
            if leads:
                st.session_state.leads_df = pd.DataFrame(leads)
                st.success(f"✅ {len(leads)} listings found!")
                st.rerun()
            else:
                st.error("No results returned. Try a different niche or location.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Verify & Score
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    df = st.session_state.leads_df.copy()
    n  = len(df)

    st.subheader(f"⚡ {n:,} leads ready to process")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total Leads",    f"{n:,}")
    m2.metric("Domain Check",   "✅ On" if check_domain else "⏭ Off")
    m3.metric("Email MX",       "✅ On" if check_email  else "⏭ Off")
    m4.metric("AI Scoring",     "GPT-4o" if (ai_scoring and api_key) else "Demo")
    st.divider()

    if ai_scoring and not api_key:
        st.warning("⚠️ No API key — running in demo mode (simulated scores).")

    if st.button("🚀 Run Full Pipeline", type="primary", use_container_width=True):
        bar   = st.progress(0.0, text="Starting…")
        msg   = st.empty()
        rows  = []

        for idx, row in df.iterrows():
            pct  = (idx+1)/n
            name = row.get("Business Name", f"Lead #{idx+1}")
            bar.progress(pct, text=f"Processing {idx+1}/{n}: {name}")
            msg.caption(f"🔍 Verifying: **{name}**")
            result = row.to_dict()

            if check_domain:
                w = str(row.get("Website",""))
                if w and w not in ("N/A","nan"):
                    d = verify_domain(w)
                    result["Domain_Live"]   = "✅ Live" if d["domain_live"] else "❌ Down"
                    result["Domain_Status"] = str(d["status_code"] or d.get("error",""))
                else:
                    result["Domain_Live"] = "⚠️ No website"; result["Domain_Status"] = ""

            if check_email:
                e = str(row.get("Email",""))
                if e and e not in ("N/A","nan"):
                    ev = verify_email_domain(e)
                    result["Email_MX"] = "✅ Valid" if ev["mx_valid"] else f"❌ {ev['error']}"
                else:
                    result["Email_MX"] = "⚠️ No email"

            if ai_scoring and api_key:
                try:
                    sc = score_lead(row.to_dict(), icp_criteria, api_key)
                    result["AI_Score"]   = sc["score"]
                    result["Confidence"] = f"{sc['confidence']:.0%}"
                    result["Reason"]     = sc["reason"]
                except Exception as exc:
                    result["AI_Score"]="Error"; result["Confidence"]="0%"; result["Reason"]=str(exc)
            else:
                demo = ["Hot","Hot","Warm","Warm","Cold","Warm","Hot","Cold"]
                result["AI_Score"]   = demo[idx % len(demo)]
                result["Confidence"] = f"{np.random.uniform(0.65,0.95):.0%}"
                result["Reason"]     = "Demo mode — add your OpenAI key for real AI scoring."

            rows.append(result)
            time.sleep(0.04)

        bar.progress(1.0, text="✅ Done!")
        msg.empty()
        st.session_state.results_df = pd.DataFrame(rows)
        hot  = int((st.session_state.results_df["AI_Score"]=="Hot").sum())
        warm = int((st.session_state.results_df["AI_Score"]=="Warm").sum())
        cold = int((st.session_state.results_df["AI_Score"]=="Cold").sum())
        st.balloons()
        st.success(f"🎉 Done! **{hot} Hot** · **{warm} Warm** · **{cold} Cold** — see Results & Export tab.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Results & Export
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    if st.session_state.results_df is None:
        st.info("⚡ Run the pipeline in **Verify & Score** to see results here.")
    else:
        df    = st.session_state.results_df
        total = len(df)
        hot   = int((df["AI_Score"]=="Hot").sum())
        warm  = int((df["AI_Score"]=="Warm").sum())
        cold  = int((df["AI_Score"]=="Cold").sum())

        k1,k2,k3,k4 = st.columns(4)
        k1.metric("🔥 Hot",   hot,  f"{hot/total:.0%}")
        k2.metric("🟡 Warm",  warm, f"{warm/total:.0%}")
        k3.metric("🔵 Cold",  cold, f"{cold/total:.0%}")
        k4.metric("📋 Total", total)
        st.divider()

        filt = st.multiselect("Filter by score:", ["Hot","Warm","Cold"],
                              default=["Hot","Warm","Cold"])
        filtered = df[df["AI_Score"].isin(filt)]
        st.dataframe(filtered.style.map(_colour_score, subset=["AI_Score"]),
                     use_container_width=True, height=400)
        st.divider()

        c1, c2 = st.columns(2)
        c1.download_button("⬇️ Download Filtered Results",
            filtered.to_csv(index=False).encode(), "leadoptimizer_results.csv",
            "text/csv", use_container_width=True)
        c2.download_button("🔥 Download Hot Leads Only",
            df[df["AI_Score"]=="Hot"].to_csv(index=False).encode(), "hot_leads.csv",
            "text/csv", use_container_width=True)

        st.divider()
        st.subheader("📈 Score Distribution")
        chart_data = df["AI_Score"].value_counts().rename_axis("Score").reset_index(name="Count")
        chart = (alt.Chart(chart_data)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Score:N", sort=["Hot","Warm","Cold"],
                         axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Count:Q", axis=alt.Axis(tickMinStep=1)),
                color=alt.Color("Score:N", scale=alt.Scale(
                    domain=["Hot","Warm","Cold"],
                    range=["#16a34a","#d97706","#6b7280"]), legend=None),
                tooltip=["Score","Count"])
            .properties(height=300))
        st.altair_chart(chart, use_container_width=True)
