#!/usr/bin/env python3
"""Static blog generator for ctfdesigns.com/blog.
Reads blog/posts/*.md (YAML-ish frontmatter + markdown body) and emits:
  blog/index.html         — post listing
  blog/<slug>.html        — each post
Wrapped in the CTF Designs chrome (nav, footer, ADA widget, cookie banner,
chat widget, newsletter popup). No external deps — mini markdown renderer.
Run: python3 build_blog.py
"""
import os, re, html, glob

ROOT = "/Users/roman/ctfdesigns"
POSTS = os.path.join(ROOT, "blog", "posts")
OUT = os.path.join(ROOT, "blog")
SITE = "https://ctfdesigns.com"

# ---------------- frontmatter + markdown ----------------
def parse(md):
    meta, body = {}, md
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    return meta, body

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" loading="lazy">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t

def render_md(md):
    out, i = [], 0
    lines = md.split("\n")
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if re.match(r"^#{1,4}\s", ln):
            lvl = len(ln) - len(ln.lstrip("#"))
            out.append(f"<h{lvl+1}>{inline(ln.lstrip('# ').strip())}</h{lvl+1}>")
            i += 1; continue
        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                txt = re.sub(r"^\s*[-*]\s+", "", lines[i])
                items.append("<li>" + inline(txt) + "</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        if re.match(r"^\s*\d+\.\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                txt = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                items.append("<li>" + inline(txt) + "</li>"); i += 1
            out.append("<ol>" + "".join(items) + "</ol>"); continue
        if re.match(r"^>\s?", ln):
            buf = []
            while i < len(lines) and re.match(r"^>\s?", lines[i]):
                buf.append(inline(re.sub(r"^>\s?", "", lines[i]))); i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>"); continue
        if re.match(r"^---+\s*$", ln):
            out.append("<hr>"); i += 1; continue
        # paragraph (gather until blank)
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|\s*[-*]\s|\s*\d+\.\s|>|---+\s*$)", lines[i]):
            buf.append(inline(lines[i])); i += 1
        out.append("<p>" + "<br>".join(buf) + "</p>")
    return "\n".join(out)

# ---------------- chrome ----------------
GA = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-0X9Q4PV3XT"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-0X9Q4PV3XT');</script>
<script>
  !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug getPageViewId captureTraceFeedback captureTraceMetric".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
  posthog.init('phc_kriY6oLdrzX5te5K5BD2tByomTBNDY7MShafdbTSJB3E',{api_host:'https://us.i.posthog.com',person_profiles:'always'});
