# 🤖 Free SEO Pipeline
**Cost: $0/month. Forever.**

Groq (free AI) → Jekyll markdown → GitHub Pages (free hosting)

---

## One-time setup (~10 minutes)

### 1. Get a free Groq API key
- Go to **console.groq.com** → sign up → API Keys → Create key
- It's free, no credit card needed
- Free tier: 30 requests/min, 14,400 req/day — more than enough

### 2. Create your GitHub Pages repo
- Go to **github.com/new**
- Name it exactly: `YOUR_USERNAME.github.io`
- Set to Public
- Go to **Settings → Pages → Source → GitHub Actions**

### 3. Get a GitHub token
- Go to **github.com → Settings → Developer settings**
- → **Personal access tokens → Fine-grained tokens → Generate new token**
- Permissions needed: **Contents** → Read and Write
- Copy the token

### 4. Fill in config.py
```python
GROQ_API_KEY  = "gsk_..."
GITHUB_TOKEN  = "github_pat_..."
GITHUB_USER   = "yourusername"
GITHUB_REPO   = "yourusername.github.io"
NICHE         = "your niche"
```

### 5. Install & run
```bash
pip install -r requirements.txt
python pipeline.py
```

### 6. Type `yes` when prompted

Articles go live at `https://yourusername.github.io` within ~60 seconds of pushing.

---

## How to make money from it

### Option A — Google AdSense
- Apply once you have 10–20 articles
- Add your AdSense code to Jekyll's `_layouts/post.html`
- Earns $1–5 per 1,000 pageviews

### Option B — Affiliate links
- Sign up for Amazon Associates or a niche affiliate program
- Ask the pipeline to weave in product recommendations
- Earns 3–10% commission per sale

### Option C — Sell a digital product
- Create a simple PDF guide / checklist / template on Gumroad (free)
- Link to it from every article
- Earns $5–50 per sale

---

## Running on a schedule (fully automated)

Add a cron job to run weekly with no interaction using `--auto` flag:

```bash
# crontab -e
0 9 * * 1 cd /path/to/pipeline && python pipeline.py --auto >> pipeline.log 2>&1
```

Add `--auto` support in pipeline.py by replacing the `input()` call:
```python
import sys
auto = "--auto" in sys.argv
ans  = "yes" if auto else input("  ▶  Type 'yes' to publish: ").strip().lower()
```

---

## Cost breakdown

| Item | Cost |
|------|------|
| Groq API | **$0** (free tier) |
| GitHub Pages | **$0** (free forever) |
| Domain (optional) | ~$12/yr from Namecheap |
| **Total** | **$0/mo** (or $1/mo with domain) |

---

## Niche ideas that work well

- Personal finance tips
- Budget travel guides  
- Python / coding tutorials
- Home improvement DIY
- Pet care advice
- Fitness & nutrition
- Gardening

Pick a niche with Amazon products or affiliate programs for best monetisation.
