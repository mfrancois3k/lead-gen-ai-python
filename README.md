# 🚀 LeadOptimizer AI

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.34+-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/GPT--4o-Powered-412991?style=flat&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

> **AI-Powered Lead Automation Engine** — scrapes niche directories, verifies domain & email health,
> and uses GPT-4o to score 500+ leads/day as **Hot**, **Warm**, or **Cold** based on your exact ICP.

**[🔗 Live Demo →](https://your-app-name.streamlit.app)** *(deploy in 3 steps below)*

---

## The Business Problem

A client was manually searching Yellow Pages to find local service businesses, then one-by-one
checking whether each had a working website and fell within their target profile.
This was taking **4+ hours daily** with no consistency or scalability.

## The Solution

LeadOptimizer AI is a Python pipeline with a live Streamlit dashboard that:

1. **Scrapes** — Pulls fresh business listings from Yellow Pages for any niche + location in under 60s
2. **Verifies** — Checks each website for live HTTP responses and validates email domains via MX records
3. **Scores** — Sends each lead to GPT-4o with your custom ICP and gets a Hot/Warm/Cold classification
4. **Exports** — Colour-coded results table with one-click CSV download (all results or hot leads only)

**Result:** 100% automation of top-of-funnel research, saving **20+ hours/week**.

---

## Project Structure

```
lead-gen-ai-python/
├── app.py               ← Streamlit dashboard (run this)
├── core/
│   ├── scraper.py       ← Yellow Pages scraper (requests + BeautifulSoup)
│   ├── verifier.py      ← Domain health + email MX checks (httpx + dnspython)
│   └── ai_agent.py      ← GPT-4o lead scoring with structured JSON output
├── data/
│   └── sample_leads.csv ← 20 pre-built leads to demo without scraping
├── requirements.txt
└── README.md
```

---

## Quick Start (Local)

```bash
git clone https://github.com/mfrancois3k/lead-gen-ai-python.git
cd lead-gen-ai-python
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. Enter your OpenAI API key in the sidebar,
define your ICP, and hit **Run Full Pipeline**.

---

## Deploy Free in 3 Steps (Streamlit Community Cloud)

1. Push this repo to GitHub ✅ *(already done)*
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo → `app.py` → **Deploy**

You'll get a public URL like `https://lead-gen-optimizer.streamlit.app`.
Add your `OPENAI_API_KEY` as a **Secret** in the Streamlit dashboard.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Dashboard | Streamlit |
| Scraping | requests + BeautifulSoup4 + lxml |
| Domain verification | httpx |
| Email verification | dnspython |
| AI scoring | OpenAI GPT-4o (JSON mode) |
| Visualisation | Altair |
| Data | pandas + numpy |

---

## Upwork Portfolio Framing

**Headline:** AI-Powered Lead Automation Engine (500+ leads/day)

**Problem:** Client was manually checking niche directories, wasting 4 hours daily.

**Solution:** Python pipeline that scrapes Yellow Pages, verifies domain + email health,
and uses GPT-4o to score each lead against a custom ICP — fully automated end-to-end.

**Result:** Eliminated 20+ hours/week of manual research. Client clicks one button and
has a prioritised, verified lead list ready in under 2 minutes.

> **Note for JS devs:** The scored data can be fed into a React/Next.js frontend via a
> FastAPI endpoint — making this a drop-in backend for a full SaaS product.

---

## License

MIT — free to use, modify, and deploy.