</script>"""

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#ffffff;--bg-soft:#fbf6ef;--grad:linear-gradient(100deg,#ffb03a 0%,#ff7a1a 48%,#e5431b 100%);--accent:#7c3aed;--orange:#ff7a1a;--text:#14121a;--muted:#5b5568;--card:#ffffff;--card-border:#e9e6f0;--radius:14px}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;line-height:1.7;overflow-x:hidden}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif;line-height:1.15;letter-spacing:-.02em}
a{color:inherit}
.container{max-width:1180px;margin:0 auto;padding:0 5%}
.grad-text{background:var(--grad);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
#navbar{position:fixed;top:0;left:0;right:0;z-index:1000;display:flex;align-items:center;justify-content:space-between;padding:.5rem 5%;background:rgba(255,255,255,.82);backdrop-filter:blur(14px);border-bottom:1px solid transparent;transition:border-color .3s,background .3s}
#navbar.scrolled{border-bottom-color:var(--card-border);background:rgba(255,255,255,.94)}
.nav-logo img{height:42px;width:auto;border-radius:50%;box-shadow:0 0 0 2px rgba(20,18,26,.06)}
.nav-links{display:flex;gap:1.6rem;list-style:none}
.nav-links a{color:var(--muted);text-decoration:none;font-weight:500;font-size:.95rem;transition:color .2s}
.nav-links a:hover,.nav-links a.active{color:var(--accent)}
.btn{display:inline-flex;align-items:center;padding:.65rem 1.5rem;border-radius:999px;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:.9rem;text-decoration:none;cursor:pointer;border:none;transition:transform .2s,box-shadow .2s}
.btn-grad{background:var(--grad);color:#fff;box-shadow:0 8px 22px rgba(255,122,26,.28)}
.btn-grad:hover{transform:translateY(-2px);box-shadow:0 12px 30px rgba(255,122,26,.4)}
.hamburger{display:none;flex-direction:column;gap:5px;background:none;border:none;cursor:pointer;padding:4px}
.hamburger span{display:block;width:24px;height:2px;background:var(--text);border-radius:2px;transition:all .3s}
.hamburger.open span:nth-child(1){transform:translateY(7px) rotate(45deg)}
.hamburger.open span:nth-child(2){opacity:0}
.hamburger.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
.mobile-menu{display:none;position:fixed;top:64px;left:0;right:0;background:rgba(255,255,255,.98);backdrop-filter:blur(14px);border-bottom:1px solid var(--card-border);padding:1.5rem 5%;z-index:999;flex-direction:column;gap:1.25rem}
.mobile-menu.open{display:flex}
.mobile-menu a{color:var(--text);text-decoration:none;font-size:1.1rem;font-weight:500}
.blog-hero{padding:9rem 0 2.5rem;text-align:center;background:radial-gradient(900px 480px at 82% -14%,rgba(255,122,26,.14),transparent 55%),radial-gradient(760px 460px at 6% 4%,rgba(255,170,80,.16),transparent 55%),var(--bg-soft)}
.blog-hero .kicker{font-family:'Space Grotesk',sans-serif;font-weight:700;letter-spacing:.18em;text-transform:uppercase;font-size:.8rem;color:var(--accent);margin-bottom:1rem}
.blog-hero h1{font-size:clamp(2.4rem,6vw,3.6rem)}
.blog-hero p{color:var(--muted);max-width:620px;margin:1rem auto 0;font-size:1.08rem}
.post-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:1.6rem;padding:2.4rem 0 5rem}
.post-card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--card-border);border-radius:16px;overflow:hidden;text-decoration:none;color:inherit;transition:transform .2s,box-shadow .2s,border-color .2s}
.post-card:hover{transform:translateY(-5px);box-shadow:0 22px 44px rgba(20,18,26,.09);border-color:transparent}
.post-card .thumb{aspect-ratio:16/9;background:var(--grad);display:flex;align-items:center;justify-content:center;font-family:'Space Grotesk',sans-serif;font-weight:700;color:#fff;font-size:1.1rem;padding:1rem;text-align:center}
.post-card .thumb img{width:100%;height:100%;object-fit:cover}
.post-card .pc-body{padding:1.3rem 1.4rem 1.5rem}
.post-card .meta{font-size:.78rem;color:var(--muted);margin-bottom:.5rem}
.post-card h3{font-size:1.22rem;margin-bottom:.5rem}
.post-card p{color:var(--muted);font-size:.93rem}
.post-card .more{margin-top:1rem;color:var(--orange);font-weight:600;font-size:.9rem}
.article{max-width:760px;margin:0 auto;padding:7.5rem 5% 4rem}
.article .back{color:var(--muted);text-decoration:none;font-size:.9rem}
.article .kicker{font-family:'Space Grotesk',sans-serif;font-weight:700;letter-spacing:.16em;text-transform:uppercase;font-size:.78rem;color:var(--accent);margin:1.4rem 0 .6rem}
.article h1{font-size:clamp(2rem,5vw,2.9rem);margin-bottom:.8rem}
.article .byline{color:var(--muted);font-size:.9rem;margin-bottom:2rem}
.post-body{font-size:1.07rem}
.post-body h2{font-size:1.6rem;margin:2.2rem 0 .8rem}
.post-body h3{font-size:1.28rem;margin:1.8rem 0 .6rem}
.post-body p{margin:0 0 1.1rem;color:#3a3546}
.post-body ul,.post-body ol{margin:0 0 1.2rem 1.3rem;color:#3a3546}
.post-body li{margin-bottom:.5rem}
.post-body a{color:var(--orange);font-weight:600}
.post-body blockquote{border-left:3px solid var(--orange);padding:.4rem 0 .4rem 1.2rem;margin:1.4rem 0;color:var(--muted);font-style:italic}
.post-body img{max-width:100%;border-radius:12px;margin:1.4rem 0}
.post-body code{background:#f3f0f7;padding:.15em .45em;border-radius:6px;font-size:.92em}
.post-body hr{border:none;border-top:1px solid var(--card-border);margin:2rem 0}
.cta-card{margin:3rem auto 0;max-width:760px;background:linear-gradient(rgba(124,58,237,.05),rgba(255,122,26,.07));border:1px solid var(--card-border);border-radius:16px;padding:2rem;text-align:center}
.cta-card h3{font-size:1.5rem;margin-bottom:.6rem}
.cta-card p{color:var(--muted);margin-bottom:1.3rem}
footer{border-top:1px solid var(--card-border);padding:3rem 0 2rem;background:#100a06;color:#c4af98}
.footer-inner{max-width:1180px;margin:0 auto;padding:0 5%}
.footer-top{display:flex;justify-content:space-between;gap:2rem;flex-wrap:wrap;margin-bottom:2rem}
.footer-brand img{height:52px;border-radius:50%}
.footer-brand p{color:#c4af98;font-size:.9rem;margin-top:.8rem;max-width:280px}
.footer-links{display:flex;gap:3rem;flex-wrap:wrap}
.footer-col h4{font-size:.95rem;margin-bottom:.8rem;color:#fff}
.footer-col ul{list-style:none}
.footer-col li{margin-bottom:.5rem}
.footer-col a{color:#c4af98;text-decoration:none;font-size:.9rem}
.footer-col a:hover{color:#fff}
.footer-bottom{border-top:1px solid rgba(255,255,255,.1);padding-top:1.5rem;display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem}
.footer-bottom p{color:#c4af98;font-size:.82rem}
.easter-egg{opacity:.85}
.cookie-banner{position:fixed;bottom:0;left:0;right:0;z-index:9998;background:rgba(255,255,255,.97);backdrop-filter:blur(14px);border-top:1px solid var(--card-border);padding:1.25rem 5%;display:flex;align-items:center;justify-content:space-between;gap:1.5rem;flex-wrap:wrap;transform:translateY(100%);transition:transform .4s}
.cookie-banner.visible{transform:translateY(0)}
.cookie-banner p{font-size:.9rem;color:var(--muted);flex:1;min-width:200px}
.cookie-banner a{color:var(--accent);text-decoration:none}
.cookie-actions{display:flex;align-items:center;gap:1rem}
.cookie-dismiss{background:none;border:none;color:var(--muted);font-size:1.3rem;cursor:pointer}
@media(max-width:820px){.nav-links{display:none}.hamburger{display:flex}.footer-top{flex-direction:column}.blog-hero{padding-top:7rem}}
"""

