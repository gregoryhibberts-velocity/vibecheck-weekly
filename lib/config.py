import os
def env(k, d=None): return os.environ.get(k, d)
APP_NAME = env("APP_NAME", "VibeCheck Weekly")
BASE_URL = env("BASE_URL", "https://vibecheck.itsvelocitygroup.com").rstrip("/")
DATABASE_URL = env("DATABASE_URL") or env("POSTGRES_URL")   # Vercel Postgres/Neon/Supabase all provide one
SQLITE_PATH = env("SQLITE_PATH", "/tmp/appcheck-dev.db")       # local dev fallback only
ALLOW_PRIVATE_TARGETS = env("ALLOW_PRIVATE_TARGETS") == "1"    # local tests only; never set in production
CRON_SECRET = env("CRON_SECRET")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET")
STRIPE_PRICE_SOLO = env("STRIPE_PRICE_SOLO")   # $19/mo, 1 app
STRIPE_PRICE_PRO = env("STRIPE_PRICE_PRO")     # $49/mo, 5 apps
STRIPE_PRICE_UNLOCK = env("STRIPE_PRICE_UNLOCK") # $9 one-time full report
STRIPE_API_BASE = env("STRIPE_API_BASE", "https://api.stripe.com")
RESEND_AUDIENCE_ID = env("RESEND_AUDIENCE_ID")   # Resend Audience for sign-ups
EMAIL_PROVIDER = env("EMAIL_PROVIDER", "log")   # resend | postmark | log
EMAIL_API_KEY = env("EMAIL_API_KEY")
EMAIL_FROM = env("EMAIL_FROM", "VibeCheck Weekly <reports@example.com>")
EMAIL_API_BASE = env("EMAIL_API_BASE")          # override for mocks
RL_SCANS_PER_IP_HOUR = int(env("RL_SCANS_PER_IP_HOUR", "10"))
RL_FREE_SCANS_PER_IP_DAY = int(env("RL_FREE_SCANS_PER_IP_DAY", "10"))
RL_SCANS_PER_EMAIL_DAY = int(env("RL_SCANS_PER_EMAIL_DAY", "5"))
PLANS = {"solo": {"name": "Solo", "price": 19, "apps": 1}, "pro": {"name": "Pro", "price": 49, "apps": 5}}
