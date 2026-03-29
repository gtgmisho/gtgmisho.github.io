#!/usr/bin/env python3
"""
FREE SEO Content Pipeline
=========================
Groq (free AI) → Jekyll markdown articles → GitHub Pages (free hosting)

Setup:
  pip install -r requirements.txt
  # fill in config.py
  python pipeline.py

Cost: $0.00
"""

import os, json, re, time, base64, textwrap, requests
from datetime import datetime
from pathlib import Path
from config import (
    GROQ_API_KEY, GROQ_MODEL,
    GITHUB_TOKEN, GITHUB_USER, GITHUB_REPO, GITHUB_BRANCH,
    SITE_TITLE, SITE_URL,
    NICHE, SEED_TOPICS, ARTICLES_PER_RUN, MIN_WORD_COUNT,
)

# ── Groq client (OpenAI-compatible) ──────────────────────────────────────────
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
}

# ── GitHub API ────────────────────────────────────────────────────────────────
GH_API = "https://api.github.com"
GH_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

Path("generated_articles").mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
#  GROQ HELPER
# ─────────────────────────────────────────────────────────────────────────────
def groq(prompt: str, max_tokens: int = 4096, temp: float = 0.7) -> str:
    payload = {
        "model": GROQ_MODEL,
        "max_tokens": max_tokens,
        "temperature": temp,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(GROQ_URL, headers=GROQ_HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1 — KEYWORD EXPANSION
# ─────────────────────────────────────────────────────────────────────────────
def expand_keywords(seeds: list[str], n: int) -> list[dict]:
    print(f"\n🔍  Generating {n} keyword targets for: '{NICHE}'")
    prompt = textwrap.dedent(f"""
        You are an SEO expert in the niche: "{NICHE}".

        Seed topics:
        {json.dumps(seeds, indent=2)}

        Generate EXACTLY {n} long-tail keyword ideas (3–6 words each) suitable for blog articles.
        Mix informational and commercial intent.

        Reply ONLY with a JSON array — no markdown, no explanation:
        [
          {{
            "keyword": "...",
            "title": "...",
            "intent": "informational|commercial",
            "angle": "one sentence article angle"
          }}
        ]
    """).strip()

    raw = groq(prompt, max_tokens=1200, temp=0.5)
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    # extract JSON array robustly
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        raw = match.group(0)
    keywords = json.loads(raw)
    print(f"   ✅  {len(keywords)} keywords ready.")
    return keywords[:n]


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2 — ARTICLE WRITING
# ─────────────────────────────────────────────────────────────────────────────
def write_article(kw: dict) -> dict:
    print(f"\n✍️   Writing: {kw['title']}")
    prompt = textwrap.dedent(f"""
        You are an expert SEO content writer in the niche: "{NICHE}".

        Write a comprehensive blog article:
        Keyword : {kw['keyword']}
        Title   : {kw['title']}
        Intent  : {kw['intent']}
        Angle   : {kw['angle']}

        Requirements:
        - Minimum {MIN_WORD_COUNT} words
        - Use markdown headings (## and ###), bullet lists, numbered lists
        - Natural keyword usage (~1–2%)
        - Include a FAQ section with 3 questions near the end
        - First line must be: META: <meta description under 155 chars>
        - After META line, write the full article in markdown
        - Do NOT include a H1 title (it comes from front matter)
    """).strip()

    raw = groq(prompt, max_tokens=4096, temp=0.7)

    meta, body = "", raw
    if raw.startswith("META:"):
        lines = raw.split("\n", 2)
        meta = lines[0].replace("META:", "").strip()
        body = "\n".join(lines[1:]).strip()

    slug = re.sub(r"[^a-z0-9]+", "-", kw["title"].lower()).strip("-")
    word_count = len(re.sub(r"[#*`\[\]()]", "", body).split())

    print(f"   ✅  {word_count} words.")
    return {
        "keyword":    kw["keyword"],
        "title":      kw["title"],
        "intent":     kw["intent"],
        "meta":       meta,
        "body":       body,
        "word_count": word_count,
        "slug":       slug,
        "date":       datetime.now().strftime("%Y-%m-%d"),
    }


def to_jekyll(article: dict) -> str:
    """Wrap article body in Jekyll front matter."""
    front = textwrap.dedent(f"""\
        ---
        layout: post
        title: "{article['title'].replace('"', "'")}"
        date: {article['date']} 12:00:00 +0000
        categories: {NICHE.replace(' ', '-')}
        description: "{article['meta'].replace('"', "'")}"
        ---
    """)
    return front + "\n" + article["body"]


def save_locally(article: dict) -> str:
    fname = f"{article['date']}-{article['slug']}.md"
    path  = Path("generated_articles") / fname
    path.write_text(to_jekyll(article), encoding="utf-8")
    return str(path)


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3 — APPROVAL GATE
# ─────────────────────────────────────────────────────────────────────────────
def approval_gate(articles: list[dict]) -> list[dict]:
    print("\n" + "═" * 62)
    print("  📋  APPROVAL SUMMARY")
    print("═" * 62)
    for i, a in enumerate(articles, 1):
        print(f"\n  {i}. {a['title']}")
        print(f"     Words  : {a['word_count']}")
        print(f"     Intent : {a['intent']}")
        print(f"     Meta   : {a['meta'][:72]}…")
    print(f"\n  Will push to: https://github.com/{GITHUB_USER}/{GITHUB_REPO}")
    print(f"  Live at    : {SITE_URL}")
    print("═" * 62)
    ans = input("\n  ▶  Type 'yes' to publish, anything else to abort: ").strip().lower()
    if ans != "yes":
        print("\n  ⛔  Aborted. Articles saved locally in ./generated_articles/")
        return []
    return articles


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 4 — GITHUB PAGES PUBLISHING
# ─────────────────────────────────────────────────────────────────────────────
def get_file_sha(path: str) -> str | None:
    """Get SHA of existing file (needed to update it)."""
    r = requests.get(
        f"{GH_API}/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}",
        headers=GH_HEADERS,
    )
    if r.status_code == 200:
        return r.json().get("sha")
    return None


def push_to_github(article: dict) -> str:
    """Create or update a file in the GitHub repo."""
    fname   = f"{article['date']}-{article['slug']}.md"
    gh_path = f"_posts/{fname}"
    content = to_jekyll(article)
    encoded = base64.b64encode(content.encode()).decode()

    sha     = get_file_sha(gh_path)
    payload = {
        "message": f"Add post: {article['title']}",
        "content": encoded,
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha   # update existing file

    r = requests.put(
        f"{GH_API}/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{gh_path}",
        headers=GH_HEADERS,
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    url = f"{SITE_URL}/{article['date'].replace('-','/')}/{article['slug']}/"
    print(f"   🚀  Pushed → {gh_path}")
    return url


def ensure_jekyll_config():
    """Push a minimal _config.yml if repo is empty / new."""
    sha = get_file_sha("_config.yml")
    if sha:
        return  # already exists

    print("\n⚙️   First run — creating Jekyll config…")
    config_content = textwrap.dedent(f"""\
        title: {SITE_TITLE}
        description: "{NICHE.capitalize()} tips, guides and reviews."
        url: "{SITE_URL}"
        theme: minima

        plugins:
          - jekyll-feed
          - jekyll-seo-tag

        markdown: kramdown
        permalink: /:year/:month/:day/:title/
    """)
    payload = {
        "message": "Init Jekyll config",
        "content": base64.b64encode(config_content.encode()).decode(),
        "branch":  GITHUB_BRANCH,
    }
    r = requests.put(
        f"{GH_API}/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/_config.yml",
        headers=GH_HEADERS, json=payload, timeout=30,
    )
    if r.status_code in (200, 201):
        print("   ✅  _config.yml created.")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("\n🤖  FREE SEO PIPELINE  |  Groq + GitHub Pages")
    print(f"    Niche: {NICHE}  |  Articles: {ARTICLES_PER_RUN}  |  Cost: $0")
    start = time.time()

    # 1. Keywords
    keywords = expand_keywords(SEED_TOPICS, ARTICLES_PER_RUN)

    # 2. Write
    articles = []
    for kw in keywords:
        art = write_article(kw)
        save_locally(art)
        articles.append(art)
        time.sleep(2)  # respect Groq rate limits (30 req/min free tier)

    # 3. Approve
    approved = approval_gate(articles)
    if not approved:
        return

    # 4. Push to GitHub
    ensure_jekyll_config()
    print("\n🚀  Pushing to GitHub Pages…")
    published_urls = []
    for art in approved:
        try:
            url = push_to_github(art)
            published_urls.append({"title": art["title"], "url": url})
            time.sleep(1)
        except Exception as e:
            print(f"   ❌  Failed '{art['title']}': {e}")

    # 5. Report
    elapsed = round(time.time() - start, 1)
    report = {
        "run_at": datetime.now().isoformat(),
        "niche": NICHE,
        "articles_written": len(articles),
        "articles_published": len(published_urls),
        "elapsed_seconds": elapsed,
        "site": SITE_URL,
        "published": published_urls,
    }
    Path("pipeline_report.json").write_text(json.dumps(report, indent=2))

    print(f"\n✅  Done in {elapsed}s — {len(published_urls)} articles live.")
    print(f"    Site: {SITE_URL}  (GitHub Pages builds in ~60s)")
    print(f"    Report: pipeline_report.json")


if __name__ == "__main__":
    main()
