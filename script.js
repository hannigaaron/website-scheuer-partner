(() => {
  'use strict';

  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const hasGSAP = !reduced && typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined';
  const root = document.documentElement;

  root.classList.remove('no-js');
  root.classList.add(hasGSAP ? 'js-gsap' : 'no-gsap');
  if (hasGSAP) gsap.registerPlugin(ScrollTrigger);

  /* ======================================================================
     Laufband aus den Leistungsbereichen
     ====================================================================== */
  const track = $('#marquee-track');
  if (track) {
    const words = (track.dataset.words || '').split('|').filter(Boolean);
    const row = words.map(w => `<span>${w}</span><i></i>`).join('');
    track.innerHTML = row + row;
  }

  /* ======================================================================
     Lenis: weiches Scrollen
     ====================================================================== */
  let lenis = null;
  if (!reduced && typeof Lenis !== 'undefined') {
    lenis = new Lenis({
      duration: 1.05,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      touchMultiplier: 1.6
    });
    if (hasGSAP) {
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add((t) => lenis.raf(t * 1000));
      gsap.ticker.lagSmoothing(0);
    } else {
      const loop = (t) => { lenis.raf(t); requestAnimationFrame(loop); };
      requestAnimationFrame(loop);
    }
  }

  const navOffset = () => -(($('#nav') || { offsetHeight: 76 }).offsetHeight + 12);
  $$('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id === '#' || id.length < 2) return;
      const target = $(id);
      if (!target) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(target, { offset: navOffset(), duration: 1.1 });
      else target.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' });
      history.replaceState(null, '', id);
    });
  });

  /* ======================================================================
     Navigation: Menü auf dem Handy, Untermenüs, klebende Leiste
     ====================================================================== */
  const nav = $('#nav');
  const burger = $('#burger');
  const setMenu = (open) => {
    if (!nav || !burger) return;
    nav.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
    document.body.style.overflow = open ? 'hidden' : '';
    if (lenis) open ? lenis.stop() : lenis.start();
  };
  if (burger) {
    burger.addEventListener('click', () => setMenu(!nav.classList.contains('is-open')));
    addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });
    $$('.nav-links a').forEach(a => a.addEventListener('click', () => setMenu(false)));
    matchMedia('(min-width: 981px)').addEventListener('change', (e) => { if (e.matches) setMenu(false); });
  }
  $$('.has-sub > button').forEach(btn => {
    btn.addEventListener('click', () => {
      const li = btn.parentElement;
      const open = !li.classList.contains('is-open');
      $$('.has-sub').forEach(x => { x.classList.remove('is-open'); x.firstElementChild.setAttribute('aria-expanded', 'false'); });
      li.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', String(open));
    });
  });
  addEventListener('click', (e) => {
    if (e.target.closest('.has-sub')) return;
    $$('.has-sub.is-open').forEach(x => { x.classList.remove('is-open'); x.firstElementChild.setAttribute('aria-expanded', 'false'); });
  });

  const progress = $('#progress');
  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const max = document.documentElement.scrollHeight - innerHeight;
      if (progress) progress.style.width = (max > 0 ? (scrollY / max) * 100 : 0) + '%';
      if (nav) nav.classList.toggle('is-stuck', scrollY > 8);
      ticking = false;
    });
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ======================================================================
     Einblendungen: GSAP, sonst IntersectionObserver
     ====================================================================== */
  /* Überschriften (h2) gehören dem Zoom und der Wortanimation, nicht der Einblendung:
     gsap.to mit overwrite würde sonst den Zoom abbrechen. */
  const revealables = $$('.reveal').filter(el => !el.closest('.hero') && el.tagName !== 'H2');

  if (hasGSAP) {
    gsap.set(revealables, { opacity: 0, y: 30 });
    const show = (els, stagger = { each: .09, amount: .7 }) => gsap.to(els, {
      opacity: 1, y: 0, duration: .8, stagger, ease: 'power3.out', overwrite: true,
      onStart: () => els.forEach(el => el.classList.add('is-visible'))
    });
    ScrollTrigger.batch(revealables, { start: 'top 88%', onEnter: (b) => show(b) });
    /* Sicherheitsnetz für Sprungmarken und sehr schnelles Scrollen */
    const catchUp = () => {
      const late = revealables.filter(el => {
        if (el.classList.contains('is-visible')) return false;
        const r = el.getBoundingClientRect();
        return r.top < innerHeight * .95 && r.bottom > 0;
      });
      if (late.length) show(late, { each: .04, amount: .35 });
    };
    let catchTimer;
    addEventListener('scroll', () => { clearTimeout(catchTimer); catchTimer = setTimeout(catchUp, 180); }, { passive: true });
    ScrollTrigger.addEventListener('refresh', catchUp);
    setTimeout(catchUp, 600);
  } else if (reduced || !('IntersectionObserver' in window)) {
    revealables.forEach(el => el.classList.add('is-visible'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const sibs = [...entry.target.parentElement.children].filter(c => c.classList.contains('reveal'));
        entry.target.style.transitionDelay = Math.min(sibs.indexOf(entry.target), 6) * 75 + 'ms';
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { threshold: .12, rootMargin: '0px 0px -60px' });
    revealables.forEach(el => io.observe(el));
  }

  /* ======================================================================
     Zähler: zählen beim Hereinscrollen hoch, der Endwert steht im HTML
     ====================================================================== */
  const counters = $$('[data-count]');
  const runCount = (el) => {
    const end = parseInt(el.dataset.count, 10);
    const from = parseInt(el.dataset.from || '0', 10);
    const suffix = el.dataset.suffix || '';
    const prefix = el.dataset.prefix || '';
    const o = { v: from };
    gsap.to(o, {
      v: end, duration: 1.8, ease: 'power3.out',
      onUpdate: () => { el.textContent = prefix + Math.round(o.v) + suffix; }
    });
  };

  /* ======================================================================
     GSAP: Auftakt und scroll-gesteuerte Effekte
     ====================================================================== */
  const splitWords = (el) => {
    if (!el || el.dataset.splitDone) return [];
    el.dataset.splitDone = '1';
    const words = el.textContent.trim().split(/\s+/);
    el.textContent = '';
    return words.map((w, i) => {
      const wrap = document.createElement('span');
      wrap.className = 'word-wrap';
      const inner = document.createElement('span');
      inner.className = 'word';
      inner.textContent = w;
      wrap.appendChild(inner);
      el.appendChild(wrap);
      if (i < words.length - 1) el.appendChild(document.createTextNode(' '));
      return inner;
    });
  };

  if (hasGSAP) {

    /* ---------- Auftakt der Startseite ----------------------------------
       Fünf senkrechte Lamellen, wie die Balken im Logo, öffnen sich nach
       dem Logo. Der Schleier entsteht nur hier im Skript: Ohne JavaScript
       ist die Seite sofort lesbar. Tippen, Scrollen oder eine Taste
       überspringt ihn, nach spätestens 4 Sekunden verschwindet er auf
       jeden Fall. */
    const hero = $('.hero');
    if (hero) {
      const firstVisit = (() => {
        try {
          if (sessionStorage.getItem('sp-intro')) return false;
          sessionStorage.setItem('sp-intro', '1');
        } catch (e) { /* privates Fenster: dann eben jedes Mal */ }
        return true;
      })();

      let curtain = null;
      if (firstVisit) {
        curtain = document.createElement('div');
        curtain.className = 'curtain';
        curtain.setAttribute('aria-hidden', 'true');
        curtain.innerHTML =
          Array.from({ length: 5 }, () => '<div class="curtain-slat"></div>').join('') +
          '<img class="curtain-logo" src="img/logo.png" alt="" width="1089" height="467" />' +
          '<span class="curtain-bar"></span>' +
          '<span class="curtain-skip">Überspringen</span>';
        document.body.appendChild(curtain);
      }

      const titleLines = $$('.hero-title .line > span');
      const intro = gsap.timeline({ defaults: { ease: 'power3.out' } });
      const dropCurtain = () => { curtain && curtain.remove(); curtain = null; };

      gsap.set('.hero-title', { transformOrigin: '18% 50%' });
      gsap.set(titleLines, { y: 0, yPercent: 108, opacity: 0 });
      gsap.set(['.eyebrow', '.hero .lead', '.hero-cta', '.stats'], { opacity: 0, y: 22 });
      gsap.set('.hero-media img', { scale: 1.2, opacity: 0, transformOrigin: '60% 30%' });
      gsap.set('.hero-wipe', { scaleY: 1 });
      gsap.set('.title-rule', { scaleX: 0 });

      if (curtain) {
        intro
          .fromTo('.curtain-logo', { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .7, ease: 'expo.out' }, 0)
          .to('.curtain-bar', { opacity: 1, duration: .3 }, .2)
          .to('.curtain-skip', { opacity: 1, duration: .4 }, .3)
          .to(['.curtain-logo', '.curtain-bar', '.curtain-skip'], { opacity: 0, duration: .3, ease: 'power2.in' }, 1.25)
          .to('.curtain-slat', { yPercent: -104, duration: .95, ease: 'expo.inOut', stagger: { each: .07, from: 'center' } }, 1.45)
          .add(dropCurtain, 2.7);
      }
      const t0 = curtain ? 1.9 : 0;

      intro
        .to(titleLines, { yPercent: 0, opacity: 1, duration: 1.1, stagger: .11, ease: 'expo.out' }, t0)
        .from('.hero-title', { scale: 1.8, xPercent: 5, yPercent: 8, filter: 'blur(14px)', duration: 2, ease: 'expo.out' }, t0)
        .to('.title-rule', { scaleX: 1, duration: .9, ease: 'expo.out' }, t0 + .9)
        .to('.hero-media img', { scale: 1, opacity: 1, duration: 1.8, ease: 'power3.out' }, t0 + .3)
        .to('.hero-wipe', { scaleY: 0, duration: 1.15, ease: 'expo.inOut' }, t0 + .34)
        .to('.eyebrow', { opacity: 1, y: 0, duration: .7 }, t0 + .55)
        .to('.hero .lead', { opacity: 1, y: 0, duration: .7 }, t0 + .7)
        .to('.hero-cta', { opacity: 1, y: 0, duration: .7 }, t0 + .82)
        .to('.stats', { opacity: 1, y: 0, duration: .7, onStart: () => counters.filter(c => c.closest('.stats')).forEach(runCount) }, t0 + 1);

      if (curtain) {
        const skip = () => {
          ['pointerdown', 'wheel', 'touchstart', 'keydown'].forEach(ev => removeEventListener(ev, skip));
          intro.progress(Math.max(intro.progress(), .5));
          dropCurtain();
        };
        ['pointerdown', 'wheel', 'touchstart', 'keydown'].forEach(ev => addEventListener(ev, skip, { once: true, passive: true }));
        setTimeout(dropCurtain, 4000);
      }

      /* Headline schrumpft beim Scrollen, Text und Bild laufen unterschiedlich schnell */
      gsap.fromTo('.hero-title-zoom', { scale: 1 }, {
        scale: matchMedia('(max-width: 820px)').matches ? .84 : .7, yPercent: -4, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: '+=520', scrub: .55 }
      });
      gsap.to('.hero-inner', { yPercent: -12, opacity: .4, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: .6 } });
      gsap.to('.hero-media', { yPercent: 8, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: .6 } });
      gsap.to('.hero-media img', { yPercent: -6, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: .5 } });
    }

    /* ---------- Seitenkopf der Unterseiten ---------- */
    const pageHead = $('.page-head');
    if (pageHead) {
      const h1 = $('h1', pageHead);
      const words = splitWords(h1);
      gsap.set(words, { yPercent: 115, opacity: 0 });
      gsap.set(['.crumbs', '.page-head .lead'], { opacity: 0, y: 18 });
      gsap.timeline({ delay: .1, defaults: { ease: 'expo.out' } })
        .to('.crumbs', { opacity: 1, y: 0, duration: .6 }, 0)
        .to(words, { yPercent: 0, opacity: 1, duration: 1, stagger: .07 }, .1)
        .to('.page-head .lead', { opacity: 1, y: 0, duration: .8, ease: 'power3.out' }, .5);
    }
    $$('.page-photo img').forEach(img => {
      gsap.fromTo(img, { yPercent: -6, scale: 1.08 }, { yPercent: 6, scale: 1, ease: 'none',
        scrollTrigger: { trigger: img.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
    });

    /* ---------- Jede Abschnitts-Headline startet gross und zieht sich zusammen.
       Der Platz dafür wird vorher im Layout reserviert (Innenabstand unten am
       Kasten), damit sie sich nie mit dem Text darunter überlagert. */
    /* Breite der längsten Zeile. Nach der Wortaufteilung besteht die Überschrift
       aus einzelnen Wortkästen: Dann zählt die Ausdehnung je Zeile, nicht das
       breiteste Einzelwort. */
    const lineWidth = (el) => {
      const wraps = $$('.word-wrap', el);
      if (wraps.length) {
        const lines = new Map();
        wraps.forEach(w => {
          const r = w.getBoundingClientRect();
          const key = Math.round(r.top / 8);
          const l = lines.get(key) || { a: Infinity, b: -Infinity };
          l.a = Math.min(l.a, r.left); l.b = Math.max(l.b, r.right);
          lines.set(key, l);
        });
        return Math.max(...[...lines.values()].map(l => l.b - l.a));
      }
      const r = document.createRange();
      r.selectNodeContents(el);
      const rects = [...r.getClientRects()];
      return rects.length ? Math.max(...rects.map(x => x.width)) : el.offsetWidth;
    };
    const heads = $$('main h2').filter(h => !h.closest('.legal'));
    heads.forEach(h2 => {
      if (h2.parentElement && h2.parentElement.classList.contains('head-box')) return;
      const box = document.createElement('div');
      box.className = 'head-box';
      h2.parentElement.insertBefore(box, h2);
      box.appendChild(h2);
    });
    const startOf = new Map();
    const measure = () => {
      const phone = matchMedia('(max-width: 820px)').matches;
      const wish = phone ? 1.34 : 1.5;
      const air = phone ? 52 : 88;
      const view = document.documentElement.clientWidth;
      heads.forEach(h2 => {
        const box = h2.parentElement;
        gsap.set(h2, { scale: 1 });
        box.style.paddingBottom = '0px';
        const line = Math.max(1, lineWidth(h2));
        const high = h2.offsetHeight || 1;
        const par = box.parentElement ? box.parentElement.getBoundingClientRect() : null;
        const centred = getComputedStyle(h2).textAlign === 'center';
        const room = centred
          ? Math.min(par ? par.width : view, view) - 8
          : Math.min(par ? par.right : view, view) - h2.getBoundingClientRect().left - 6;
        const s = Math.max(1, Math.min(wish, room / line, 1 + air / high));
        startOf.set(h2, s);
        box.style.paddingBottom = Math.round(high * (s - 1)) + 'px';
      });
    };
    measure();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { measure(); ScrollTrigger.refresh(); });
    heads.forEach(h2 => {
      gsap.fromTo(h2, { scale: () => startOf.get(h2) || 1 }, { scale: 1, ease: 'none', invalidateOnRefresh: true,
        scrollTrigger: { trigger: h2, start: 'top 97%', end: 'top 50%', scrub: .5 } });
    });
    let remeasure;
    addEventListener('resize', () => { clearTimeout(remeasure); remeasure = setTimeout(() => { measure(); ScrollTrigger.refresh(); }, 220); });

    /* Überschriften fahren Wort für Wort herein */
    $$('h2[data-split]').forEach(h2 => {
      const words = splitWords(h2);
      if (!words.length) return;
      gsap.set(words, { yPercent: 115, opacity: 0 });
      ScrollTrigger.create({ trigger: h2, start: 'top 86%', once: true,
        onEnter: () => gsap.to(words, { yPercent: 0, opacity: 1, duration: .85, stagger: .055, ease: 'expo.out' }) });
    });

    /* Vorzeilen schieben sich seitlich herein */
    $$('.kicker').forEach(k => {
      ScrollTrigger.create({ trigger: k, start: 'top 92%', once: true,
        onEnter: () => gsap.from(k, { x: -22, opacity: 0, duration: .7, ease: 'power3.out' }) });
    });

    /* Fotos laufen gegen ihre Flächen */
    $$('.media').forEach(m => {
      const img = $('img', m);
      gsap.fromTo(img, { yPercent: 5 }, { yPercent: -5, ease: 'none',
        scrollTrigger: { trigger: m, start: 'top bottom', end: 'bottom top', scrub: true } });
    });

    /* Staffelung für Kacheln, Karten, Personen, Vorteile */
    [['.tile', .08], ['.card', .05], ['.person', .1], ['.perk', .06], ['.news-item', .08], ['.stat', .08]].forEach(([sel, st]) => {
      if (!$(sel)) return;
      ScrollTrigger.batch(sel, { start: 'top 90%', once: true,
        onEnter: b => gsap.from(b, { y: 34, scale: .985, duration: .8, stagger: st, ease: 'power3.out' }) });
    });

    /* Zähler außerhalb des Hero */
    counters.filter(c => !c.closest('.stats')).forEach(el => {
      ScrollTrigger.create({ trigger: el, start: 'top 90%', once: true, onEnter: () => runCount(el) });
    });

    /* Zeitstrahl: Linie füllt sich, Jahre leuchten auf */
    const tl = $('.timeline');
    if (tl) {
      const fill = document.createElement('span');
      fill.className = 'tl-fill';
      tl.prepend(fill);
      const items = $$('li', tl);
      ScrollTrigger.create({
        trigger: tl, start: 'top 70%', end: 'bottom 60%', scrub: .4,
        onUpdate: (self) => {
          fill.style.height = (self.progress * 100) + '%';
          items.forEach(li => {
            const r = li.getBoundingClientRect();
            li.classList.toggle('is-on', r.top < innerHeight * .68);
          });
        }
      });
    }

    /* Laufband reagiert auf Scrollrichtung und Tempo */
    if (track) {
      const marquee = gsap.to(track, { xPercent: -50, repeat: -1, duration: 30, ease: 'none' });
      let resetter;
      ScrollTrigger.create({
        onUpdate: (self) => {
          const v = self.getVelocity();
          marquee.timeScale(gsap.utils.clamp(-4, 4, v / 320 || 1));
          gsap.to('.marquee', { skewX: gsap.utils.clamp(-4, 4, v / 900), duration: .4, overwrite: true });
          clearTimeout(resetter);
          resetter = setTimeout(() => { marquee.timeScale(1); gsap.to('.marquee', { skewX: 0, duration: .6, ease: 'power2.out' }); }, 140);
        }
      });
    }

    /* Schnittkanten neigen sich beim Durchscrollen leicht mit */
    $$('.cut-top').forEach(sec => {
      gsap.fromTo(sec, { '--cut': '4.4vw' }, { '--cut': '1.6vw', ease: 'none',
        scrollTrigger: { trigger: sec, start: 'top bottom', end: 'top 40%', scrub: .5 } });
    });

    /* Senkrechte Balken im Schlussabschnitt gleiten ein */
    $$('.cta-bars i').forEach((bar, i) => {
      gsap.from(bar, { scaleY: 0, transformOrigin: i < 3 ? 'top' : 'bottom', duration: 1.1, ease: 'expo.out',
        scrollTrigger: { trigger: '.cta', start: 'top 80%', once: true } });
    });

    addEventListener('load', () => ScrollTrigger.refresh());
  } else {
    /* ohne GSAP stehen die Zahlen direkt im HTML */
  }

  /* ======================================================================
     Magnetische Buttons und Neigung der Fotos
     ====================================================================== */
  if (!reduced && matchMedia('(pointer: fine)').matches) {
    $$('.magnetic').forEach(el => {
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2);
        const dy = e.clientY - (r.top + r.height / 2);
        if (hasGSAP) gsap.to(el, { x: dx * .18, y: dy * .26, duration: .4, ease: 'power3.out' });
        else el.style.transform = `translate(${dx * .18}px, ${dy * .26}px)`;
      });
      el.addEventListener('mouseleave', () => {
        if (hasGSAP) gsap.to(el, { x: 0, y: 0, duration: .6, ease: 'elastic.out(1, .4)' });
        else el.style.transform = '';
      });
    });
  }

  /* ======================================================================
     Skonto-Rechner (Beispielrechnung, rechnet im Browser, sendet nichts)
     Effektiver Jahreszins = Skonto / (100 - Skonto) * 360 / (Ziel - Frist)
     ====================================================================== */
  const calc = $('#skonto');
  if (calc) {
    const f = (n) => n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const val = (id) => parseFloat(String($('#' + id).value).replace(',', '.'));
    const out = { saving: $('#o-saving'), pay: $('#o-pay'), rate: $('#o-rate'), verdict: $('#o-verdict') };
    const run = () => {
      const amount = val('c-amount'), pct = val('c-pct'), early = val('c-early'), term = val('c-term');
      if (![amount, pct, early, term].every(Number.isFinite) || amount <= 0 || pct <= 0 || pct >= 100 || term <= early || early < 0) {
        out.saving.textContent = out.pay.textContent = out.rate.textContent = '–';
        out.verdict.textContent = 'Bitte gültige Werte eingeben. Das Zahlungsziel muss nach der Skontofrist liegen.';
        return;
      }
      const saving = amount * pct / 100;
      const rate = pct / (100 - pct) * 360 / (term - early) * 100;
      out.saving.textContent = f(saving) + ' €';
      out.pay.textContent = f(amount - saving) + ' €';
      out.rate.textContent = f(rate) + ' % p. a.';
      out.verdict.textContent = `Wer das Skonto nutzt, erzielt umgerechnet ${f(rate)} % Verzinsung pro Jahr. Liegt Ihr Zinssatz für Kontokorrent oder Kredit darunter, lohnt sich der Skontoabzug.`;
    };
    $$('input', calc).forEach(i => i.addEventListener('input', run));
    run();
  }

  /* ======================================================================
     Öffnungszeiten: heutigen Tag markieren, Status anzeigen (Zeit in Berlin)
     ====================================================================== */
  const hours = $('#hours');
  if (hours) {
    const parts = new Intl.DateTimeFormat('de-DE', { timeZone: 'Europe/Berlin', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false })
      .formatToParts(new Date()).reduce((o, p) => (o[p.type] = p.value, o), {});
    const day = { 'Mo.': 1, 'Di.': 2, 'Mi.': 3, 'Do.': 4, 'Fr.': 5, 'Sa.': 6, 'So.': 0 }[parts.weekday] ?? ({ Mo: 1, Di: 2, Mi: 3, Do: 4, Fr: 5, Sa: 6, So: 0 }[parts.weekday]);
    const now = parseInt(parts.hour, 10) * 60 + parseInt(parts.minute, 10);
    const slots = day >= 1 && day <= 4 ? [[480, 720], [780, 960]] : day === 5 ? [[480, 720]] : [];
    const open = slots.some(([a, b]) => now >= a && now < b);
    $$('tr[data-days]', hours).forEach(tr => {
      const [a, b] = tr.dataset.days.split('-').map(Number);
      if (day >= a && day <= b) tr.classList.add('is-today');
    });
    const badge = $('#open-badge');
    if (badge) {
      badge.textContent = open ? 'Jetzt geöffnet' : 'Aktuell geschlossen';
      badge.classList.toggle('is-open', open);
    }
  }

  /* ======================================================================
     Kontakt speichern: erzeugt die vCard im Browser, ohne Server
     ====================================================================== */
  $$('.vcard').forEach(btn => {
    btn.addEventListener('click', () => {
      const d = btn.dataset;
      const lines = ['BEGIN:VCARD', 'VERSION:3.0',
        `N:${d.last};${d.first};;;`, `FN:${d.first} ${d.last}`,
        'ORG:Scheuer & Partner mbB Steuerberatungsgesellschaft', `TITLE:${d.title}`,
        'TEL;TYPE=WORK,VOICE:+49714270000', 'TEL;TYPE=WORK,FAX:+497142700099',
        `EMAIL;TYPE=WORK:${d.mail}`,
        'ADR;TYPE=WORK:;;In den Freßäckern 10;Bietigheim-Bissingen;;74321;Deutschland',
        'URL:https://www.scheuer-partner.de', 'END:VCARD'];
      const blob = new Blob([lines.join('\r\n')], { type: 'text/vcard;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${d.first}-${d.last}.vcf`.replace(/\s+/g, '-');
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    });
  });

})();
