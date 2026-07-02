// Auto-fires on every Netlify form submission. For the "audit" form, it runs a
// PageSpeed scan on the submitted URL and emails Roman a head-start report so he
// can add his human design/conversion review and send it fast. Fails safe: if
// the scan is slow or errors, the lead + a 1-click PageSpeed link still email.
const RESEND_KEY = process.env.RESEND_API_KEY;
const PSI_KEY = process.env.PAGESPEED_API_KEY || '';
const TO = 'roman@ctfdesigns.com';
const FROM = 'CTF Audit Bot <audit@ctfdesigns.com>';

exports.handler = async (event) => {
  try {
    const body = JSON.parse(event.body || '{}');
    const payload = body.payload || {};
    const form = payload.form_name || (payload.data && payload.data['form-name']) || '';

    // Instant-scan lead: the visitor ran the /scan tool and entered their email
    // to unlock the full report. The scan already ran client-side, so just email
    // Roman the lead fast (speed-to-lead).
    if (form === 'scan-lead') {
      const d = payload.data || {};
      const site = String(d.website || '').trim();
      const html = `
        <h2 style="font-family:sans-serif">New instant-scan lead</h2>
        <p style="font-family:sans-serif">
          <b>Email:</b> ${esc(d.email || '')}<br>
          <b>Scanned site:</b> <a href="${esc(site)}">${esc(site)}</a>
        </p>
        <p style="font-family:sans-serif;color:#888;font-size:12px">They used the free /scan tool and unlocked the full report. Warm lead — follow up with a personal audit offer.</p>`;
      await sendEmail(`⚡ Instant-scan lead: ${site || d.email || 'new lead'}`, html);
      return { statusCode: 200, body: 'ok (scan-lead)' };
    }

    if (form !== 'audit') return { statusCode: 200, body: 'ignored (not audit form)' };

    const d = payload.data || {};
    const site = String(d.website || '').trim();
    const scanHtml = site ? await scan(site) : '<p>(No website URL submitted.)</p>';

    const html = `
      <h2 style="font-family:sans-serif">New free-audit request</h2>
      <p style="font-family:sans-serif">
        <b>Name:</b> ${esc(d.name || '(none)')}<br>
        <b>Business:</b> ${esc(d.business || '(none)')}<br>
        <b>Email:</b> ${esc(d.email || '')}<br>
        <b>Phone:</b> ${esc(d.phone || '')}<br>
        <b>Website:</b> <a href="${esc(site)}">${esc(site)}</a>
      </p>
      <hr>
      <h3 style="font-family:sans-serif">Head-start scan</h3>
      <div style="font-family:sans-serif">${scanHtml}</div>
      <p style="font-family:sans-serif;color:#888;font-size:12px">Auto-scan (PageSpeed). Add your human design + conversion review, then send the report. Reply fast — speed-to-lead wins these.</p>`;

    await sendEmail(`🔎 Free audit request: ${site || d.name || 'new lead'}`, html);
    return { statusCode: 200, body: 'ok' };
  } catch (e) {
    try { await sendEmail('⚠️ Audit function error', `<pre>${esc(String(e && e.stack || e))}</pre>`); } catch (_) {}
    return { statusCode: 200, body: 'error-handled' };
  }
};

async function scan(url) {
  const psi = `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(url)}` +
    `&strategy=mobile&category=performance&category=seo&category=accessibility&category=best-practices` +
    (PSI_KEY ? `&key=${PSI_KEY}` : '');
  const full = `https://pagespeed.web.dev/report?url=${encodeURIComponent(url)}`;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 8000);
  try {
    const r = await fetch(psi, { signal: ctrl.signal });
    clearTimeout(timer);
    if (!r.ok) throw new Error('PageSpeed ' + r.status);
    const j = await r.json();
    const cats = (j.lighthouseResult && j.lighthouseResult.categories) || {};
    const row = (k, label) => {
      const s = cats[k] && cats[k].score;
      return `<tr><td style="padding:4px 12px 4px 0">${label}</td><td><b>${s == null ? '—' : Math.round(s * 100)}</b>/100</td></tr>`;
    };
    const audits = (j.lighthouseResult && j.lighthouseResult.audits) || {};
    const opps = Object.values(audits)
      .filter(a => a && a.details && a.details.type === 'opportunity' && a.score != null && a.score < 0.9)
      .slice(0, 5).map(a => `<li>${esc(a.title)}</li>`).join('') || '<li>No major performance opportunities flagged.</li>';
    return `<table style="border-collapse:collapse">${row('performance', 'Performance')}${row('seo', 'SEO')}${row('accessibility', 'Accessibility')}${row('best-practices', 'Best Practices')}</table>` +
      `<p><b>Top opportunities:</b></p><ul>${opps}</ul>` +
      `<p><a href="${full}">Open full PageSpeed report →</a></p>`;
  } catch (e) {
    clearTimeout(timer);
    return `<p>Auto-scan didn't finish (${esc(String((e && e.message) || e))}). Run it in one click: <a href="${full}">PageSpeed report →</a></p>`;
  }
}

async function sendEmail(subject, html) {
  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${RESEND_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: FROM, to: [TO], subject, html }),
  });
}

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