NAV = """<nav id="navbar">
  <a href="/index.html" class="nav-logo" aria-label="CTF Designs home"><img src="/images/logo-sm.png" alt="CTF Designs"></a>
  <ul class="nav-links">
    <li><a href="/work.html">Work</a></li>
    <li><a href="/services.html">Services</a></li>
    <li><a href="/about.html">About</a></li>
    <li><a href="/blog/" class="active">Blog</a></li>
    <li><a href="/pricing.html">Pricing</a></li>
    <li><a href="/contact.html">Contact</a></li>
  </ul>
  <a href="/contact.html" class="btn btn-grad" style="font-size:.85rem;padding:.6rem 1.25rem;">Get a quote</a>
  <button class="hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
</nav>
<div class="mobile-menu" id="mobile-menu">
  <a href="/work.html" class="mobile-link">Work</a>
  <a href="/services.html" class="mobile-link">Services</a>
  <a href="/about.html" class="mobile-link">About</a>
  <a href="/blog/" class="mobile-link">Blog</a>
  <a href="/pricing.html" class="mobile-link">Pricing</a>
  <a href="/contact.html" class="mobile-link">Contact</a>
  <a href="/contact.html" class="btn btn-grad" style="width:fit-content;margin-top:.5rem;">Get a quote</a>
</div>"""

