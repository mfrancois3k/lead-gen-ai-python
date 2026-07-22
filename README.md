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
├── .claude/
│   ├── skills/          ← AI Sales Team: /sales orchestrator + 13 sub-skills
│   └── agents/          ← 5 parallel Claude Code sub-agents
├── setup.sh             ← one-command install of skills/agents to ~/.claude
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

## 🤖 AI Sales Team — Claude Code Sub-Agents

This repo ships with the **AI Sales Team** suite for [Claude Code](https://docs.anthropic.com/en/docs/claude-code):
**14 skills + 5 sub-agents that run in parallel** to research prospects, qualify leads
(BANT + MEDDIC), find decision makers, write outreach sequences, prep meetings, and
generate client-ready PDF pipeline reports — the perfect companion to the lead lists
this app produces.

Credit: built by [Zubair Trabzada](https://github.com/zubair-trabzada/ai-sales-team-claude)
(AI Workshop — [skool.com/aiworkshop](https://www.skool.com/aiworkshop), free tier:
[skool.com/aiworkshop-lite](https://www.skool.com/aiworkshop-lite)). Vendored under MIT —
see `.claude/skills/sales/ATTRIBUTION.md`. His JARVIS voice-assistant pack lives in the
Skool community.

### Install on your machine (one command)

```bash
git pull
./setup.sh
```

This copies the skills to `~/.claude/skills` and the sub-agents to `~/.claude/agents`,
so `/sales` commands work in **any** project. (Opening Claude Code inside this repo also
works with zero install — the `.claude/` folder auto-loads project-level skills.)

### Commands

| Command | What it does |
|---|---|
| `/sales prospect <url>` | **Flagship** — full analysis with 5 sub-agents in parallel, returns a Prospect Score |
| `/sales quick <url>` | 60-second prospect snapshot |
| `/sales research <url>` | Deep company research |
| `/sales qualify <url>` | BANT + MEDDIC lead scoring |
| `/sales contacts <url>` | Find decision makers |
| `/sales outreach <prospect>` | Cold/warm/referral outreach sequences |
| `/sales followup <prospect>` | Follow-up sequences |
| `/sales prep <url>` | Meeting preparation brief |
| `/sales proposal <client>` | Client proposal generation |
| `/sales objections <topic>` | Objection-handling playbook |
| `/sales icp <description>` | Ideal Customer Profile builder |
| `/sales competitors <url>` | Competitive intelligence |
| `/sales report` / `report-pdf` | Pipeline report (Markdown / PDF) |

**Workflow tip:** run this app to scrape + score leads, export the hot list, then
`/sales prospect <url>` each hot lead for a full 5-agent deep-dive and outreach sequence.

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
