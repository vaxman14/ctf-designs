// CTF deep scanner (private /deep tool, Roman's pre-call prep). Adds the heavy
// data the public /scan deliberately omits: Google PageSpeed / Lighthouse scores
// for mobile AND desktop plus the top improvement opportunities. The /deep page
// combines this with the light-scan checks for a full picture.
const PSI_KEY = process.env.PAGESPEED_API_KEY || '';

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') return resp(200, {});
  if (event.httpMethod !== 'POST') return resp(405, { error: 'POST only' });
  let url;
  try { url = String(JSON.parse(event.body || '{}').url || '').trim(); }
  catch { return resp(400, { error: 'bad request' }); }
  if (!url) return resp(400, { error: 'Enter a URL.' });
  if (!/^https?:\/\//i.test(url)) url = 'https://' + url;

  try {
    const [mobile, desktop] = await Promise.all([psi(url, 'mobile'), psi(url, 'desktop')]);
    return resp(200, { url, mobile, desktop, report: `https://pagespeed.web.dev/report?url=${encodeURIComponent(url)}` });
  } catch (e) {
    return resp(200, { error: String((e && e.message) || e) });
  }
};

async function psi(url, strategy) {
  const api = `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(url)}` +
    `&strategy=${strategy}&category=performance&category=seo&category=accessibility&category=best-practices` +
    (PSI_KEY ? `&key=${PSI_KEY}` : '');
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 25000);
  try {
    const r = await fetch(api, { signal: ctrl.signal });
    clearTimeout(t);
    if (!r.ok) return { error: 'PageSpeed ' + r.status };
    const j = await r.json();
    const cats = (j.lighthouseResult && j.lighthouseResult.categories) || {};
    const sc = (k) => (cats[k] && cats[k].score != null ? Math.round(cats[k].score * 100) : null);
    const audits = (j.lighthouseResult && j.lighthouseResult.audits) || {};
    const opps = Object.values(audits)
      .filter(a => a && a.details && a.details.type === 'opportunity' && a.score != null && a.score < 0.9)
      .sort((a, b) => (b.details.overallSavingsMs || 0) - (a.details.overallSavingsMs || 0))
      .slice(0, 6)
      .map(a => ({ title: a.title, savings: a.details.overallSavingsMs ? Math.round(a.details.overallSavingsMs) + ' ms' : '' }));
    const lcp = audits['largest-contentful-paint'] && audits['largest-contentful-paint'].displayValue;
    const cls = audits['cumulative-layout-shift'] && audits['cumulative-layout-shift'].displayValue;
    const tbt = audits['total-blocking-time'] && audits['total-blocking-time'].displayValue;
    return {
      performance: sc('performance'), seo: sc('seo'), accessibility: sc('accessibility'), bestPractices: sc('best-practices'),
      lcp, cls, tbt, opportunities: opps,
    };
  } catch (e) {
    clearTimeout(t);
    return { error: String((e && e.message) || e) };
  }
}

function resp(code, obj) {
  return {
    statusCode: code,
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'POST, OPTIONS' },
    body: JSON.stringify(obj),
  };
}