FOOTER = """<footer>
  <div class="footer-inner">
    <div class="footer-top">
      <div class="footer-brand">
        <a href="/index.html" class="nav-logo"><img src="/images/logo-sm.png" alt="CTF Designs"></a>
        <p>Built by humans. Powered by results.<br>Web design &amp; development for businesses ready to grow.</p>
        <div style="display:flex;gap:14px;margin-top:16px"><a href="https://facebook.com/ctfdesigns" target="_blank" rel="noopener" aria-label="Facebook" style="color:#c4af98"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.2c-1.2 0-1.6.8-1.6 1.6V12h2.7l-.4 2.9h-2.3v7A10 10 0 0 0 22 12z"/></svg></a><a href="https://instagram.com/ctfdesigns" target="_blank" rel="noopener" aria-label="Instagram" style="color:#c4af98"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/></svg></a><a href="https://www.linkedin.com/in/roman-vaxman-49a93a73/" target="_blank" rel="noopener" aria-label="LinkedIn" style="color:#c4af98"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.07 2.07 0 1 1 0-4.14 2.07 2.07 0 0 1 0 4.14zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg></a></div>
      </div>
      <div class="footer-links">
        <div class="footer-col"><h4>Pages</h4><ul>
          <li><a href="/index.html">Home</a></li><li><a href="/about.html">About</a></li>
          <li><a href="/blog/">Blog</a></li><li><a href="/pricing.html">Pricing</a></li>
          <li><a href="/contact.html">Contact</a></li></ul></div>
        <div class="footer-col"><h4>Services</h4><ul>
          <li><a href="/index.html#services">Web Design</a></li><li><a href="/index.html#services">E-Commerce</a></li>
          <li><a href="/index.html#services">Maintenance</a></li><li><a href="/index.html#services">Domain Setup</a></li></ul></div>
        <div class="footer-col"><h4>Legal</h4><ul>
          <li><a href="/privacy.html">Privacy Policy</a></li><li><a href="/cookies.html">Cookie Policy</a></li>
          <li><a href="/accessibility.html">Accessibility</a></li></ul></div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 CTF Designs. All rights reserved. &mdash; Murrieta, CA</p>
      <p class="easter-egg">Named after Cheddar The Floof 🐾</p>
    </div>
  </div>
</footer>"""

A11Y = """<script src="https://ctf-widgets.netlify.app/v1/ada.js" defer data-position="bottom-left" data-color="#7C3AED" data-statement="/accessibility.html"></script>
<div class="cookie-banner" id="cookieBanner" role="region" aria-label="Cookie consent">
  <p>We use cookies to improve your experience. By continuing, you agree to our <a href="/cookies.html">Cookie Policy</a>.</p>
  <div class="cookie-actions">
    <a href="/cookies.html" style="color:var(--muted);font-size:.85rem;text-decoration:none;">Cookie Settings</a>
    <button class="btn btn-grad" id="cookieAccept" style="font-size:.85rem;padding:.5rem 1.1rem;">Accept</button>
    <button class="cookie-dismiss" id="cookieDismiss" aria-label="Close">&times;</button>
  </div>
</div>"""

SCRIPTS = """<script>
var navbar=document.getElementById('navbar');
window.addEventListener('scroll',function(){navbar.classList.toggle('scrolled',window.scrollY>20);},{passive:true});
var hb=document.getElementById('hamburger'),mm=document.getElementById('mobile-menu');
hb.addEventListener('click',function(){var o=mm.classList.toggle('open');hb.classList.toggle('open',o);hb.setAttribute('aria-expanded',o);});
document.querySelectorAll('.mobile-link,.mobile-menu .btn').forEach(function(l){l.addEventListener('click',function(){mm.classList.remove('open');hb.classList.remove('open');hb.setAttribute('aria-expanded',false);});});
(function(){var b=document.getElementById('cookieBanner');if(!b)return;if(!localStorage.getItem('ctf_cookie'))setTimeout(function(){b.classList.add('visible');},1200);function d(){b.classList.remove('visible');localStorage.setItem('ctf_cookie','1');}document.getElementById('cookieAccept').onclick=d;document.getElementById('cookieDismiss').onclick=d;})();
</script>
<script src="https://www.socalreceptionist.com/widget.js" data-name="CTF Designs" data-about="CTF Designs is a web design agency building fast, modern websites for small businesses. Pricing: Landing Page $299, Scrolling Single Page $499, Custom $1,499, eCommerce custom. Founder: Roman. Contact: roman@ctfdesigns.com." data-accent="#7b2fbe"></script>
<script defer src="/newsletter-popup.js"></script>"""

