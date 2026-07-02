// CTF light website scanner. Fetches a page server-side and runs fast,
// dependency-free checks (NO Lighthouse / PageSpeed). Returns a 0-100 health
// score plus per-check results. Free findings are marked public; the rest are
// gated behind an email capture on the front end.
const UA = 'Mozilla/5.0 (compatible; CTFDesignsScanner/1.0; +https://ctfdesigns.com/scan)';

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') return resp(200, {});
  if (event.httpMethod !== 'POST') return resp(405, { error: 'POST only' });

  let url;
  try { url = String(JSON.parse(event.body || '{}').url || '').trim(); }
  catch { return resp(400, { error: 'bad request' }); }
  if (!url) return resp(400, { error: 'Enter your website address.' });
  if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
  let base;
  try { base = new URL(url); } catch { return resp(400, { error: 'That does not look like a valid website address.' }); }

  const checks = [];
  const add = (id, label, status, detail, weight, pub) =>
    checks.push({ id, label, status, detail, weight, public: !!pub });

  // ---- fetch the page (time it) ----
  let html = '', headers = {}, status = 0, ms = 0, ok = false, finalUrl = url;
  try {
    const t0 = Date.now();
    const ctrl = new AbortController();
    const to = setTimeout(() => ctrl.abort(), 15000);
    const r = await fetch(url, { headers: { 'User-Agent': UA }, redirect: 'follow', signal: ctrl.signal });
    clearTimeout(to);
    ms = Date.now() - t0;
    status = r.status; ok = r.ok; finalUrl = r.url || url;
    r.headers.forEach((v, k) => { headers[k.toLowerCase()] = v; });
    html = await r.text();
  } catch (e) {
    return resp(200, { error: 'We could not reach that site. Check the address and try again.', reachable: false });
  }
  if (!ok) add('reachable', 'Site loads without errors', 'fail', `Server returned HTTP ${status}.`, 3, true);
  else add('reachable', 'Site loads without errors', 'pass', `Responded HTTP ${status}.`, 3, true);

  const head = (html.match(/<head[\s\S]*?<\/head>/i) || [html])[0];
  const lower = html.toLowerCase();

  // ---- HTTPS ----
  const https = new URL(finalUrl).protocol === 'https:';
  add('https', 'Secure connection (HTTPS)', https ? 'pass' : 'fail',
    https ? 'Served over HTTPS with a valid certificate.' : 'Not served over HTTPS. Visitors see a "Not secure" warning and Google ranks you lower.',
    3, true);

  // ---- mobile viewport ----
  const viewport = /<meta[^>]+name=["']viewport["'][^>]*>/i.test(head);
  add('viewport', 'Mobile-friendly viewport', viewport ? 'pass' : 'fail',
    viewport ? 'A responsive viewport tag is set.' : 'No mobile viewport tag. The site likely looks broken on phones, where most local traffic is.',
    3, true);

  // ---- title ----
  const title = (head.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [,''])[1].trim();
  add('title', 'Page title for Google', title ? (title.length >= 15 && title.length <= 65 ? 'pass' : 'warn') : 'fail',
    title ? `Title is ${title.length} characters${title.length > 65 ? ' (a bit long, Google may cut it off)' : title.length < 15 ? ' (very short)' : '.'}` : 'Missing a <title>. This is the blue link Google shows in search results.',
    2, false);

  // ---- meta description ----
  const desc = (head.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']*)["']/i) || [,''])[1].trim();
  add('description', 'Search description', desc ? (desc.length >= 70 && desc.length <= 165 ? 'pass' : 'warn') : 'fail',
    desc ? `Description is ${desc.length} characters.` : 'No meta description. Google writes its own (usually worse) snippet for you.',
    2, false);

  // ---- single H1 ----
  const h1s = (html.match(/<h1[\s>]/gi) || []).length;
  add('h1', 'Clear main heading', h1s === 1 ? 'pass' : h1s === 0 ? 'fail' : 'warn',
    h1s === 1 ? 'Exactly one H1 heading.' : h1s === 0 ? 'No H1 heading. Google and screen readers use it to understand the page.' : `${h1s} H1 headings — should usually be one.`,
    1, false);

  // ---- image alt coverage ----
  const imgs = html.match(/<img\b[^>]*>/gi) || [];
  const withAlt = imgs.filter(t => /\salt=["'][^"']*["']/i.test(t) && !/\salt=["']["']/i.test(t)).length;
  const altPct = imgs.length ? Math.round((withAlt / imgs.length) * 100) : 100;
  add('alt', 'Image accessibility (alt text)', imgs.length === 0 ? 'pass' : altPct >= 80 ? 'pass' : altPct >= 40 ? 'warn' : 'fail',
    imgs.length === 0 ? 'No images to check.' : `${withAlt} of ${imgs.length} images (${altPct}%) have alt text. Missing alt text hurts accessibility and image SEO.`,
    2, false);

  // ---- Open Graph (social sharing preview) ----
  const ogTitle = /<meta[^>]+property=["']og:title["']/i.test(head);
  const ogImage = /<meta[^>]+property=["']og:image["']/i.test(head);
  add('og', 'Social share preview', ogTitle && ogImage ? 'pass' : (ogTitle || ogImage) ? 'warn' : 'fail',
    ogTitle && ogImage ? 'Open Graph title and image are set.' : 'Missing Open Graph tags. Links to your site share as a bare URL with no image on Facebook, iMessage, etc.',
    1, false);

  // ---- favicon ----
  const favicon = /<link[^>]+rel=["'][^"']*icon[^"']*["']/i.test(head);
  add('favicon', 'Browser tab icon (favicon)', favicon ? 'pass' : 'warn',
    favicon ? 'A favicon is set.' : 'No favicon. Your tab shows a blank/default icon, which reads as unfinished.',
    1, false);

  // ---- security headers ----
  const hsts = 'strict-transport-security' in headers;
  add('hsts', 'Security headers', hsts ? 'pass' : 'warn',
    hsts ? 'HSTS security header is present.' : 'No HSTS header. A basic hardening step most small-business sites miss.',
    1, false);

  // ---- analytics / tracking ----
  const hasGA = /gtag\(|googletagmanager|google-analytics|gtm\.js|fbq\(|clarity\.ms|plausible/i.test(html);
  add('analytics', 'Visitor tracking installed', hasGA ? 'pass' : 'warn',
    hasGA ? 'An analytics/tracking tag was detected.' : 'No analytics detected. You cannot see how many people visit or where they drop off.',
    1, false);

  // ---- contact / phone present ----
  const hasTel = /href=["']tel:/i.test(html) || /\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/.test(html.replace(/<[^>]+>/g, ' '));
  add('contact', 'Easy to contact you', hasTel ? 'pass' : 'warn',
    hasTel ? 'A phone number or click-to-call link was found.' : 'No obvious phone number or click-to-call link. The #1 reason a local visitor leaves.',
    2, false);

  // ---- page weight ----
  const kb = Math.round(Buffer.byteLength(html) / 1024);
  add('weight', 'Page weight', kb <= 500 ? 'pass' : kb <= 1500 ? 'warn' : 'fail',
    `The HTML document is ${kb} KB${kb > 1500 ? ' — heavy. Page builders like Wix often bloat this, slowing phones on cellular.' : kb > 500 ? ' — a little heavy.' : '.'}`,
    1, false);

  // ---- response time (not a Lighthouse score, just TTFB-ish) ----
  add('speed', 'Server response time', ms <= 800 ? 'pass' : ms <= 2000 ? 'warn' : 'fail',
    `The page responded in ${ms} ms${ms > 2000 ? ' — slow. Every second of delay loses visitors.' : ms > 800 ? '.' : ' — snappy.'}`,
    2, true);

  // ---- score ----
  const val = { pass: 1, warn: 0.5, fail: 0 };
  const totW = checks.reduce((s, c) => s + c.weight, 0);
  const gotW = checks.reduce((s, c) => s + c.weight * val[c.status], 0);
  const score = Math.round((gotW / totW) * 100);
  const fails = checks.filter(c => c.status === 'fail').length;
  const warns = checks.filter(c => c.status === 'warn').length;

  return resp(200, {
    url: finalUrl,
    score,
    grade: score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 55 ? 'D' : 'F',
    summary: { pass: checks.filter(c => c.status === 'pass').length, warn: warns, fail: fails, total: checks.length },
    checks,
  });
};

function resp(code, obj) {
  return {
    statusCode: code,
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'POST, OPTIONS' },
    body: JSON.stringify(obj),
  };
}
