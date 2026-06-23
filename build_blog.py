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
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-0X9Q4PV3XT');</script>"""

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#070711;--grad:linear-gradient(135deg,#7C3AED,#EC4899,#F97316);--accent:#3B82F6;--text:#f8fafc;--muted:#94a3b8;--card:#0d0d1a;--card-border:rgba(255,255,255,.08);--radius:12px}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;line-height:1.7;overflow-x:hidden}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif;line-height:1.25}
a{color:inherit}
.container{max-width:1180px;margin:0 auto;padding:0 5%}
.grad-text{background:var(--grad);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
/* nav */
#navbar{position:fixed;top:0;left:0;right:0;z-index:1000;display:flex;align-items:center;justify-content:space-between;padding:.4rem 5%;background:rgba(7,7,17,.7);backdrop-filter:blur(20px);border-bottom:1px solid transparent;transition:border-color .3s,background .3s}
#navbar.scrolled{border-bottom-color:var(--card-border);background:rgba(7,7,17,.92)}
.nav-logo img{height:64px;width:auto;border-radius:50%}
.nav-links{display:flex;gap:1.6rem;list-style:none}
.nav-links a{color:var(--muted);text-decoration:none;font-weight:500;font-size:.95rem;transition:color .2s}
.nav-links a:hover,.nav-links a.active{color:var(--text)}
.btn{display:inline-flex;align-items:center;padding:.65rem 1.5rem;border-radius:var(--radius);font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:.9rem;text-decoration:none;cursor:pointer;border:none;transition:transform .2s,box-shadow .2s}
.btn-grad{background:var(--grad);color:#fff}
.btn-grad:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(124,58,237,.4)}
.hamburger{display:none;flex-direction:column;gap:5px;background:none;border:none;cursor:pointer;padding:4px}
.hamburger span{display:block;width:24px;height:2px;background:var(--text);border-radius:2px;transition:all .3s}
.hamburger.open span:nth-child(1){transform:translateY(7px) rotate(45deg)}
.hamburger.open span:nth-child(2){opacity:0}
.hamburger.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
.mobile-menu{display:none;position:fixed;top:72px;left:0;right:0;background:rgba(7,7,17,.97);backdrop-filter:blur(20px);border-bottom:1px solid var(--card-border);padding:1.5rem 5%;z-index:999;flex-direction:column;gap:1.25rem}
.mobile-menu.open{display:flex}
.mobile-menu a{color:var(--muted);text-decoration:none;font-size:1.1rem;font-weight:500}
/* blog */
.blog-hero{padding:9rem 0 2.5rem;text-align:center}
.blog-hero .kicker{font-family:'Space Grotesk',sans-serif;font-weight:700;letter-spacing:.18em;text-transform:uppercase;font-size:.8rem;color:#EC4899;margin-bottom:1rem}
.blog-hero h1{font-size:clamp(2.4rem,6vw,3.6rem)}
.blog-hero p{color:var(--muted);max-width:620px;margin:1rem auto 0;font-size:1.08rem}
.post-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:1.6rem;padding:2rem 0 5rem}
.post-card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--card-border);border-radius:16px;overflow:hidden;text-decoration:none;color:inherit;transition:transform .2s,border-color .2s}
.post-card:hover{transform:translateY(-4px);border-color:rgba(236,72,153,.45)}
.post-card .thumb{aspect-ratio:16/9;background:var(--grad);display:flex;align-items:center;justify-content:center;font-family:'Space Grotesk',sans-serif;font-weight:700;color:#fff;font-size:1.1rem;padding:1rem;text-align:center}
.post-card .thumb img{width:100%;height:100%;object-fit:cover}
.post-card .pc-body{padding:1.3rem 1.4rem 1.5rem}
.post-card .meta{font-size:.78rem;color:var(--muted);margin-bottom:.5rem}
.post-card h3{font-size:1.22rem;margin-bottom:.5rem}
.post-card p{color:var(--muted);font-size:.93rem}
.post-card .more{margin-top:1rem;color:#EC4899;font-weight:600;font-size:.9rem}
/* article */
.article{max-width:760px;margin:0 auto;padding:8.5rem 5% 4rem}
.article .back{color:var(--muted);text-decoration:none;font-size:.9rem}
.article .kicker{font-family:'Space Grotesk',sans-serif;font-weight:700;letter-spacing:.16em;text-transform:uppercase;font-size:.78rem;color:#EC4899;margin:1.4rem 0 .6rem}
.article h1{font-size:clamp(2rem,5vw,2.9rem);margin-bottom:.8rem}
.article .byline{color:var(--muted);font-size:.9rem;margin-bottom:2rem}
.post-body{font-size:1.07rem}
.post-body h2{font-size:1.6rem;margin:2.2rem 0 .8rem}
.post-body h3{font-size:1.28rem;margin:1.8rem 0 .6rem}
.post-body p{margin:0 0 1.1rem;color:#e2e8f0}
.post-body ul,.post-body ol{margin:0 0 1.2rem 1.3rem;color:#e2e8f0}
.post-body li{margin-bottom:.5rem}
.post-body a{color:#EC4899}
.post-body blockquote{border-left:3px solid #7C3AED;padding:.4rem 0 .4rem 1.2rem;margin:1.4rem 0;color:var(--muted);font-style:italic}
.post-body img{max-width:100%;border-radius:12px;margin:1.4rem 0}
.post-body code{background:#16162a;padding:.15em .45em;border-radius:6px;font-size:.92em}
.post-body hr{border:none;border-top:1px solid var(--card-border);margin:2rem 0}
.cta-card{margin:3rem auto 0;max-width:760px;background:var(--card);border:1px solid var(--card-border);border-radius:16px;padding:2rem;text-align:center}
.cta-card h3{font-size:1.5rem;margin-bottom:.6rem}
.cta-card p{color:var(--muted);margin-bottom:1.3rem}
/* footer */
footer{border-top:1px solid var(--card-border);padding:3rem 0 2rem;background:#05050c}
.footer-inner{max-width:1180px;margin:0 auto;padding:0 5%}
.footer-top{display:flex;justify-content:space-between;gap:2rem;flex-wrap:wrap;margin-bottom:2rem}
.footer-brand img{height:64px;border-radius:50%}
.footer-brand p{color:var(--muted);font-size:.9rem;margin-top:.8rem;max-width:280px}
.footer-links{display:flex;gap:3rem;flex-wrap:wrap}
.footer-col h4{font-size:.95rem;margin-bottom:.8rem}
.footer-col ul{list-style:none}
.footer-col li{margin-bottom:.5rem}
.footer-col a{color:var(--muted);text-decoration:none;font-size:.9rem}
.footer-col a:hover{color:var(--text)}
.footer-bottom{border-top:1px solid var(--card-border);padding-top:1.5rem;display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem}
.footer-bottom p{color:var(--muted);font-size:.82rem}
.easter-egg{opacity:.8}
/* a11y widget */
#a11y-btn{position:fixed;bottom:24px;left:24px;z-index:9999;width:48px;height:48px;border-radius:50%;background:#7C3AED;color:#fff;border:none;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,.3);font-size:22px;display:flex;align-items:center;justify-content:center}
#a11y-btn:hover{background:#EC4899}
#a11y-panel{position:fixed;bottom:82px;left:24px;z-index:9999;background:#0d0d1a;border:1px solid rgba(255,255,255,.15);border-radius:12px;padding:16px;width:230px;box-shadow:0 8px 24px rgba(0,0,0,.4);display:none;flex-direction:column;gap:10px}
#a11y-panel.open{display:flex}
#a11y-panel h3{font-size:1rem;margin-bottom:.2rem}
.a11y-row{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:.88rem}
.a11y-controls button,#a11y-reset{background:#1b1b2e;border:1px solid rgba(255,255,255,.15);color:#fff;border-radius:8px;padding:5px 10px;cursor:pointer}
#a11y-reset{width:100%;margin-top:4px}
.a11y-toggle{position:relative;display:inline-block;width:40px;height:22px}
.a11y-toggle input{opacity:0;width:0;height:0}
.a11y-toggle .slider{position:absolute;inset:0;background:#374151;border-radius:22px;cursor:pointer;transition:background .2s}
.a11y-toggle .slider:before{content:"";position:absolute;width:16px;height:16px;left:3px;bottom:3px;background:#fff;border-radius:50%;transition:transform .2s}
.a11y-toggle input:checked + .slider{background:#7C3AED}
.a11y-toggle input:checked + .slider:before{transform:translateX(18px)}
body.a11y-high-contrast{filter:contrast(1.25)}
body.a11y-reduce-motion *{animation:none!important;transition:none!important;scroll-behavior:auto!important}
body.a11y-dyslexia{font-family:Arial,Helvetica,sans-serif!important;letter-spacing:.05em;word-spacing:.1em;line-height:1.9!important}
/* cookie */
.cookie-banner{position:fixed;bottom:0;left:0;right:0;z-index:9998;background:rgba(7,7,17,.95);backdrop-filter:blur(20px);border-top:1px solid var(--card-border);padding:1.25rem 5%;display:flex;align-items:center;justify-content:space-between;gap:1.5rem;flex-wrap:wrap;transform:translateY(100%);transition:transform .4s}
.cookie-banner.visible{transform:translateY(0)}
.cookie-banner p{font-size:.9rem;color:var(--muted);flex:1;min-width:200px}
.cookie-banner a{color:var(--accent);text-decoration:none}
.cookie-actions{display:flex;align-items:center;gap:1rem}
.cookie-dismiss{background:none;border:none;color:var(--muted);font-size:1.3rem;cursor:pointer}
@media(max-width:820px){.nav-links{display:none}.hamburger{display:flex}.footer-top{flex-direction:column}}
"""

NAV = """<nav id="navbar">
  <a href="/index.html" class="nav-logo" aria-label="CTF Designs home"><img src="/images/logo.png" alt="CTF Designs"></a>
  <ul class="nav-links">
    <li><a href="/index.html#services">Services</a></li>
    <li><a href="/index.html#portfolio">Portfolio</a></li>
    <li><a href="/about.html">About</a></li>
    <li><a href="/blog/" class="active">Blog</a></li>
    <li><a href="/pricing.html">Pricing</a></li>
    <li><a href="/contact.html">Contact</a></li>
  </ul>
  <a href="/contact.html" class="btn btn-grad" style="font-size:.85rem;padding:.6rem 1.25rem;">Start a Project</a>
  <button class="hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
</nav>
<div class="mobile-menu" id="mobile-menu">
  <a href="/index.html#services" class="mobile-link">Services</a>
  <a href="/index.html#portfolio" class="mobile-link">Portfolio</a>
  <a href="/about.html" class="mobile-link">About</a>
  <a href="/blog/" class="mobile-link">Blog</a>
  <a href="/pricing.html" class="mobile-link">Pricing</a>
  <a href="/contact.html" class="mobile-link">Contact</a>
  <a href="/contact.html" class="btn btn-grad" style="width:fit-content;margin-top:.5rem;">Start a Project</a>
</div>"""

FOOTER = """<footer>
  <div class="footer-inner">
    <div class="footer-top">
      <div class="footer-brand">
        <a href="/index.html" class="nav-logo"><img src="/images/logo.png" alt="CTF Designs"></a>
        <p>Built by humans. Powered by results.<br>Web design &amp; development for businesses ready to grow.</p>
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

A11Y = """<button id="a11y-btn" aria-label="Accessibility options" aria-expanded="false" aria-controls="a11y-panel">&#9855;</button>
<div id="a11y-panel" role="dialog" aria-label="Accessibility options" aria-modal="false">
  <h3>Accessibility</h3>
  <div class="a11y-row"><span class="a11y-label">Text size</span><div class="a11y-controls"><button id="a11y-dec">A&#8722;</button><button id="a11y-inc">A+</button></div></div>
  <div class="a11y-row"><label class="a11y-label" for="a11y-contrast">High contrast</label><label class="a11y-toggle"><input type="checkbox" id="a11y-contrast"/><span class="slider"></span></label></div>
  <div class="a11y-row"><label class="a11y-label" for="a11y-motion">Reduce motion</label><label class="a11y-toggle"><input type="checkbox" id="a11y-motion"/><span class="slider"></span></label></div>
  <div class="a11y-row"><label class="a11y-label" for="a11y-dyslexia">Dyslexia-friendly</label><label class="a11y-toggle"><input type="checkbox" id="a11y-dyslexia"/><span class="slider"></span></label></div>
  <button id="a11y-reset">Reset all</button>
</div>
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
(function(){var btn=document.getElementById("a11y-btn"),panel=document.getElementById("a11y-panel"),body=document.body,KEY="a11y_prefs",fs=100;function save(){localStorage.setItem(KEY,JSON.stringify({fontSize:fs,contrast:document.getElementById("a11y-contrast").checked,motion:document.getElementById("a11y-motion").checked,dyslexia:document.getElementById("a11y-dyslexia").checked}));}function applyFs(){document.documentElement.style.fontSize=fs===100?"":fs+"%";}function load(){try{var p=JSON.parse(localStorage.getItem(KEY)||"{}");if(p.fontSize){fs=p.fontSize;applyFs();}if(p.contrast){document.getElementById("a11y-contrast").checked=true;body.classList.add("a11y-high-contrast");}if(p.motion){document.getElementById("a11y-motion").checked=true;body.classList.add("a11y-reduce-motion");}if(p.dyslexia){document.getElementById("a11y-dyslexia").checked=true;body.classList.add("a11y-dyslexia");}}catch(e){}}btn.addEventListener("click",function(e){e.stopPropagation();var o=panel.classList.toggle("open");btn.setAttribute("aria-expanded",o);});document.addEventListener("click",function(e){if(!panel.contains(e.target)&&e.target!==btn){panel.classList.remove("open");btn.setAttribute("aria-expanded","false");}});document.addEventListener("keydown",function(e){if(e.key==="Escape"){panel.classList.remove("open");btn.focus();}});document.getElementById("a11y-inc").addEventListener("click",function(){fs=Math.min(fs+10,150);applyFs();save();});document.getElementById("a11y-dec").addEventListener("click",function(){fs=Math.max(fs-10,80);applyFs();save();});["contrast","motion","dyslexia"].forEach(function(id){document.getElementById("a11y-"+id).addEventListener("change",function(){body.classList.toggle("a11y-"+(id==="contrast"?"high-contrast":id==="motion"?"reduce-motion":"dyslexia"),this.checked);save();});});document.getElementById("a11y-reset").addEventListener("click",function(){fs=100;applyFs();["contrast","motion","dyslexia"].forEach(function(id){document.getElementById("a11y-"+id).checked=false;});body.classList.remove("a11y-high-contrast","a11y-reduce-motion","a11y-dyslexia");localStorage.removeItem(KEY);});load();})();
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
  <p>Practical tips on websites, branding, and getting found online — from CTF Designs. Named after Cheddar the Floof. 🐾</p>
</div></header>
<div class="container"><div class="post-grid">{grid}</div></div>"""
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        shell("The Floof Factor — CTF Designs Blog",
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
  <p>CTF Designs builds fast, modern websites for small businesses — from $299.</p>
  <a class="btn btn-grad" href="/contact.html">Start a project →</a></div>
<div style="height:3rem"></div>"""
        open(os.path.join(OUT, f"{p['slug']}.html"), "w", encoding="utf-8").write(
            shell(f"{p['title']} — The Floof Factor",
                  p["excerpt"] or p["title"], article, f"{SITE}/blog/{p['slug']}.html",
                  og_img=(p['cover'] if p['cover'].startswith('http') else None)))
    print(f"built {len(posts)} post(s) + index → {OUT}")

if __name__ == "__main__":
    build()