def shell(title, desc, body, canonical, og_img=None):
    og = og_img or f"{SITE}/images/logo.png"
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article"><meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}"><meta property="og:image" content="{og}">
<meta property="og:url" content="{canonical}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/images/logo.png">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&family=Inter:wght@300;400;500;700&display=swap" rel="stylesheet">
{GA}
<style>{CSS}</style></head><body>
{NAV}
{body}
{FOOTER}
{A11Y}
{SCRIPTS}
</body></html>"""

# ---------------- build ----------------
def load_posts():
    posts = []
    for path in glob.glob(os.path.join(POSTS, "*.md")):
        meta, body = parse(open(path, encoding="utf-8").read())
        slug = meta.get("slug") or os.path.splitext(os.path.basename(path))[0]
        if str(meta.get("draft", "")).lower() == "true":
            continue
        posts.append({
            "slug": slug, "title": meta.get("title", slug), "date": meta.get("date", ""),
            "excerpt": meta.get("excerpt", ""), "cover": meta.get("cover", ""),
            "author": meta.get("author", "Roman"), "read": meta.get("read", ""),
            "kicker": meta.get("kicker", "The Floof Factor"), "body_md": body,
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts

def fmt_date(d):
    import datetime
    try:
        return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")
    except Exception:
        return d

def build():
    os.makedirs(POSTS, exist_ok=True)
    posts = load_posts()

    # index
    cards = []
    for p in posts:
        thumb = f'<img src="{p["cover"]}" alt="{html.escape(p["title"])}">' if p["cover"] else html.escape(p["kicker"])
        meta = " · ".join(x for x in [fmt_date(p["date"]), p["read"]] if x)
        cards.append(f"""<a class="post-card" href="/blog/{p['slug']}.html">
  <div class="thumb">{thumb}</div>
  <div class="pc-body"><div class="meta">{meta}</div><h3>{html.escape(p['title'])}</h3>
  <p>{html.escape(p['excerpt'])}</p><div class="more">Read more →</div></div></a>""")
    grid = "\n".join(cards) if cards else '<p style="color:var(--muted);text-align:center;padding:2rem">First issue dropping soon. 🐾</p>'
    index_body = f"""<header class="blog-hero"><div class="container">
  <div class="kicker">The Floof Factor</div>
  <h1 class="grad-text">Small-business web &amp; brand, unleashed.</h1>
  <p>Practical tips on websites, branding, and getting found online. From CTF Designs. Named after Cheddar the Floof. 🐾</p>
</div></header>
<div class="container"><div class="post-grid">{grid}</div></div>"""
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        shell("The Floof Factor | CTF Designs Blog",
              "Practical web design, branding, and small-business growth tips from CTF Designs.",
              index_body, f"{SITE}/blog/"))

    # posts
    for p in posts:
        meta = " · ".join(x for x in [p["author"], fmt_date(p["date"]), p["read"]] if x)
        article = f"""<article class="article">
  <a class="back" href="/blog/">← The Floof Factor</a>
  <div class="kicker">{html.escape(p['kicker'])}</div>
  <h1>{html.escape(p['title'])}</h1>
  <div class="byline">{meta}</div>
  {f'<img src="{p["cover"]}" alt="{html.escape(p["title"])}" style="width:100%;border-radius:14px;margin-bottom:1.6rem">' if p['cover'] else ''}
  <div class="post-body">{render_md(p['body_md'])}</div>
</article>
<div class="cta-card"><h3>Want a site that actually works this hard?</h3>
  <p>CTF Designs builds fast, modern websites for small businesses, from $299.</p>
  <a class="btn btn-grad" href="/contact.html">Start a project →</a></div>
<div style="height:3rem"></div>"""
        open(os.path.join(OUT, f"{p['slug']}.html"), "w", encoding="utf-8").write(
            shell(f"{p['title']} | The Floof Factor",
                  p["excerpt"] or p["title"], article, f"{SITE}/blog/{p['slug']}.html",
                  og_img=(p['cover'] if p['cover'].startswith('http') else None)))
    print(f"built {len(posts)} post(s) + index → {OUT}")

if __name__ == "__main__":
    build()
