# ============================================================
#  FREE SEO PIPELINE — CONFIG
#  Groq (free AI) + GitHub Pages (free hosting)
# ============================================================

# --- Groq API (free at console.groq.com) ---
GROQ_API_KEY = "gsk_YOUR_KEY_HERE"
GROQ_MODEL   = "llama3-70b-8192"   # best free model on Groq

# --- GitHub ---
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"   # Settings → Developer settings → Personal access tokens → Fine-grained
GITHUB_USER  = "your-github-username"
GITHUB_REPO  = "your-github-username.github.io"  # must be this format for GitHub Pages
GITHUB_BRANCH = "main"

# --- Your site ---
SITE_TITLE   = "My Niche Blog"
SITE_URL     = "https://your-github-username.github.io"  # or custom domain

# --- Niche & Strategy ---
NICHE        = "home coffee brewing"
SEED_TOPICS  = [
    "best espresso machines under $200",
    "how to make cold brew at home",
    "french press vs pour over",
    "coffee grinder buying guide",
    "how to store coffee beans",
]

# --- Volume ---
ARTICLES_PER_RUN = 5
MIN_WORD_COUNT   = 1200
