/* ==========================================================================
   ORF Bio — interactions (v10)
   No dependencies. Every module no-ops if its markup isn't on the page,
   so one file serves every template.
   ========================================================================== */
(function () {
  'use strict';

  var d = document, html = d.documentElement, body = d.body;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.min(b === undefined ? 1 : b, Math.max(a || 0, v)); };
  var hasIO = 'IntersectionObserver' in window;

  /* One rAF-throttled scroll/resize bus instead of many listeners */
  var scrollFns = [], resizeFns = [], ticking = false;
  function onScroll(fn) { scrollFns.push(fn); }
  function onResize(fn) { resizeFns.push(fn); }
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { scrollFns.forEach(function (f) { f(); }); ticking = false; });
  }, { passive: true });
  var rt;
  window.addEventListener('resize', function () {
    clearTimeout(rt);
    rt = setTimeout(function () { resizeFns.forEach(function (f) { f(); }); scrollFns.forEach(function (f) { f(); }); }, 120);
  });

  function once(el, fn, margin) {
    if (!hasIO) { fn(); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { fn(); io.disconnect(); } });
    }, { rootMargin: margin || '0px 0px -18% 0px' });
    io.observe(el);
  }

  /* ---- 1. Colour-field morph ------------------------------------------- */
  (function morph() {
    if (!hasIO || !html.classList.contains('morph')) return;
    var sections = $$('[data-theme]').filter(function (el) { return el !== body; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) body.setAttribute('data-theme', e.target.getAttribute('data-theme'));
      });
    }, { rootMargin: '-50% 0px -50% 0px' });
    sections.forEach(function (s) { io.observe(s); });
  })();

  /* ---- 2. Navigation ---------------------------------------------------- */
  (function nav() {
    var nav = $('.nav'); if (!nav) return;
    var burger = $('.nav__burger', nav), menu = $('#menu');
    var lastY = window.scrollY, open = false;

    onScroll(function () {
      var y = window.scrollY, dy = y - lastY;
      if (Math.abs(dy) < 6) return;
      if (!open && y > 180 && dy > 0) nav.classList.add('is-hidden');
      else nav.classList.remove('is-hidden');
      lastY = y;
    });
    nav.addEventListener('focusin', function () { nav.classList.remove('is-hidden'); });

    if (!burger || !menu) return;
    var outside = $$('main, footer, .skip');
    function toggle(state) {
      open = state;
      burger.setAttribute('aria-expanded', String(state));
      html.classList.toggle('menu-open', state);
      outside.forEach(function (el) { el.inert = state; });
      if (state) {
        menu.hidden = false;
        requestAnimationFrame(function () { requestAnimationFrame(function () { menu.classList.add('is-open'); }); });
        var first = $('a', menu); if (first) setTimeout(function () { first.focus(); }, 250);
      } else {
        menu.classList.remove('is-open');
        setTimeout(function () { if (!open) menu.hidden = true; }, reduce ? 0 : 700);
      }
    }
    burger.addEventListener('click', function () { toggle(!open); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && open) { toggle(false); burger.focus(); } });
    $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { toggle(false); }); });
    window.matchMedia('(min-width: 961px)').addEventListener('change', function (m) { if (m.matches && open) toggle(false); });
  })();

  /* ---- 3. Fit text to its container ------------------------------------ */
  var fitters = [];
  function fitAll() {
    fitters.forEach(function (f) {
      var box = f.box.clientWidth;
      if (!box) return;
      f.el.style.setProperty('--fit', '100px');
      var w = f.measure.getBoundingClientRect().width;
      if (!w) return;
      var size = Math.min(f.max, (100 * box * f.ratio) / w);
      f.el.style.setProperty('--fit', size.toFixed(2) + 'px');
    });
  }
  $$('[data-fit]').forEach(function (el) {
    var measure = $(el.getAttribute('data-fit-measure') || ':scope > span', el) || el;
    var box = el.getAttribute('data-fit-box') ? el.closest(el.getAttribute('data-fit-box')) : el;
    fitters.push({
      el: el, measure: measure, box: box,
      ratio: parseFloat(el.getAttribute('data-fit')) || 1,
      max: parseFloat(el.getAttribute('data-fit-max')) || Infinity
    });
  });
  if (fitters.length) {
    fitAll();
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(fitAll);
    onResize(fitAll);
  }

  /* ---- 3b. Page titles never overflow ------------------------------- */
  var titles = $$('.page-title');
  function fitTitles() {
    titles.forEach(function (h) {
      h.style.removeProperty('--fit-size');
      var line = $('.hero__line', h) || h, inner = $('.hero__line > span', h) || line;
      var size = parseFloat(getComputedStyle(h).fontSize), guard = 0;
      // an unbreakable word wider than the column shows up as inner overflow
      while (inner.scrollWidth > line.clientWidth + 1 && guard++ < 40) {
        size *= .95; h.style.setProperty('--fit-size', size.toFixed(1) + 'px');
      }
    });
  }
  if (titles.length) { fitTitles(); if (d.fonts && d.fonts.ready) d.fonts.ready.then(fitTitles); onResize(fitTitles); }

  /* ---- 4. Hero entrance -------------------------------------------------- */
  (function entrance() {
    var go = function () { html.classList.add('is-loaded'); };
    if (reduce) { go(); return; }
    var done = false, fire = function () { if (!done) { done = true; requestAnimationFrame(go); } };
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(fire);
    setTimeout(fire, 650);
  })();

  /* ---- 5. Culture: living cell field ----------------------------------- */
  $$('[data-culture]').forEach(function (root) {
    var canvas = $('canvas', root); if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var host = root.parentElement;
    var W = 0, H = 0, cells = [], raf = 0, visible = true;
    var pointer = { x: -9999, y: -9999 };
    var TAU = Math.PI * 2;
    var density = parseFloat(root.getAttribute('data-density')) || 1;

    function rand(a, b) { return a + Math.random() * (b - a); }

    function build() {
      var n = Math.min(120, Math.round((W * H) / 15500 * density));
      cells = [];
      for (var i = 0; i < n; i++) {
        var big = Math.random() < .1;
        var r = big ? rand(70, 150) : Math.pow(Math.random(), 1.7) * 44 + 5;
        cells.push({
          x: rand(-r, W + r), y: rand(-r, H + r), r: r,
          vx: rand(-.14, .14), vy: rand(-.1, .1), ox: 0, oy: 0,
          lw: big ? rand(2.5, 5) : rand(1.2, 3.2),
          a: big ? rand(.16, .3) : rand(.22, .55),
          warm: Math.random() < .55,
          nucleus: !big && r > 12 && Math.random() < .45,
          nr: rand(.22, .42), nx: rand(-.25, .25), ny: rand(-.25, .25),
          ph: rand(0, TAU), sp: rand(.4, 1.1)
        });
      }
    }

    function resize() {
      var rect = root.getBoundingClientRect();
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      W = rect.width; H = rect.height;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      build(); draw(0);
    }

    function draw(t) {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < cells.length; i++) {
        var c = cells[i];
        if (!reduce) {
          c.x += c.vx; c.y += c.vy;
          if (c.x < -c.r - 20) c.x = W + c.r; else if (c.x > W + c.r + 20) c.x = -c.r;
          if (c.y < -c.r - 20) c.y = H + c.r; else if (c.y > H + c.r + 20) c.y = -c.r;
          var dx = c.x - pointer.x, dy = c.y - pointer.y, dist = Math.sqrt(dx * dx + dy * dy) || 1;
          var reach = 170 + c.r, tx = 0, ty = 0;
          if (dist < reach) { var f = 1 - dist / reach; tx = dx / dist * f * 42; ty = dy / dist * f * 42; }
          c.ox += (tx - c.ox) * .07; c.oy += (ty - c.oy) * .07;
        }
        var x = c.x + c.ox, y = c.y + c.oy;
        var rr = c.r * (1 + Math.sin(t * .0006 * c.sp + c.ph) * .035);
        ctx.beginPath(); ctx.arc(x, y, rr, 0, TAU);
        ctx.lineWidth = c.lw;
        ctx.strokeStyle = c.warm ? 'rgba(242,101,34,' + c.a + ')' : 'rgba(255,240,140,' + (c.a + .15) + ')';
        ctx.stroke();
        if (c.nucleus) {
          ctx.beginPath(); ctx.arc(x + rr * c.nx, y + rr * c.ny, rr * c.nr, 0, TAU);
          ctx.fillStyle = c.warm ? 'rgba(242,101,34,' + (c.a * .45) + ')' : 'rgba(255,244,170,' + (c.a * .7) + ')';
          ctx.fill();
        }
      }
    }

    function loop(t) { draw(t); raf = requestAnimationFrame(loop); }
    function start() { if (!raf && visible && !reduce && !d.hidden) raf = requestAnimationFrame(loop); }
    function stop() { cancelAnimationFrame(raf); raf = 0; }

    resize();
    root.classList.add('is-ready');
    onResize(resize);

    if (!reduce) {
      host.addEventListener('pointermove', function (e) {
        var r = root.getBoundingClientRect(); pointer.x = e.clientX - r.left; pointer.y = e.clientY - r.top;
      });
      host.addEventListener('pointerleave', function () { pointer.x = pointer.y = -9999; });
      if (hasIO) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; visible ? start() : stop(); }).observe(root);
      d.addEventListener('visibilitychange', function () { d.hidden ? stop() : start(); });
      start();
    }
  });

  /* ---- 7. What sets us apart: sticky views -------------------------- */
  (function apart() {
    var root = $('[data-apart]'); if (!root) return;
    var views = $$('.view', root), steps = $$('.step', root), ticks = $$('.views__tick', root);
    var current = -1;
    function set(i) {
      if (i === current || i < 0) return;
      current = i;
      steps.forEach(function (s, j) { s.classList.toggle('is-active', j === i); });
      views.forEach(function (v, j) { v.classList.toggle('is-shown', j <= i); v.setAttribute('aria-hidden', String(j !== i)); });
      ticks.forEach(function (t, j) { t.classList.toggle('is-on', j <= i); });
    }
    set(0);
    if (!hasIO) { steps.forEach(function (s) { s.classList.add('is-active'); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) set(steps.indexOf(e.target)); });
    }, { rootMargin: '-45% 0px -55% 0px' });
    steps.forEach(function (s) { io.observe(s); });
  })();

  /* ---- 8. Word fill tied to scroll ------------------------------------- */
  (function fill() {
    var els = $$('[data-fill]'); if (!els.length) return;
    var sets = els.map(function (el) {
      var words = el.textContent.trim().split(/\s+/);
      el.setAttribute('aria-label', el.textContent.trim());
      el.textContent = '';
      var spans = words.map(function (w, i) {
        var s = d.createElement('span'); s.className = 'w'; s.textContent = w; s.setAttribute('aria-hidden', 'true');
        el.appendChild(s); if (i < words.length - 1) el.appendChild(d.createTextNode(' '));
        return s;
      });
      return { el: el, spans: spans };
    });
    if (reduce) return;
    function update() {
      var vh = window.innerHeight;
      sets.forEach(function (set) {
        var r = set.el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var p = clamp((vh * .86 - r.top) / (r.height + vh * .32));
        var n = set.spans.length;
        set.spans.forEach(function (s, i) {
          s.style.setProperty('--o', (.2 + .8 * clamp(p * (n + 3) - i)).toFixed(3));
        });
      });
    }
    onScroll(update); update();
  })();

  /* ---- 9. Therapeutic areas accordion --------------------------------- */
  (function areas() {
    var heads = $$('.area button.area__head'); if (!heads.length) return;
    function setOpen(area, state) {
      area.classList.toggle('is-open', state);
      $('button.area__head', area).setAttribute('aria-expanded', String(state));
    }
    heads.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var area = btn.closest('.area');
        setOpen(area, !area.classList.contains('is-open'));
      });
    });
    function fromHash() {
      var target = location.hash && d.getElementById(location.hash.slice(1));
      if (target && target.classList.contains('area') && $('button.area__head', target)) {
        setOpen(target, true);
        setTimeout(function () { target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); }, 80);
        return true;
      }
    }
    if (!fromHash() && heads[0]) setOpen(heads[0].closest('.area'), true);
    window.addEventListener('hashchange', fromHash);
  })();

  /* ---- 10. Segmented switches: tabs + filters ------------------------- */
  function placeThumb(sw) {
    var thumb = $('.switch__thumb', sw);
    var on = $('[aria-selected="true"], [aria-pressed="true"]', sw);
    if (!thumb || !on) return;
    thumb.style.setProperty('--w', on.offsetWidth + 'px');
    thumb.style.setProperty('--x', (on.offsetLeft - 0) + 'px');
  }

  $$('[data-tabs]').forEach(function (sw) {
    var tabs = $$('[role="tab"]', sw);
    function select(tab, focus, silent) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        var panel = d.getElementById(t.getAttribute('aria-controls'));
        if (panel) {
          panel.hidden = !on;
          if (on && !silent && !reduce) { panel.classList.remove('panel-in'); void panel.offsetWidth; panel.classList.add('panel-in'); }
        }
      });
      if (focus) tab.focus();
      placeThumb(sw);
    }
    // keep the URL shareable without triggering a jump (replaceState fires no hashchange)
    function syncHash(tab) {
      var h = tab.getAttribute('data-hash');
      if (h && history.replaceState) history.replaceState(null, '', '#' + h);
    }
    sw.addEventListener('click', function (e) { var t = e.target.closest('[role="tab"]'); if (t) { select(t); syncHash(t); } });
    sw.addEventListener('keydown', function (e) {
      var i = tabs.indexOf(d.activeElement); if (i < 0) return;
      var next = { ArrowRight: tabs[(i + 1) % tabs.length], ArrowLeft: tabs[(i - 1 + tabs.length) % tabs.length], Home: tabs[0], End: tabs[tabs.length - 1] }[e.key];
      if (next) { e.preventDefault(); select(next, true); syncHash(next); }
    });
    function fromHash() {
      var h = location.hash.slice(1);
      var match = tabs.filter(function (t) { return t.getAttribute('data-hash') === h; })[0];
      if (match) {
        select(match, false, true);
        var anchor = sw.closest('[data-tabs-anchor]') || sw;
        setTimeout(function () { anchor.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); }, 80);
      }
    }
    select($('[aria-selected="true"]', sw) || tabs[0], false, true);
    fromHash();
    window.addEventListener('hashchange', fromHash);
    onResize(function () { placeThumb(sw); });
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(function () { placeThumb(sw); });
  });

  $$('[data-filter]').forEach(function (sw) {
    var btns = $$('button', sw);
    var items = $$(sw.getAttribute('data-filter'));
    var empty = $(sw.getAttribute('data-empty'));
    sw.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      btns.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      var kind = b.getAttribute('data-kind'), shown = 0;
      items.forEach(function (it) {
        var show = kind === 'all' || it.getAttribute('data-kind') === kind;
        it.hidden = !show;
        if (show) { shown++; if (!reduce) { it.classList.remove('panel-in'); void it.offsetWidth; it.classList.add('panel-in'); } }
      });
      if (empty) empty.hidden = shown > 0;
      placeThumb(sw);
    });
    placeThumb(sw);
    onResize(function () { placeThumb(sw); });
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(function () { placeThumb(sw); });
  });

  /* ---- 11. Advisor bio expand ----------------------------------------- */
  $$('[data-bio-toggle]').forEach(function (btn) {
    var bio = d.getElementById(btn.getAttribute('aria-controls'));
    var label = $('span', btn);
    btn.addEventListener('click', function () {
      var expanded = bio.classList.toggle('is-clamped') === false;
      btn.setAttribute('aria-expanded', String(expanded));
      label.textContent = expanded ? 'Show less' : 'Read full bio';
    });
  });

  /* ---- 12. One-time in-view reveals for data visuals ------------------ */
  $$('[data-inview]').forEach(function (el) {
    if (reduce) { el.classList.add('is-in'); return; }
    once(el, function () { el.classList.add('is-in'); });
  });

  /* ---- 13. Timeline rail ---------------------------------------------- */
  $$('[data-timeline]').forEach(function (tl) {
    var rail = $('.timeline__rail i', tl), items = $$('.milestone', tl);
    function update() {
      var r = tl.getBoundingClientRect(), vh = window.innerHeight;
      var p = reduce ? 1 : clamp((vh * .78 - r.top) / (r.height + vh * .2));
      rail.style.setProperty('--p', p.toFixed(4));
      items.forEach(function (it, i) { it.classList.toggle('is-reached', p >= (i / Math.max(1, items.length - 1)) * .96); });
    }
    onScroll(update); update();
  });

  /* ---- 14a. Population field (home registry: few, dispersed) --------- */
  $$('[data-population]').forEach(function (canvas) {
    var ctx = canvas.getContext('2d'), W, H, pts = [], raf = 0, live = false;
    var TAU = Math.PI * 2, gap = 15;
    function build() {
      var r = canvas.getBoundingClientRect(), dpr = Math.min(2, window.devicePixelRatio || 1);
      W = r.width; H = r.height;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      pts = [];
      var cols = Math.floor(W / gap), rows = Math.floor(H / gap);
      var ox = (W - (cols - 1) * gap) / 2, oy = (H - (rows - 1) * gap) / 2;
      for (var y = 0; y < rows; y++) for (var x = 0; x < cols; x++) {
        pts.push({ x: ox + x * gap, y: oy + y * gap, hot: Math.random() < .018, ph: Math.random() * 4000, warm: Math.random() < .6 });
      }
      paint(0);
    }
    function paint(t) {
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = 'rgba(255,255,255,.16)';
      for (var i = 0; i < pts.length; i++) {
        var p = pts[i]; if (p.hot) continue;
        ctx.beginPath(); ctx.arc(p.x, p.y, 1.3, 0, TAU); ctx.fill();
      }
      for (var j = 0; j < pts.length; j++) {
        var q = pts[j]; if (!q.hot) continue;
        var col = q.warm ? '242,101,34' : '255,222,23';
        var k = ((t + q.ph) % 4000) / 4000;
        if (!reduce) {
          ctx.beginPath(); ctx.arc(q.x, q.y, 4 + k * 22, 0, TAU);
          ctx.strokeStyle = 'rgba(' + col + ',' + (0.55 * (1 - k)).toFixed(3) + ')'; ctx.lineWidth = 1.5; ctx.stroke();
        }
        ctx.beginPath(); ctx.arc(q.x, q.y, 4.2, 0, TAU);
        ctx.fillStyle = 'rgb(' + col + ')'; ctx.fill();
      }
    }
    function loop(t) { paint(t); raf = requestAnimationFrame(loop); }
    build(); onResize(build);
    if (reduce || !hasIO) return;
    new IntersectionObserver(function (en) {
      live = en[0].isIntersecting;
      if (live && !raf) raf = requestAnimationFrame(loop);
      if (!live) { cancelAnimationFrame(raf); raf = 0; }
    }).observe(canvas);
  });

  /* ---- 14b. Motes: 300, one per million people with a rare disease ---- */
  $$('[data-motes]').forEach(function (canvas) {
    var ctx = canvas.getContext('2d'), W, H, motes = [], raf = 0, t0 = 0;
    var TAU = Math.PI * 2, N = 300, REVEAL = 1600;
    var FOOT = parseFloat(canvas.getAttribute('data-foot')) || 118;   // room for the stat
    var pairs = [[30, 10], [25, 12], [20, 15], [15, 20], [12, 25], [10, 30]];
    // fixed seed so every visitor sees the same field
    var seed = 7; function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }

    function build() {
      var r = canvas.getBoundingClientRect(), dpr = Math.min(2, window.devicePixelRatio || 1);
      W = r.width; H = r.height; if (!W || !H) return;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var pad = Math.max(24, W * .06), aw = W - pad * 2, ah = H - pad - FOOT;
      var best = pairs[0], diff = Infinity;
      pairs.forEach(function (p) { var d = Math.abs(Math.log((p[0] / p[1]) / (aw / ah))); if (d < diff) { diff = d; best = p; } });
      var cols = best[0], rows = best[1], gx = aw / cols, gy = ah / rows, rad = Math.max(2.2, Math.min(gx, gy) * .19);
      seed = 7; motes = [];
      for (var i = 0; i < N; i++) {
        var c = i % cols, rw = Math.floor(i / cols);
        motes.push({
          x: pad + gx * (c + .5) + (rnd() - .5) * gx * .5,
          y: pad * .8 + gy * (rw + .5) + (rnd() - .5) * gy * .5,
          r: rad * (.75 + rnd() * .5), warm: rnd() < .28,
          at: rnd() * REVEAL, ph: rnd() * TAU, sp: .6 + rnd() * .9
        });
      }
      paint(reduce ? Infinity : (t0 ? performance.now() - t0 : 0));
    }
    function paint(t) {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < motes.length; i++) {
        var m = motes[i];
        var k = t === Infinity ? 1 : clamp((t - m.at) / 520);
        if (k <= 0) continue;
        var e = 1 - Math.pow(1 - k, 3);
        var tw = reduce ? 1 : .78 + Math.sin((t === Infinity ? 0 : t) * .0012 * m.sp + m.ph) * .22;
        ctx.globalAlpha = e * tw;
        ctx.beginPath(); ctx.arc(m.x, m.y, m.r * (.4 + .6 * e), 0, TAU);
        ctx.fillStyle = m.warm ? '#F26522' : '#FFDE17'; ctx.fill();
      }
      ctx.globalAlpha = 1;
    }
    function loop(now) { if (!t0) t0 = now; paint(now - t0); raf = requestAnimationFrame(loop); }
    build(); onResize(build);
    if (reduce || !hasIO) { paint(Infinity); return; }
    new IntersectionObserver(function (en) {
      if (en[0].isIntersecting) { if (!raf) raf = requestAnimationFrame(loop); }
      else { cancelAnimationFrame(raf); raf = 0; }
    }, { rootMargin: '0px 0px -12% 0px' }).observe(canvas);
  });

  /* ---- 15. Plug-and-play rig ------------------------------------------ */
  $$('[data-rig]').forEach(function (rig) {
    var chips = $$('.rig__chip', rig), wrap = $('.rig__host-wrap', rig);
    var timer = 0, idx = 0, userTook = false;
    function run() { rig.classList.remove('is-run'); void rig.offsetWidth; rig.classList.add('is-run'); }
    function plug(i) {
      idx = i;
      chips.forEach(function (c, j) { c.setAttribute('aria-pressed', String(j === i)); });
      var old = $('.rig__host:not(.is-leaving)', wrap);
      var next = d.createElement('span');
      next.className = 'rig__host is-entering';
      next.textContent = chips[i].textContent;
      wrap.appendChild(next);
      requestAnimationFrame(function () { requestAnimationFrame(function () { next.classList.remove('is-entering'); }); });
      if (old) { old.classList.add('is-leaving'); setTimeout(function () { old.remove(); }, 750); }
      run();
    }
    chips.forEach(function (c, i) {
      c.addEventListener('click', function () { userTook = true; clearInterval(timer); if (i !== idx) plug(i); else run(); });
    });
    if (reduce || !hasIO) return;
    new IntersectionObserver(function (en) {
      clearInterval(timer);
      if (en[0].isIntersecting && !userTook) {
        run();
        timer = setInterval(function () { plug((idx + 1) % chips.length); }, 2600);
      }
    }, { threshold: .4 }).observe(rig);
  });

  /* ---- 15b. Region picker (distributors) ----------------------------- */
  $$('[data-regions]').forEach(function (list) {
    var tabs = $$('[role="tab"]', list);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1;
        var panel = d.getElementById(t.getAttribute('aria-controls'));
        if (panel) { panel.hidden = !on; if (on && !reduce) { panel.classList.remove('panel-in'); void panel.offsetWidth; panel.classList.add('panel-in'); } }
      });
      if (focus) tab.focus();
    }
    list.addEventListener('click', function (e) { var t = e.target.closest('[role="tab"]'); if (t) select(t); });
    list.addEventListener('keydown', function (e) {
      var i = tabs.indexOf(d.activeElement); if (i < 0) return;
      var step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
      var next = step ? tabs[(i + step + tabs.length) % tabs.length] : e.key === 'Home' ? tabs[0] : e.key === 'End' ? tabs[tabs.length - 1] : null;
      if (next) { e.preventDefault(); select(next, true); }
    });
    select(tabs[0]);
  });

  /* ---- 16. Respect reduced motion in SMIL graphics -------------------- */
  if (reduce) $$('svg').forEach(function (s) { if (s.pauseAnimations) s.pauseAnimations(); });

  scrollFns.forEach(function (f) { f(); });
})();
