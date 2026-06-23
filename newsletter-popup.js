/* CTF Designs — newsletter signup popup. Routes subscribers into CTF Engine.
   Drop <script defer src="/newsletter-popup.js"></script> before </body>.
   ADA-friendly modal: role=dialog, ESC to close, focus management, honeypot. */
(function () {
  var CFG = {
    endpoint: 'https://app.ctfdesigns.com/v1/newsletter/subscribe',
    clientId: '8dbc9e10-114f-41b1-bedf-9af6403f105a', // CTF Designs (engine)
    source: 'ctf-popup',
    accent: '#7b2fbe',
    title: 'Get the good stuff',
    sub: 'Web design tips, launch checklists, and the occasional deal. No spam, unsubscribe anytime.',
    button: 'Subscribe',
    delayMs: 18000
  };
  var KEY = 'nl_popup_' + CFG.source;
  try { if (localStorage.getItem(KEY)) return; } catch (e) {}
  if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) return;

  var shown = false, lastFocus = null;

  var css = ''
  + '.nlp-ov{position:fixed;inset:0;z-index:2147483640;background:rgba(8,8,14,.62);backdrop-filter:blur(3px);'
  + 'display:flex;align-items:center;justify-content:center;padding:18px;opacity:0;transition:opacity .2s}'
  + '.nlp-ov.on{opacity:1}'
  + '.nlp-card{position:relative;width:100%;max-width:420px;background:#15131c;color:#f3f0f8;border:1px solid #2c2738;'
  + 'border-radius:18px;box-shadow:0 30px 80px rgba(0,0,0,.6);padding:26px 24px 22px;'
  + "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;transform:translateY(10px);transition:transform .2s}"
  + '.nlp-ov.on .nlp-card{transform:none}'
  + '.nlp-x{position:absolute;top:12px;right:14px;background:none;border:0;color:#9a93ab;font-size:22px;line-height:1;'
  + 'cursor:pointer;padding:4px 8px;border-radius:8px}.nlp-x:hover{color:#fff;background:#241f30}'
  + '.nlp-card h3{margin:2px 0 6px;font-size:1.32rem;font-weight:800}'
  + '.nlp-card p{margin:0 0 16px;font-size:.93rem;line-height:1.45;color:#b8b1c7}'
  + '.nlp-card label{display:block;font-size:.78rem;color:#9a93ab;margin:0 0 5px}'
  + '.nlp-card input[type=email]{width:100%;background:#0f0d15;border:1px solid #332c42;border-radius:10px;'
  + 'color:#f3f0f8;padding:12px 13px;font-size:1rem;margin-bottom:12px}'
  + '.nlp-card input[type=email]:focus{outline:2px solid ' + CFG.accent + ';border-color:' + CFG.accent + '}'
  + '.nlp-btn{width:100%;background:' + CFG.accent + ';color:#fff;border:0;border-radius:10px;padding:13px;'
  + 'font-size:1rem;font-weight:700;cursor:pointer;transition:filter .12s}.nlp-btn:hover{filter:brightness(1.08)}'
  + '.nlp-btn:disabled{opacity:.6;cursor:default}'
  + '.nlp-fine{margin:11px 0 0;font-size:.72rem;color:#7d7690;text-align:center}'
  + '.nlp-msg{margin:10px 0 0;font-size:.88rem;text-align:center}'
  + '.nlp-hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}';

  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }

  function close(ov) {
    ov.classList.remove('on');
    setTimeout(function () { if (ov.parentNode) ov.parentNode.removeChild(ov); }, 220);
    document.removeEventListener('keydown', ov._esc);
    if (lastFocus && lastFocus.focus) try { lastFocus.focus(); } catch (e) {}
  }
  function seen() { try { localStorage.setItem(KEY, Date.now()); } catch (e) {} }

  function build() {
    if (shown) return; shown = true; seen(); // show once regardless of outcome
    lastFocus = document.activeElement;
    var style = el('style'); style.textContent = css; document.head.appendChild(style);

    var ov = el('div', { 'class': 'nlp-ov', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'nlp-t' });
    var card = el('div', { 'class': 'nlp-card' });
    var x = el('button', { 'class': 'nlp-x', 'aria-label': 'Close' }, '&times;');
    var h = el('h3', { id: 'nlp-t' }, CFG.title);
    var p = el('p', null, CFG.sub);
    var form = el('form');
    var lbl = el('label', { 'for': 'nlp-email' }, 'Email address');
    var inp = el('input', { type: 'email', id: 'nlp-email', name: 'email', required: 'required', placeholder: 'you@email.com', autocomplete: 'email' });
    var hp = el('input', { type: 'text', 'class': 'nlp-hp', tabindex: '-1', autocomplete: 'off', 'aria-hidden': 'true', name: 'company' });
    var btn = el('button', { 'class': 'nlp-btn', type: 'submit' }, CFG.button);
    var fine = el('p', { 'class': 'nlp-fine' }, 'We respect your inbox. Unsubscribe anytime.');
    var msg = el('p', { 'class': 'nlp-msg', role: 'status', 'aria-live': 'polite' });

    form.appendChild(lbl); form.appendChild(inp); form.appendChild(hp); form.appendChild(btn);
    card.appendChild(x); card.appendChild(h); card.appendChild(p); card.appendChild(form);
    card.appendChild(fine); card.appendChild(msg);
    ov.appendChild(card); document.body.appendChild(ov);
    requestAnimationFrame(function () { ov.classList.add('on'); });
    setTimeout(function () { try { inp.focus(); } catch (e) {} }, 60);

    ov._esc = function (e) { if (e.key === 'Escape') close(ov); };
    document.addEventListener('keydown', ov._esc);
    x.onclick = function () { close(ov); };
    ov.addEventListener('click', function (e) { if (e.target === ov) close(ov); });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (hp.value) { close(ov); return; } // bot
      var email = (inp.value || '').trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { msg.style.color = '#ff6b6b'; msg.textContent = 'Please enter a valid email.'; return; }
      btn.disabled = true; btn.textContent = 'Subscribing…'; msg.textContent = '';
      fetch(CFG.endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: CFG.clientId, email: email, source: CFG.source })
      }).then(function (r) {
        if (!r.ok) throw new Error('bad');
        msg.style.color = '#54d6a0'; msg.textContent = "You're in. Thanks for subscribing!";
        form.style.display = 'none'; fine.style.display = 'none';
        setTimeout(function () { close(ov); }, 1900);
      }).catch(function () {
        btn.disabled = false; btn.textContent = CFG.button;
        msg.style.color = '#ff6b6b'; msg.textContent = 'Something went wrong. Please try again.';
      });
    });
  }

  // triggers: timed OR exit-intent, whichever first
  var t = setTimeout(build, CFG.delayMs);
  function exit(e) { if (e.clientY <= 0) { clearTimeout(t); document.removeEventListener('mouseout', exit); build(); } }
  document.addEventListener('mouseout', exit);
})();
