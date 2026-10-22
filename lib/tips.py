"""Daily tips: stored in lib/tips.json (a daily job appends entries). Only status=published entries are shown; use status=draft to stage one."""
import json, os, datetime
from email.utils import format_datetime
from . import config
from .views import page, E
from .guides import cta, GUIDES
PATH = os.path.join(os.path.dirname(__file__), "tips.json")
SCAN_LINE = "Run a free scan to see what your site exposes"
def _today():
    try:
        from zoneinfo import ZoneInfo; return datetime.datetime.now(ZoneInfo("America/Chicago")).date().isoformat()
    except Exception: return datetime.date.today().isoformat()
def load():
    with open(PATH) as f: return json.load(f)
def save(tips):
    with open(PATH, "w") as f: json.dump(tips, f, indent=2, ensure_ascii=False); f.write("\n")
def published():
    t = _today()
    return sorted([x for x in load() if x.get("status") == "published"], key=lambda x: x["date"], reverse=True)
def get(slug): return next((x for x in published() if x["slug"] == slug), None)
def url(t): return f"{config.BASE_URL}/tips/{t['slug']}"
def text(t): return "\n\n".join(t["body"]) + f"\n\n{t.get('cta', SCAN_LINE)}: {config.BASE_URL}"
def html_body(t): return "".join(f"<p>{E(p)}</p>" for p in t["body"]) + f"<p>{E(t.get('cta', SCAN_LINE))}: <a href='{config.BASE_URL}/'>{E(config.BASE_URL.split('//')[-1])}</a></p>"
# Pick the guide that goes deeper on a tip: an explicit "guide" slug in tips.json wins, else match words in the title.
GUIDE_WORDS = [("google", "why-google-cant-find-your-ai-built-app"), ("index", "why-google-cant-find-your-ai-built-app"), ("seo", "why-google-cant-find-your-ai-built-app"),
               ("rls", "supabase-rls-checklist"), ("row level", "supabase-rls-checklist"), ("supabase", "supabase-rls-checklist"),
               ("hide", "hide-api-keys-in-ai-built-apps"), ("key", "api-key-exposed-in-frontend"), ("secret", "api-key-exposed-in-frontend"),
               ("lovable", "is-my-lovable-app-secure"), ("secure", "is-my-lovable-app-secure")]
def guide_for(t):
    g = t.get("guide")
    if g in GUIDES: return g
    title = t["title"].lower()
    return next((s for w, s in GUIDE_WORDS if w in title), None)
def guide_link(t):
    g = guide_for(t)
    if not g: return ""
    return f"<div class=card><small>GO DEEPER</small><p style='margin:6px 0 0'>Read the full guide: <a href=/guides/{g}>{E(GUIDES[g]['title'])}</a></p></div>"
def render(slug):
    t = get(slug)
    if not t: return None
    return page(f"{t['title']} | {config.APP_NAME}", f"<small class=eyebrow>TIP · {E(t['date'])}</small><h1>{E(t['title'])}</h1>{html_body(t)}{guide_link(t)}{cta("tip")}",
                f"<link rel=alternate type=application/rss+xml title='{E(config.APP_NAME)} tips' href=/tips/rss.xml>", desc=t["body"][0][:155])
def index():
    items = "".join(f"<div class=card><small>{E(t['date'])}</small><h2 style='margin-top:4px'><a href=/tips/{t['slug']}>{E(t['title'])}</a></h2><p>{E(t['body'][0])}</p></div>" for t in published())
    return page(f"Tips | {config.APP_NAME}", f"<h1>Daily tips</h1><p class=sub>One short security or Google-visibility tip for apps built with AI tools. <a href=/tips/rss.xml>RSS feed</a></p>{items or '<p>No tips yet.</p>'}{cta("tips-index")}",
                f"<link rel=alternate type=application/rss+xml title='{E(config.APP_NAME)} tips' href=/tips/rss.xml>", desc="Short daily security and Google-visibility tips for apps built with Lovable, Bolt, Replit, v0 and Cursor.")
def _rfc822(d): return format_datetime(datetime.datetime.fromisoformat(d + "T11:00:00+00:00"))
def rss():
    X = lambda s: E(s, quote=True)
    items = "".join(f"<item><title>{X(t['title'])}</title><link>{url(t)}</link><guid isPermaLink=\"true\">{url(t)}</guid><pubDate>{_rfc822(t['date'])}</pubDate><description>{X(text(t))}</description></item>" for t in published())
    return (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{X(config.APP_NAME)} tips</title>'
            f"<link>{config.BASE_URL}/tips</link><atom:link href=\"{config.BASE_URL}/tips/rss.xml\" rel=\"self\" type=\"application/rss+xml\"/>"
            f"<description>Daily security and Google-visibility tips for apps built with AI tools.</description><language>en-us</language>{items}</channel></rss>")
