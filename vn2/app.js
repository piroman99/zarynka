// Зарянка — VN-эп1 «Пролог + Приёмная». Движок без зависимостей.
// Тумблеры: текст (подстрочник) ⇄ голос закадра ⇄ музыка — независимы.
// Навигация: → далее, ← назад, «Авто» — само листается; конец серии = экран, не авто-тизер.
// Голос — ПОСТРАНИЧНО (pg.vo), иначе 51 страница Приёмной не озвучивается.
(function () {
  const D = window.VN;
  const $ = (id) => document.getElementById(id);
  const bgA = $("bg-a"), bgB = $("bg-b");
  const castEls = Array.from(document.querySelectorAll("#cast .sprite"));
  const propEl = document.querySelector("#props .prop");   // статичный предмет сцены (скамейка)
  const box = $("box"), nameEl = $("name"), textEl = $("text"), chapter = $("chapter");
  const hud = $("hud"), title = $("title"), vlayer = $("vlayer"), znak = $("znak"), vskip = $("vskip");
  const music = $("music"), voice = $("voice");
  const cinema = $("cinema"), avm = $("avm"), skip = $("skip");
  const endScr = $("end"), prevBtn = $("prev"), nextBtn = $("next");
  const creditsEl = $("credits"), crList = $("crlist");   // титры (ролл)
  const crView = $("crview"), dedEl = $("ded");           // вьюпорт титров / посвящение
  const brk = $("brk");                     // акварельная перебивка между сценами
  const ovlEl = $("ovl");                    // титр-слой кадра (pg.ovl)
  const transEl = $("trans"), transLogo = $("translogo");  // долгий переход + лого
  const AVM = "../out/avm_v3_epic.mp4";

  const qp = new URLSearchParams(location.search);
  const OVL_OFF = qp.get("ovl") === "0";     // ?ovl=0 — кадр без титр-слоя (для пиксельных проверок)
  const INSTANT = qp.get("instant") === "1";     // не печатать по буквам (для скриншотов)
  const SHOT = qp.has("node");
  // ?ovln=N — тест-хук: показать ровно N букв надписи; ?ovlp=P — показать срез прогресса P (0..1)
  const OVL_N = qp.has("ovln") ? Math.max(0, parseInt(qp.get("ovln"), 10) || 0) : null;
  const OVL_P = qp.has("ovlp") ? Math.min(1, Math.max(0, parseFloat(qp.get("ovlp")) || 0)) : null;

  let curBg = "", curVo = "";
  let bgActive = bgA, other = bgB, typing = null;
  let musicKey = "", cinemaOpen = false, started = false, curNode = -1;
  let textOn = qp.get("text") !== "0";
  let voiceOn = qp.get("voice") !== "0";
  let musicOn = qp.get("music") !== "0";
  // Авто-режим включён ПО УМОЛЧАНИЮ (Иван 2026-10-21: «запускаться надо … авто сразу»);
  // отключается тумблером или адресом ?auto=0.
  const AUTO_DEFAULT = qp.get("auto") !== "0";
  let autoOn = AUTO_DEFAULT;

  let autoTimer = null, playToken = 0;
  let paused = qp.get("pause") === "1";
  // титр-слой: строки ждут свою фразу и печатаются под озвучку (0 ₽, решение Ивана 2026-11-04)
  let OVL_SPANS = [], OVL_LINES = [], OVL_PLATES = [], OVL_TICK = null, OVL_VOD = 0;
  let ovlRun = 0, ovlLast = 0;
  let ty = null, tyPaused = false;
  // Стартовый экран без титров (Иван 2026-10-21: «титры бы выключить по умолчанию»).
  // Остаются логотип, «Начать» и полоска загрузки; ?titles=1 возвращает надписи.
  if (qp.get("titles") !== "1") document.body.classList.add("notitles");
  // PACE = общий темп новеллы. 1.0 — как было, 0.8 = на 20% быстрее (решение Ивана 2026-10-19).
  // Можно переопределить из адреса: ?pace=0.9 — для сравнения на глаз.
  const PACE = (function () {
    const v = parseFloat(qp.get("pace"));
    return isFinite(v) && v >= 0.3 && v <= 2 ? v : 0.8;
  })();
  const AUTO_BASE = 450 * PACE, AUTO_PER_CHAR = 20 * PACE, AUTO_GAP = 500 * PACE;
  const TYPE_MS = Math.max(6, Math.round(18 * PACE));

  const NODES = D.nodes;
  // плоский список страниц всех сцен → единая навигация вперёд/назад
  const SCENES = [];
  NODES.forEach((nd, ni) => {
    if (nd.t === "scene") nd.pages.forEach((_, pi) => SCENES.push({ n: ni, p: pi }));
  });
  const scriptStart = {};
  SCENES.forEach((s, i) => { if (!(s.n in scriptStart)) scriptStart[s.n] = i; });
  let pos = 0;

  // ---------- ПРОГРЕСС И ОГЛАВЛЕНИЕ ----------
  // Иван 2026-11-09: третья кнопка на заставке — оглавление «как в книге»:
  // главы с подпунктами, счёт страниц, первая фраза, метка «пройдено».
  // Пройденное помнит localStorage (раньше движок вообще не помнил, где ты).
  const PROG_KEY = "zaryanka.progress.v1";
  function progLoad() {
    try {
      const v = JSON.parse(localStorage.getItem(PROG_KEY) || "null");
      if (v && typeof v.max === "number" && v.max >= 0) {
        return Math.min(Math.floor(v.max), SCENES.length - 1);
      }
    } catch (e) {}
    return -1;
  }
  function progSave() {
    try { localStorage.setItem(PROG_KEY, JSON.stringify({ max: progMax, at: Date.now() })); } catch (e) {}
  }
  let progMax = progLoad();        // дальний индекс SCENES, до которого дошли (-1 = ещё не начинали)
  function progMark(i) {
    if (SHOT || i < 0) return;     // скриншоты — не игра, прогресс не трогают
    if (i > progMax) { progMax = i; progSave(); }
  }
  function pagesWord(n) {
    const a = Math.abs(n) % 100, b = a % 10;
    if (a > 10 && a < 20) return "страниц";
    if (b === 1) return "страница";
    if (b >= 2 && b <= 4) return "страницы";
    return "страниц";
  }

  // Структура оглавления: глава → узлы content.js. id сверять с _vn2_nodes.node_index().
  const TOC = [
    { t: "Пролог", items: [
      ["s1", "Клич «Марс — дело общее»"],
      ["p6", "Вторая Марсианская"],
      ["p7", "Недостроенный корабль"],
      ["p8", "Стыковка у станции"],
      ["s3", "Зал · вопрос"],
      ["s4", "Ролик на скорую руку"],
      ["s5a", "Площадь · лозунг"],
      ["s5b", "Триумф"],
      ["s6", "Открытый конкурс"],
      ["s7", "Тысячи людей"],
    ] },
    { t: "Кабинет Старика", items: [["starik", ""]] },
    { t: "Приёмная", items: [["reception", ""]] },
    { t: "Аллея у ворот", items: [["steps", "Ступени"], ["alley", "У ворот"]] },
  ];

  function nodeById(id) {
    for (let i = 0; i < NODES.length; i++) if (NODES[i].id === id) return i;
    return -1;
  }
  function nodeStart(id) {                 // первая страница узла в SCENES
    const ni = nodeById(id);
    return ni < 0 ? -1 : (ni in scriptStart ? scriptStart[ni] : -1);
  }
  function nodePages(id) {
    const ni = nodeById(id);
    return ni < 0 ? 0 : ((NODES[ni].pages || []).length);
  }
  function nodeExcerpt(id) {               // первая фраза узла — как первая строка в книге
    const ni = nodeById(id);
    const pg = ni >= 0 && NODES[ni].pages && NODES[ni].pages[0];
    if (!pg || !pg.tx) return "";
    let s = String(pg.tx).split("\n")[0].trim();
    const m = s.match(/^[^.!?…]{14,}?[.!?…]/);
    if (m) s = m[0];
    if (s.length > 64) s = s.slice(0, 63).replace(/[\s,;:—–-]+$/, "") + "…";
    return s;
  }

  const tocEl = $("toc"), tocList = $("toclist"), tocNote = $("tocnote");
  let tocShown = false;
  function tocIsOpen() { return tocShown; }

  function renderToc() {
    if (!tocList) return;
    tocList.innerHTML = "";
    const hereId = (started && SCENES[pos]) ? NODES[SCENES[pos].n].id : null;
    TOC.forEach((ch) => {
      const st0 = nodeStart(ch.items[0][0]);
      const total = ch.items.reduce((s, it) => s + nodePages(it[0]), 0);
      const box = document.createElement("div");
      box.className = "toc-chap";
      // строка главы: сама кликабельна (ведёт на первую страницу главы)
      const head = document.createElement("button");
      head.type = "button";
      const lockedCh = !(st0 >= 0 && st0 <= progMax);
      head.className = "toc-row toc-chaprow" + (lockedCh ? " locked" : "") +
                       (st0 >= 0 && st0 <= progMax ? " done" : "") +
                       (ch.items.length === 1 && ch.items[0][0] === hereId ? " here" : "");
      head.disabled = lockedCh;
      const hn = document.createElement("span");
      hn.className = "n";
      hn.textContent = ch.t;
      const hp = document.createElement("span");
      hp.className = "pg";
      hp.textContent = total + " " + pagesWord(total);
      head.appendChild(hn);
      head.appendChild(hp);
      const ex = nodeExcerpt(ch.items[0][0]);
      if (ex) {
        const sn = document.createElement("span");
        sn.className = "sn";
        sn.textContent = ex;
        hn.appendChild(sn);
      }
      head.onclick = (e) => { e.stopPropagation(); if (!lockedCh) tocJump(st0); };
      box.appendChild(head);
      // подпункты — только там, где их реально несколько
      if (ch.items.length > 1) {
        ch.items.forEach((it) => {
          const id = it[0], label = it[1] || it[0];
          const st = nodeStart(id);
          if (st < 0) return;
          const cnt = nodePages(id);
          const locked = st > progMax;
          const b = document.createElement("button");
          b.type = "button";
          b.className = "toc-row" + (locked ? " locked" : "") +
                        (st <= progMax ? " done" : "") + (id === hereId ? " here" : "");
          b.disabled = locked;
          b.dataset.node = id;
          b.dataset.start = String(st);
          const n = document.createElement("span");
          n.className = "n";
          n.textContent = label;
          const p = document.createElement("span");
          p.className = "pg";
          p.textContent = cnt + " " + pagesWord(cnt);
          b.appendChild(n);
          b.appendChild(p);
          b.onclick = (e) => { e.stopPropagation(); if (!locked) tocJump(st); };
          const sub = document.createElement("div");
          sub.className = "toc-sub";
          sub.appendChild(b);
          box.appendChild(sub);
        });
      }
      tocList.appendChild(box);
    });
    if (tocNote) {
      const all = SCENES.length;
      tocNote.textContent = progMax < 0
        ? "ещё не начато · всего " + all + " " + pagesWord(all)
        : (progDone() ? "пройдено до конца · " + all + " " + pagesWord(all)
                      : "пройдено до стр. " + (progMax + 1) + " из " + all);
    }
  }

  function tocOpen() {
    if (!tocEl) return;
    renderToc();
    tocShown = true;
    tocEl.classList.add("show");
    tocEl.setAttribute("aria-hidden", "false");
    if (tocList) tocList.scrollTop = 0;
  }
  function tocClose() {
    if (!tocEl) return;
    tocShown = false;
    tocEl.classList.remove("show");
    tocEl.setAttribute("aria-hidden", "true");
  }
  function tocJump(i) {
    tocClose();
    if (started) { enterPos(i, true); return; }
    beginAt(i);
  }
  // запуск сразу с выбранной страницы (значок и посвящение — только через «Начать»)
  function beginAt(i) {
    started = true; starting = false; pendingGo = null;
    const btn = $("start");
    if (btn) { btn.textContent = "Начать"; btn.title = ""; }
    hideScreens();
    tryFullscreen();
    wakeOn();
    if (music.src && musicOn) music.play().catch(() => {});
    enterPos(i, true);
    updateStartBtn();
  }

  // «Начать» превращается в «Продолжить», если уже что-то пройдено.
  // Если серия дойдена до конца — снова «Начать» (продолжать с последней
  // страницы бессмысленно), а галочки в оглавлении остаются.
  function progDone() { return progMax >= SCENES.length - 1; }
  function updateStartBtn() {
    const btn = $("start");
    if (!btn || started || starting) return;
    if (progMax > 0 && !progDone()) {
      btn.textContent = "Продолжить";
      btn.title = "С " + (progMax + 1) + "-й страницы";
    } else {
      btn.textContent = "Начать";
      btn.title = progDone() ? "Серия пройдена — можно пересмотреть" : "";
    }
  }

  let resetArmed = false, resetT = null;
  function resetProg() {
    const b = $("toc-reset");
    if (!resetArmed) {                    // защита от случайного клика: два шага
      resetArmed = true;
      if (b) { b.classList.add("arm"); b.textContent = "Точно? Прогресс сотрётся"; }
      clearTimeout(resetT);
      resetT = setTimeout(() => {
        resetArmed = false;
        if (b) { b.classList.remove("arm"); b.textContent = "Сбросить прогресс"; }
      }, 4000);
      return;
    }
    clearTimeout(resetT);
    resetArmed = false;
    if (b) { b.classList.remove("arm"); b.textContent = "Сбросить прогресс"; }
    progMax = -1;
    try { localStorage.removeItem(PROG_KEY); } catch (e) {}
    renderToc();
    updateStartBtn();
  }

  // ---------- ПРЕДЗАГРУЗКА ----------
  // Кадры/голос качаются ЗАРАНЕЕ, чтобы не мигали во время просмотра.
  // Список берём из content.js (nd.bg / pg.cast / pg.vo / D.chars / D.music) —
  // ручной манифест не нужен, будущий контент подхватится сам.
  // ?preload=0 — выключить (и авто-отключка в режиме скриншотов ?node=N,
  // если явно не сказано ?node=N&preload=1).
  const PRELOAD_OFF = qp.get("preload") === "0" || (SHOT && qp.get("preload") !== "1");
  const PL_CONC = 4;                    // одновременных запросов (не душим канал)
  const plImg = new Map();              // url -> HTMLImageElement (держит декод)
  const plAud = new Map();              // url -> blob: (мгновенный старт без сети)
  const plVid = new Map();
  const plMiss = new Set();             // 404 — второй раз не просим
  const plSeen = new Map();             // "kind|url" -> задача (чтобы не дублировать)
  let plQ = [], plActive = 0, plDone = 0, plTotal = 0, plSeq = 0;

  function plStat() {
    const el = $("pl"), bar = $("plbar"), txt = $("pltext");
    const pct = plTotal ? Math.round(plDone * 100 / plTotal) : 100;
    if (bar) bar.style.width = pct + "%";
    const fin = plTotal > 0 && plDone >= plTotal;
    if (txt) { txt.textContent = fin ? "" : (plTotal ? "загрузка " + pct + "%" : ""); txt.classList.toggle("done", fin); }
    if (el) el.classList.toggle("done", fin);
  }

  function plPush(url, kind, prio) {
    if (PRELOAD_OFF || !url) return;
    if (kind === "img" && (plImg.has(url) || plMiss.has(url))) return;
    const key = kind + "|" + url, ex = plSeen.get(key);
    if (ex) { if (prio < ex.prio) ex.prio = prio; return; }   // уже в очереди — только поднимаем приоритет
    const t = { url: url, kind: kind, prio: prio, seq: plSeq++ };
    plSeen.set(key, t); plQ.push(t); plTotal++; plStat(); plPump();
  }

  function plRun(t) {
    const url = t.url;
    if (t.kind === "img") {
      return new Promise((res) => {
        const im = new Image();
        plImg.set(url, im);
        im.decoding = "async";
        const fin = () => res();
        im.onload = () => { (im.decode ? im.decode() : Promise.resolve()).then(fin, fin); };
        im.onerror = () => { plImg.delete(url); plMiss.add(url); fin(); };
        im.src = url;
      });
    }
    const store = t.kind === "audio" ? plAud : plVid;
    if (store.has(url) || plMiss.has(url)) return Promise.resolve();
    return fetch(url, { cache: "force-cache" })
      .then((r) => (r.ok ? r.blob() : Promise.reject(new Error(r.status))))
      .then((b) => { store.set(url, URL.createObjectURL(b)); })
      .catch(() => { plMiss.add(url); });
  }

  function plPump() {
    while (plActive < PL_CONC && plQ.length) {
      let bi = 0;
      for (let i = 1; i < plQ.length; i++) {
        const a = plQ[i], b = plQ[bi];
        if (a.prio < b.prio || (a.prio === b.prio && a.seq < b.seq)) bi = i;
      }
      const t = plQ.splice(bi, 1)[0];
      plActive++;
      plRun(t).then(() => {}, () => {}).then(() => { plActive--; plDone++; plStat(); plPump(); });
    }
  }

  function plPage(i, prio) {
    const s = SCENES[i]; if (!s) return;
    const nd = NODES[s.n], pg = nd.pages[s.p];
    if (s.p === 0) plPush(nd.bg, "img", prio);
    if (pg.bg) plPush(pg.bg, "img", prio);
    if (pg.cast) [pg.cast.l, pg.cast.r].forEach((c) => {
      if (!c) return;
      plPush(charUrl(c[0], c[1]), "img", prio);
      plPush(charUrl(c[0], "neutral"), "img", prio);
    });
    voList(pg, nd).forEach((u) => plPush(u, "audio", prio));
  }
  function plNode(ni, prio) {
    const nd = NODES[ni]; if (!nd || nd.t !== "scene") return;
    plPush(nd.bg, "img", prio);
    voList(null, nd).forEach((u) => plPush(u, "audio", prio));
  }

  // весь эп1 в очередь: сначала ближние страницы, в конце — музыка и тизер
  function plBuild() {
    if (PRELOAD_OFF) return;
    plPush("img/logo.png", "img", 0);
    NODES.forEach((nd) => { if (nd.t === "znak") plPush(nd.video, "video", 0); });
    SCENES.forEach((_, i) => plPage(i, i < 2 ? 0 : 1 + Math.floor(i / 6)));
    Object.keys(D.chars || {}).forEach((w) => {
      const ch = D.chars[w];
      plPush(ch.base, "img", 90);
      Object.keys(ch.emos || {}).forEach((e) => plPush(ch.emos[e], "img", 90));
    });
    Object.keys(D.music || {}).forEach((k) => plPush(D.music[k], "audio", 95));
    plPush(AVM, "video", 99);
  }

  // при входе на страницу — поднять вперёд следующие 6
  function plWarm(from) {
    if (PRELOAD_OFF) return;
    for (let i = from; i < Math.min(SCENES.length, from + 6); i++) plPage(i, 0);
  }

  // ждём готовности конкретных url (только для старейшего запуска)
  function plWhen(list, ms) {
    const lim = Math.ceil((ms || 15000) / 100);
    return Promise.all(list.map((u) => new Promise((res) => {
      let n = 0;
      const tick = () => {
        if (plMiss.has(u)) return res();
        const im = plImg.get(u);
        if (im && im.complete && im.naturalWidth) return res();
        if (plAud.has(u) || plVid.has(u)) return res();
        if (n++ > lim) return res();   // не держим зрителя бесконечно
        setTimeout(tick, 100);
      };
      tick();
    })));
  }

  // ---------- фон / спрайт ----------
  function setBg(url) {
    if (url === curBg) return;
    curBg = url;
    clearCam();                         // при смене фона гасим наезд камеры
    other.style.backgroundImage = url ? `url("${url}")` : "none";
    other.classList.add("on");
    if (INSTANT) { other.style.transition = "none"; other.style.opacity = 1; }
    bgActive.classList.remove("on");
    if (INSTANT) bgActive.style.opacity = 0;
    [bgActive, other] = [other, bgActive];
  }

  // ---------- камера: «наезд» = ДВУХБИТ ОДНИМ КАДРОМ (широкий → врезка) ----------
  // pg.cam = {from,to,x,y,hold,dur}: start wide, then push in to (x,y) over dur s.
  let camTimer = null;
  function clearCam() {
    clearTimeout(camTimer); camTimer = null;
    [bgA, bgB].forEach((el) => {
      el.style.transition = ""; el.style.transform = ""; el.style.transformOrigin = "";
    });
  }
  function applyCam(pg) {
    clearTimeout(camTimer); camTimer = null;
    const el = bgActive; if (!el) return;
    const c = pg && pg.cam;
    if (!c) { el.style.transition = ""; el.style.transform = ""; el.style.transformOrigin = ""; return; }
    const x = (c.x != null ? c.x : 0.5) * 100, y = (c.y != null ? c.y : 0.5) * 100;
    const from = (c.from != null ? c.from : 1), to = (c.to != null ? c.to : 1.4);
    el.style.transition = "none";
    el.style.transformOrigin = x + "% " + y + "%";
    el.style.transform = "scale(" + from + ")";
    void el.offsetWidth;                 // зафиксировать «широкий» кадр (бит 1)
    if (INSTANT) { el.style.transform = "scale(" + to + ")"; return; }
    const hold = (c.hold != null ? c.hold : 0.9) * 1000 * PACE,
          dur = (c.dur != null ? c.dur : 3.4) * PACE;
    camTimer = setTimeout(() => {        // бит 2: плавный наезд
      el.style.transition = "opacity .6s ease, transform " + dur + "s ease-in-out";
      el.style.transform = "scale(" + to + ")";
    }, hold);
  }
  // ---------- персонажи: ДВА слота, эмоции, кроссфейд, говорящий ярко ----------
  // Слот 0 = левый, слот 1 = правый. Кто на сцене — из pg.cast {l,r,speak},
  // его пишет _vn2_build.py. Эмоции — из D.chars[who].emos (нейтр. = база).
  function charUrl(who, emo) {
    const ch = D.chars && D.chars[who];
    if (!ch) return null;
    return (ch.emos && (ch.emos[emo] || ch.emos.neutral)) || ch.base || null;
  }
  // Предмет сцены (скамейка): ставится по УЗЛУ (nd.prop) и НИЧЕГО не анимирует.
  // Пустое значение = убрать (например, на странице CG, где кадр рисуется целиком).
  function applyProp(p) {
    if (!propEl) return;
    if (!p || !p.src) { propEl.classList.remove("on"); propEl.removeAttribute("src"); return; }
    if (propEl.getAttribute("src") !== p.src) propEl.src = p.src;
    propEl.style.left = p.left || "50%";
    propEl.style.bottom = p.bottom || "-3%";
    propEl.style.height = p.h || "40%";
    propEl.classList.add("on");
  }
  function applySlot(i, who, emo) {
    const el = castEls[i]; if (!el) return;
    // сброс инлайновой opacity: в режиме скриншота (INSTANT) она ставится в 1 и
    // иначе переживает снятие класса .on — спрайт остаётся видимым на CG-странице
    if (!who) { el.classList.remove("on", "dim", "breathe"); el.style.opacity = ""; return; }
    const url = charUrl(who, emo);
    if (!url) { el.classList.remove("on", "dim", "breathe"); el.style.opacity = ""; return; }
    el.dataset.base = charUrl(who, "neutral") || url;
    if (el.getAttribute("src") !== url) el.src = url;
    el.classList.toggle("seated", !!(D.chars && D.chars[who] && D.chars[who].seated));
    el.classList.add("on", "breathe");
    if (INSTANT) { el.style.transition = "none"; el.style.opacity = 1; }
  }
  function renderCast(c) {
    c = c || {};
    const l = c.l, r = c.r, sp = c.speak;
    applySlot(0, l && l[0], l && l[1]);
    applySlot(1, r && r[0], r && r[1]);
    // Сидящего НЕ центруем, когда он остался один (правка 2026-11-05, сцена «аллея»):
    // скамейка-проп стоит на месте, и от центровки фигура уезжала бы с неё.
    const seated = (who) => !!(who && D.chars && D.chars[who] && D.chars[who].seated);
    const solo = !(l && r) && !seated(l && l[0]) && !seated(r && r[0]);
    castEls[0].classList.toggle("solo", solo);
    castEls[1].classList.toggle("solo", solo);
    castEls[0].classList.toggle("dim", !!(l && r && sp && l[0] !== sp));
    castEls[1].classList.toggle("dim", !!(l && r && sp && r[0] !== sp));
  }
  function clearCast() { castEls.forEach((el) => el.classList.remove("on", "dim", "breathe", "solo", "seated")); }
  // нет файла эмоции -> откат на базовый спрайт (движок готов к доб. эмоциям)
  castEls.forEach((el) => el.addEventListener("error", () => {
    if (el.dataset.base && el.getAttribute("src") !== el.dataset.base) el.src = el.dataset.base;
  }));

  // ---------- музыка ----------
  // Смена трека = короткий фейд-аут → подмена источника → фейд-ин.
  // Без этого переход пролог→кабинет Старика начинался с резкого обрыва трека.
  let fadeT = null;
  // Громкость, к которой стремится музыка. 1 = обычная; меньше — приглушение на
  // долгом переходе (флешбэк в кабинет). Нужна именно цель, а не разовый fade:
  // на стыке пролог→кабинет трек ещё и подменяется (setMusic), и без общей цели
  // фейд-ин подмены возвращал бы полную громкость прямо в затемнении.
  let duck = 1;
  function fadeTo(v, ms, done) {
    clearInterval(fadeT);
    const from = music.volume, t0 = performance.now();
    fadeT = setInterval(() => {
      const k = Math.min(1, (performance.now() - t0) / Math.max(1, ms));
      music.volume = from + (v - from) * k;
      if (k >= 1) { clearInterval(fadeT); music.volume = v; if (done) done(); }
    }, 30);
  }
  // приглушить/вернуть музыку (только если она вообще играет)
  function duckTo(v, ms) {
    duck = v;
    if (musicOn && started && !music.paused) fadeTo(v, ms);
  }
  function setMusic(key) {
    if (key === musicKey) return;
    musicKey = key;
    const src = D.music[key];
    if (!src) return;
    const swap = () => {
      music.src = plAud.get(src) || src;   // предзагруженный blob — стартует мгновенно
      music.volume = 0;
      if (musicOn && started) music.play().catch(() => {});
      fadeTo(duck, 700);
    };
    if (musicOn && started && !music.paused) fadeTo(0, PACE * 380, swap);
    else { swap(); music.volume = 1; }
  }

  // ---------- голос (постранично, может быть НЕСКОЛЬКО сегментов) ----------
  // Обычно страница озвучена одним файлом. Но склеенная страница
  // «— Спасибо, — от улыбки…» имеет ДВА голоса: реплику читает персонаж,
  // авторскую вставку — закадр. Тогда pg.vo = [файл, файл], pg.vwho = [кто, кто].
  // Играем их подряд одним потоком.
  let voQ = [];
  // Отложенный старт голоса на длинном переходе: картинка гаснет, показывается жетон,
  // и только когда снова светло — начинается речь новой сцены. Без этого голос кабинета
  // читал ПОД тёмным экраном и паузы-тишины не было
  // (Иван 2026-10-21: «пауза между прологом и кабинетом не тормозит голос, почти нет тишины»).
  let voDelay = 0;        // мс: сколько ждать (ставит sceneTrans, съедает playVoice)
  let voTimer = null;     // таймер отложенного старта
  let voWaitMs = 0;       // сколько ещё ждать — чтобы автолист не уехал вперёд
  // Версия озвучки в адресе (?v=N): иначе браузер и GitHub Pages отдают старый
  // mp3 из кеша даже после Ctrl+F5 — force-cache в предзагрузке перезагрузка не отменяет.
  function voUrl(u) { return D.voVer ? u + "?v=" + D.voVer : u; }
  function voList(pg, nd) {
    let l = [];
    if (pg && pg.vo) l = Array.isArray(pg.vo) ? pg.vo.slice() : [pg.vo];
    else if (nd && nd.vo) l = [nd.vo];
    return l.map(voUrl);
  }
  function stopVoice() {
    clearTimeout(voTimer); voTimer = null; voWaitMs = 0; voDelay = 0;
    voice.pause();
    voice.removeAttribute("src");
    curVo = "";
    voQ = [];
  }
  function playVoice(pg, nd) {
    const d = voDelay;                    // забрать ДО stopVoice: он обнуляет задержку
    stopVoice();
    if (!voiceOn) return;
    voQ = voList(pg, nd);                 // страница → узел (совместимость)
    if (!voQ.length) return;
    curVo = voQ.join("|");
    if (d > 0) {
      voWaitMs = d;
      voTimer = setTimeout(() => {
        voTimer = null; voWaitMs = 0;
        playVoNext();
        if (autoOn && typingDone()) scheduleAuto();   // автолист ждал голоса
      }, d);
      return;
    }
    playVoNext();
  }
  function playVoNext() {
    if (!voQ.length) return;
    const src = voQ.shift();
    voice.src = plAud.get(src) || src;    // предзагруженный blob — без сетевой паузы
    voice.volume = 1.0;
    voice.play().catch(() => {});
  }

  // ---------- печать ----------
  // LETTERS: каждая буква — <span> со своей анимацией (проявляется из размытия и оседает).
  // Это не PNG-спрайты букв: вес нулевой, чётко на любом экране, работает с подстрочником.
  // Отключается адресом: ?letters=0
  const LETTERS = qp.get("letters") !== "0";

  function typeText(s, cb) {
    clearInterval(typing);
    ty = { full: s, i: 0, cb: cb };
    tyPaused = false;
    textEl.textContent = "";
    if (INSTANT) { textEl.textContent = s; ty.i = s.length; typing = null; ovlSync(); if (cb) cb(); return; }
    typing = setInterval(typeTick, TYPE_MS);
  }
  function typeTick() {
    if (tyPaused || !ty) return;
    const ch = ty.full[ty.i++];
    if (LETTERS && ch !== " ") {
      const sp = document.createElement("span");
      sp.className = "ch";
      sp.textContent = ch;
      textEl.appendChild(sp);
    } else {
      textEl.appendChild(document.createTextNode(ch));
    }
    ovlSync();                        // буквы надписи идут следом за подстрочником
    if (ty.i >= ty.full.length) { clearInterval(typing); typing = null; ovlSync(); if (ty.cb) ty.cb(); }
  }
  function typingDone() { return !ty || ty.i >= ty.full.length; }
  function skipTyping() {
    if (ty && ty.i < ty.full.length) {
      clearInterval(typing); typing = null; textEl.textContent = ty.full; ty.i = ty.full.length;
      ovlSync();
    }
  }

  // ---------- рендер ----------
  function showHud(on) { hud.style.opacity = on ? "" : 0; hud.classList.toggle("on", on); }
  function hideScreens() {
    title.classList.remove("show"); endScr.classList.remove("show"); vlayer.hidden = true;
  }

  // ---------- перебивка между сценами ----------
  // Смена узла (пролог → кабинет Старика → приёмная) больше не рывок: фон уходит под
  // акварельную «промокашку», под ней же меняются фон/каст/музыка, потом заливка тает.
  let inBreak = false, brkT = null, brkCb = null;
  function sceneBreak(cb) {
    if (!brk) { cb(); return; }
    brkCb = cb;
    clearTimeout(brkT);
    brk.classList.add("on");
    brkT = setTimeout(() => {
      const f = brkCb; brkCb = null;
      if (f) f();
      brkT = setTimeout(() => brk.classList.remove("on"), 120);
    }, PACE * 220);
  }
  // Долгий переход «в кабинет Старика» (узел trans:"fade"):
  // затемнение → жетон в темноте → осветление → и только потом речь.
  // Иван 2026-10-21: «переход с проходной на кабинет должен быть чуть подольше,
  // затемнением, а потом осветлением; может даже лого показать» → потом «слишком
  // короткая пауза, сделай общую длину 4 секунды».
  // Тайминги заданы так, чтобы СУММА (включая тишину после света) была ровно 4000 мс:
  // 750 + 80 + 580 + 920 + 420 + 1100 = 3850 видимая часть, + 150 тишины = 4000.
  const TR = { dark: 750, gap: 80, logoIn: 580, hold: 920, logoOut: 420, light: 1100 };
  const TR_DUCK = 0.32;              // музыка в темноте перехода — тише втрое
  const TR_VIS = TR.dark + TR.gap + TR.logoIn + TR.hold + TR.logoOut + TR.light;
  const TR_TOTAL = 4000;             // полная тишина от клика до первого слова
  const TR_SILENCE = TR_TOTAL - TR_VIS;   // тишина после того, как стало светло
  let transT = [], transActive = false;
  // погасить переход сейчас: снять затемнение/жетон, вернуть музыку
  function endTrans(quick) {
    transT.forEach(clearTimeout); transT = [];
    transActive = false;
    if (transEl) transEl.classList.remove("on");
    if (transLogo) transLogo.classList.remove("on");
    if (duck !== 1) duckTo(1, quick ? 260 : 760);
  }
  function sceneTrans(cb) {
    if (!transEl) { cb(); return; }
    brkCb = cb;
    clearTimeout(brkT);
    transT.forEach(clearTimeout); transT = [];
    transActive = true;
    const at = (ms, fn) => transT.push(setTimeout(fn, ms));
    duckTo(TR_DUCK, 340);                              // музыка уходит вместе с кадром
    stopVoice();                                       // и голос тоже — вот она, тишина
    transEl.classList.add("on");                       // затемнение
    at(TR.dark, () => {
      // сцена меняется в темноте, но ГОЛОС молчит до конца перехода:
      // речь стартует через (остаток видимой части + хвост тишины) = TR_TOTAL - TR.dark
      voDelay = (TR_VIS - TR.dark) + TR_SILENCE;
      const f = brkCb; brkCb = null; if (f) f();
    });
    at(TR.dark + TR.gap, () => transLogo && transLogo.classList.add("on"));
    at(TR.dark + TR.gap + TR.logoIn + TR.hold,
       () => transLogo && transLogo.classList.remove("on"));
    at(TR.dark + TR.gap + TR.logoIn + TR.hold + TR.logoOut, () => endTrans(false));
  }
  // клик во время перебивки = сразу пройти её (иначе на стыке сцен теряются нажатия).
  // Работает и когда сцена уже сменилась в темноте — тогда сразу догоняем отложенный голос.
  function finishBreak() {
    if (!brkCb && !transActive) return;
    const f = brkCb; brkCb = null;
    clearTimeout(brkT);
    if (brk) brk.classList.remove("on");
    endTrans(true);
    inBreak = false;
    voDelay = 0;                         // голос не ждать: пользователь уже прошёл
    if (f) { f(); return; }
    if (voWaitMs > 0) {                  // сцена уже стоит, ждём только голос
      clearTimeout(voTimer); voTimer = null; voWaitMs = 0;
      playVoNext();
      if (autoOn && typingDone()) scheduleAuto();
    }
  }

  // ---------- титр-слой кадра (pg.ovl) ----------
  // Надписи кадров пролога до 2026-11-01 вжигались в PNG и висели весь кадр. Теперь это
  // DOM-слой ПОВЕРХ кадра. Строка приходит НА СВОЕЙ ФРАЗЕ: у каждой строки в content.js
  // есть `at` — доля текста страницы, на которой эта фраза звучит (Иван 2026-11-04:
  // «я думал под озвучку… появляется вместе с фразой»). Часы берём у ОЗВУЧКИ
  // (voice.currentTime/duration), а если голоса нет — у длительности записи (pg.vod)
  // или у печати подстрочника. Буквы внутри строки идут очередью LINE_MS.
  // Координаты и кегли — в пространстве 2400x1350 (как было в _prolog_finals.py).
  // Элемент: {t,f,s,c,x,y,a,at} — текст; {b:[x0,y0,x1,y1],c,a,bl} — скрим/плашка.
  const LINE_MS = Math.max(12, Math.round(24 * PACE));   // одна буква строки

  function applyOvl(pg) {
    if (!ovlEl) return;
    ovlEl.textContent = "";
    OVL_SPANS = []; OVL_LINES = []; OVL_PLATES = []; OVL_VOD = 0;
    ovlRun = 0; ovlLast = performance.now();
    clearInterval(OVL_TICK); OVL_TICK = null;
    if (OVL_OFF) { ovlEl.classList.remove("on"); return; }   // ?ovl=0 — снимок кадра без слоя (проверки)
    const list = (pg && pg.ovl) || null;
    if (!list || !list.length) { ovlEl.classList.remove("on"); return; }
    OVL_VOD = (pg && pg.vod) || 0;             // длительность озвучки страницы, сек
    const E = 2400;
    const px = ovlEl.clientWidth || 2400;
    ovlEl.style.fontSize = px + "px";       // 1em = ширина кадра
    list.forEach(function (it) {
      if (it.b) {                            // мягкая плашка/скрим под текст
        const b = it.b, el = document.createElement("i");
        el.style.left = b[0] / E * 100 + "%";
        el.style.top = b[1] / 1350 * 100 + "%";
        el.style.width = (b[2] - b[0]) / E * 100 + "%";
        el.style.height = (b[3] - b[1]) / 1350 * 100 + "%";
        el.style.borderRadius = 20 / E + "em";
        el.style.background = "rgba(" + (it.c || [6, 8, 14]).join(",") + "," +
          ((it.a == null ? 150 : it.a) / 255).toFixed(3) + ")";
        if (it.bl) el.style.filter = "blur(" + (it.bl / E) + "em)";
        el.style.opacity = 0;                // плашка выезжает вместе с первой строкой, а не пустым прямоугольником
        ovlEl.appendChild(el);
        OVL_PLATES.push(el);
        return;
      }
      const el = document.createElement("b");
      const spans = [];
      // буквы кладём span'ами СРАЗУ (ширина строки и её центровка не пляшут при наборе),
      // видимыми они станут по очереди — см. ovlTick(). Пробелы — обычные текстовые узлы.
      Array.prototype.forEach.call(String(it.t), function (c) {
        if (c === " ") { el.appendChild(document.createTextNode(c)); return; }
        const sp = document.createElement("span");
        sp.textContent = c;
        el.appendChild(sp);
        OVL_SPANS.push(sp);
        spans.push(sp);
      });
      el.style.fontSize = (it.s || 48) / E + "em";
      el.style.fontFamily = (it.f === "l" ? "LatoBold" : "URWGothicDemi") + ",sans-serif";
      el.style.color = it.c || "#f6eede";
      // ВАЖНО: left/top — в ПРОЦЕНТАХ кадра, а не в em. У строки свой font-size (кегль),
      // и em в left/top считается от него, а не от ширины кадра: из-за этого все надписи
      // уезжали в левый верхний угол и обрезались (баг найден 2026-11-04).
      el.style.left = ((it.x == null ? 1200 : it.x) / E * 100) + "%";
      el.style.top = ((it.y == null ? 675 : it.y) / 1350 * 100) + "%";
      const a = it.a || "mm";
      el.style.transform = (a === "mm") ? "translate(-50%,-50%)"
                         : (a === "lt" ? "none" : "translateX(-50%)");
      ovlEl.appendChild(el);
      OVL_LINES.push({ spans: spans, at: (it.at == null ? 0 : it.at), i: 0, t0: -1 });
    });
    ovlEl.classList.add("on");
    if (INSTANT || !LETTERS || OVL_N !== null || OVL_P !== null) {
      ovlTestReveal();                        // снимки/проверки — без ожидания фраз
    } else {
      ovlTick();                              // первая строка ставится сразу (at=0)
      OVL_TICK = setInterval(ovlTick, 40);
    }
  }

  // ---------- набор букв титр-слоя ----------
  // Одна буква — один span. Строка ждёт свою фразу (`at`), затем пишется очередью LINE_MS.
  // Часы слоя (ovlRun) стоят на паузе/при скрытом тексте — буквы тоже стоят.
  function ovlShow(sp) {
    if (!sp || sp.dataset.on) return;
    sp.dataset.on = "1";
    // ?instant=1 / ?letters=0 — без анимации: в headless-снимках CSS-анимация под
    // виртуальным временем замирает на кадре opacity:0 и кадр «без надписей».
    sp.classList.add(LETTERS && !INSTANT ? "in" : "plain");
  }
  function ovlClock() {                     // накопленное «игровое» время слоя, сек
    const now = performance.now();
    if (!paused && !tyPaused && started) ovlRun += (now - ovlLast) / 1000;
    ovlLast = now;
    return ovlRun;
  }
  function ovlProgress() {
    if (OVL_P !== null) return OVL_P;                     // тест-хук ?ovlp=0.4
    if (INSTANT) return 1;
    if (voiceOn && curVo && !voice.paused && isFinite(voice.duration) && voice.duration > 0.2) {
      return Math.min(1, voice.currentTime / voice.duration);   // часы озвучки — главные
    }
    if (OVL_VOD > 0.2 && !typing && !ty) return Math.min(1, ovlClock() / OVL_VOD);  // голоса нет и печати нет
    if (ty && ty.full && ty.full.length) return ty.i / ty.full.length;   // голос выключен — по печати
    return 1;
  }
  function ovlTestReveal() {                // режимы снимков: ?instant / ?letters=0 / ?ovln / ?ovlp
    OVL_LINES.forEach(function (L) {
      if (OVL_P !== null && L.at > OVL_P) return;
      if (OVL_N !== null) {
        const room = OVL_N - OVL_SPANS.filter(function (s) { return s.dataset.on; }).length;
        L.spans.slice(0, Math.max(0, room)).forEach(ovlShow);
        return;
      }
      L.spans.forEach(ovlShow);
    });
    if (OVL_LINES.length && OVL_LINES.some(function (L) { return L.spans[0] && L.spans[0].dataset.on; })) {
      ovlPlateOn();
    }
  }
  function ovlPlateOn() {                    // плашка = часть надписи: ждёт первую строку
    OVL_PLATES.forEach(function (el) { el.style.opacity = ""; });
  }
  function ovlTick() {
    if (!OVL_LINES.length) { clearInterval(OVL_TICK); OVL_TICK = null; return; }
    if (OVL_N !== null || OVL_P !== null || INSTANT) return;
    const t = ovlClock(), p = ovlProgress();
    let pending = false;
    OVL_LINES.forEach(function (L) {
      if (L.i >= L.spans.length) return;               // строка дописана
      if (p < L.at) { pending = true; return; }        // её фраза ещё не звучит
      if (L.t0 < 0) L.t0 = t;                          // фраза пошла — строка пишется
      ovlPlateOn();                                    // и плашка появляется вместе с ней
      const k = Math.floor((t - L.t0) * 1000 / LINE_MS);
      while (L.i < L.spans.length && L.i < k) ovlShow(L.spans[L.i++]);
      if (L.i < L.spans.length) pending = true;
    });
    if (!pending) { clearInterval(OVL_TICK); OVL_TICK = null; }
  }
  function ovlSync() { ovlTick(); }          // совместимость: тик печати тоже подталкивает слой

  function enterPos(i, skipBreak) {
    if (i < 0) i = 0;
    if (i > SCENES.length - 1) return enterEnd();
    const s0 = SCENES[i];
    if (!skipBreak && s0.n !== curNode && curNode >= 0 && !INSTANT && !inBreak) {
      clearTimeout(autoTimer);
      playToken++;                       // гасим отложенный автолист
      inBreak = true;
      const long = NODES[s0.n] && NODES[s0.n].trans === "fade";
      (long ? sceneTrans : sceneBreak)(() => { inBreak = false; enterPos(i, true); });
      return;
    }
    inBreak = false;
    playToken++;
    pos = i;
    progMark(i);                     // помним, докуда дошли — для «Продолжить» и замков в оглавлении
    const s = SCENES[i], nd = NODES[s.n], pg = nd.pages[s.p];
    clearTimeout(autoTimer);
    showHud(true);
    hideScreens();
    chapter.textContent = D.episode;
    if (s.n !== curNode) {
      setMusic(nd.music || musicKey);
      curNode = s.n;
    }
    // страницу можно перекрыть своим кадром (CG): pg.bg важнее фона сцены
    const wantBg = pg.bg || nd.bg;
    if (wantBg !== curBg) setBg(wantBg);
    applyProp(pg.cg ? null : nd.prop);   // CG = кадр целиком, предмет сцены не нужен
    renderCast(pg.cast);
    applyCam(pg);
    applyOvl(pg);                    // надписи кадра — по страницам (было вожжено в PNG)
    plWarm(i);                       // заранее тянем следующие страницы
    if (pg.name) { nameEl.style.visibility = "visible"; nameEl.textContent = pg.name; }
    else nameEl.style.visibility = "hidden";
    playVoice(pg, nd);
    typeText(pg.tx, scheduleAuto);
    prevBtn.disabled = (pos === 0);
  }

  // ---------- авто-режим ----------
  function scheduleAuto() {
    clearTimeout(autoTimer);
    if (!autoOn || paused || cinemaOpen || !started) return;
    // голос новой сцены ещё ждёт конца перехода — не считаем время, стартуем после него
    if (voWaitMs > 0) return;
    const s = SCENES[pos]; if (!s) return;
    const nd = NODES[s.n], pg = nd.pages[s.p];
    const t = playToken;
    let delay = AUTO_BASE + Math.min(1900, pg.tx.length * AUTO_PER_CHAR);
    if (voiceOn && curVo && !voice.paused && isFinite(voice.duration)) {
      const remain = Math.max(0, (voice.duration - voice.currentTime)) * 1000;
      delay = Math.max(delay, remain + AUTO_GAP);
    }
    autoTimer = setTimeout(() => {
      if (t !== playToken || !autoOn) return;
      // страница ещё говорит (второй сегмент в очереди или голос не дочитал) — не листаем
      const speaking = voQ.length || (voiceOn && curVo && !voice.paused
        && isFinite(voice.duration) && voice.currentTime < voice.duration - 0.08);
      if (speaking) { scheduleAuto(); return; }
      next();
    }, delay);
  }

  // ---------- навигация ----------
  function next() {
    clearTimeout(autoTimer);
    if (!started) return;                 // титул/меню: листать нечего
    if (inBreak) { finishBreak(); return; }
    if (!vlayer.hidden) { vskip.click(); return; }   // идёт интро-значок → пропустить
    if (paused) { paused = false; tyPaused = false; syncToggles(); }
    if (!typingDone()) {                      // сперва дописать страницу
      const s = SCENES[pos]; const pg = NODES[s.n].pages[s.p];
      skipTyping(); textEl.textContent = pg.tx;
      if (autoOn) scheduleAuto();
      return;
    }
    enterPos(pos + 1);
  }
  function prev() {
    clearTimeout(autoTimer);
    if (!started) return;
    if (inBreak) { finishBreak(); return; }
    if (cinemaOpen) return;
    if (!vlayer.hidden) return;
    if (paused) { paused = false; tyPaused = false; syncToggles(); }
    if (pos > 0) enterPos(pos - 1);
  }

  function enterEnd() {
    clearTimeout(autoTimer);
    playToken++;
    curNode = -1;
    clearCast();
    applyProp(null);        // предмет сцены не должен висеть над финальным экраном
    clearCam();
    paused = false; tyPaused = false;
    showHud(false);
    vlayer.hidden = true;
    title.classList.remove("show");
    prevBtn.disabled = true;
    voice.pause();
    wakeOff();                       // серия закончилась — экран может гаснуть
    // титры в конце показываются САМИ (Иван 2026-10-24); после них — экран конца
    // серии. Отключить для снимка экрана «Конец»: ?credits=0
    endScr.classList.add("show");
    if (qp.get("credits") !== "0" && !crOpen()) openCredits();  // openCredits убирает экран конца
  }
  // Возврат в меню = сброс к «первому запуску». Без сброса started/starting
  // кнопка «Начать» после прохождения молчала (start() упирался в started=true),
  // работал только «Тизер».
  function goMenu() {
    clearTimeout(autoTimer);
    closeCredits();
    dedShown = false; clearTimeout(dedT); dedT = null;
    if (dedEl) { dedEl.classList.remove("show"); dedEl.setAttribute("aria-hidden", "true"); }
    wakeOff();
    clearTimeout(brkT); brkCb = null; inBreak = false;
    transT.forEach(clearTimeout); transT = [];
    if (brk) brk.classList.remove("on");
    if (transEl) transEl.classList.remove("on");
    if (transLogo) transLogo.classList.remove("on");
    duck = 1;                       // в меню музыка не должна остаться приглушённой
    playToken++;
    curNode = -1;
    clearCast();
    applyProp(null);
    clearCam();
    paused = false; tyPaused = false;
    pos = 0;
    started = false; starting = false; pendingGo = null;
    updateStartBtn();                // «Продолжить», если прогресс есть (или «Начать» после сброса)
    plStat();                        // вернуть полосу загрузки в актуальное состояние
    try { znak.onended = null; znak.pause(); } catch (err) {}
    showHud(false); hideScreens();
    setBg("");
    music.pause(); stopVoice();
    musicKey = null;                 // иначе setMusic() на рестарте решит «уже играет»
    title.classList.add("show");
    autoOn = AUTO_DEFAULT; syncToggles();
  }

  // ---------- титул / значок ----------
  function enterTitle() {
    showHud(false); hideScreens(); music.pause(); voice.pause();
    title.classList.add("show");
  }
  function enterZnak(nd) {
    showHud(false); hideScreens();
    setMusic("prolog");
    vlayer.hidden = false;
    znak.src = plVid.get(nd.video) || nd.video;   // предзагруженный blob — без чёрного кадра
    znak.currentTime = 0;
    znak.play().catch(() => {});
    const done = () => { vlayer.hidden = true; try { znak.pause(); } catch (e) {} znak.onended = null; enterDed(); };
    znak.onended = done;
    vskip.onclick = (e) => { e.stopPropagation(); done(); };
  }

  // ---------- посвящение (сразу после лого-значка, до пролога) ----------
  // Текст — дословно из рассказа (story.txt, строки 1 и 3), берётся из content.js.
  const DED = NODES.find((n) => n.t === "ded");
  const DED_MS = 7000;                     // сколько висеть, если не кликнули
  let dedShown = false, dedT = null;
  function dedOpen() { return dedShown; }
  function enterDed() {
    clearTimeout(autoTimer);
    if (!DED) return enterPos(0);
    showHud(false); hideScreens();
    $("ded-l1").textContent = DED.l1 || "";
    $("ded-l2").textContent = DED.l2 || "";
    dedShown = true;
    dedEl.classList.add("show");
    dedEl.setAttribute("aria-hidden", "false");
    clearTimeout(dedT); dedT = null;
    if (autoOn) dedT = setTimeout(leaveDed, DED_MS);   // в ручном режиме ждёт клика
  }
  function leaveDed() {
    if (!dedShown) return;
    dedShown = false; clearTimeout(dedT); dedT = null;
    dedEl.classList.remove("show");
    dedEl.setAttribute("aria-hidden", "true");
    if (started) enterPos(0);
  }

  let starting = false, pendingGo = null;
  function start() {
    if (started) return;
    if (starting) {                       // повторный клик — не ждать загрузку
      const g = pendingGo; pendingGo = null; starting = false;
      if (g) g();
      return;
    }
    starting = true;
    const btn = $("start");
    const go = () => {
      if (started) return;
      started = true; starting = false; pendingGo = null;
      btn.textContent = "Начать";
      hideScreens();
      tryFullscreen();                 // клик = жест: можно сразу во весь экран
      wakeOn();                        // и экран больше не гаснет
      if (music.src && musicOn) music.play().catch(() => {});
      if (progMax > 0 && !progDone()) { enterPos(progMax, true); return; }   // «Продолжить» — туда, где остановились
      enterZnak(NODES[1]);
    };
    if (PRELOAD_OFF) return go();
    // ждём только КРИТИЧНОЕ (значок + S1 + его голос), не весь эп1
    const crit = [];
    NODES.forEach((nd) => { if (nd.t === "znak") crit.push(nd.video); });
    const first = SCENES[(progMax > 0 && !progDone()) ? progMax : 0];
    if (first) {
      const nd = NODES[first.n];
      crit.push(nd.bg);
      crit.push(nd.pages[first.p].vo || nd.vo);
    }
    pendingGo = go;
    btn.textContent = "Загрузка…";
    btn.title = "Клик — начать, не дожидаясь загрузки";
    plWhen(crit.filter(Boolean), 12000).then(() => { if (pendingGo) pendingGo(); });
  }

  // ---------- кинозал ----------
  function playCinema(src) {
    clearTimeout(autoTimer);
    cinemaOpen = true;
    avm.src = plVid.get(src) || src; cinema.hidden = false;
    requestAnimationFrame(() => cinema.classList.add("on"));
    music.pause();
    const done = () => {
      cinemaOpen = false; cinema.classList.remove("on");
      avm.pause(); avm.removeAttribute("src"); avm.load();
      setTimeout(() => { cinema.hidden = true; }, 400);
      if (started && musicOn && !endScr.classList.contains("show")) music.play().catch(() => {});
      if (autoOn && !endScr.classList.contains("show")) scheduleAuto();
    };
    avm.onended = done;
    skip.onclick = (e) => { e.stopPropagation(); done(); };
    cinema.onclick = done;
    avm.play().catch(() => {});
  }

  // ---------- тумблеры ----------
  function syncToggles() {
    $("t-text").classList.toggle("off", !textOn);
    $("t-voice").classList.toggle("off", !voiceOn);
    $("t-music").classList.toggle("off", !musicOn);
    const au = $("t-auto");
    au.classList.toggle("on", autoOn && !paused);
    au.classList.toggle("pause", autoOn && paused);
    au.classList.toggle("off", !autoOn);
    $("t-pause").hidden = !autoOn;
    $("t-pause").textContent = paused ? "▶" : "⏸";
    $("t-pause").classList.toggle("on", paused);
    document.getElementById("stage").classList.toggle("notext", !textOn);
    document.getElementById("stage").classList.toggle("paused", paused);
  }
  $("t-text").onclick = (e) => { e.stopPropagation(); textOn = !textOn; syncToggles(); };
  $("t-voice").onclick = (e) => {
    e.stopPropagation(); voiceOn = !voiceOn; syncToggles();
    if (!voiceOn) voice.pause();
    else { const s = SCENES[pos]; if (s) { const nd = NODES[s.n]; playVoice(nd.pages[s.p], nd); } }
    if (autoOn) scheduleAuto();
  };
  $("t-music").onclick = (e) => {
    e.stopPropagation(); musicOn = !musicOn; syncToggles();
    if (!musicOn) { clearInterval(fadeT); music.volume = 1; music.pause(); }
    else if (started) music.play().catch(() => {});
  };
  $("t-auto").onclick = (e) => {
    e.stopPropagation();
    autoOn = !autoOn;
    if (!autoOn) { paused = false; tyPaused = false; clearTimeout(autoTimer); }
    syncToggles();
    // В МЕНЮ таймер не запускаем: иначе «Авто» на титуле сразу перелистывал
    // новеллу и проглатывал видео с жетоном (баг, найден Иваном 2026-10-21).
    if (autoOn && started && !paused && typingDone()) scheduleAuto();
  };
  $("t-pause").onclick = (e) => { e.stopPropagation(); togglePause(); };

  // ---------- сворачиваемый тулбар (только портрет) ----------
  // В портрете ряд из шести кнопок наезжал на кадр, поэтому он прячется за ☰.
  // На десктопе #t-menu скрыт, .open ни на что не влияет — поведение прежнее.
  const tools = $("tools"), tMenu = $("t-menu");
  function setToolsOpen(on) {
    tools.classList.toggle("open", !!on);
    tMenu.textContent = on ? "✕" : "☰";
    tMenu.setAttribute("aria-expanded", on ? "true" : "false");
    tMenu.title = on ? "Скрыть кнопки" : "Кнопки: авто, текст, голос, музыка, экран";
  }
  tMenu.onclick = (e) => { e.stopPropagation(); setToolsOpen(!tools.classList.contains("open")); };
  // Вариант B (Иван, 2026-11-09): ряд НЕ сворачивается сам — висит открытым,
  // пока не нажмёшь ✕. Так удобнее, когда щёлкаешь два тумблера подряд.
  setToolsOpen(false);

  // пауза: замораживает таймер + голос + печать (резюм с того же места)
  function togglePause() {
    if (!autoOn) return;
    if (!paused) {
      paused = true;
      clearTimeout(autoTimer);
      tyPaused = true;
      if (!voice.paused) voice.pause();
    } else {
      paused = false;
      tyPaused = false;
      if (voiceOn && curVo && voice.currentTime > 0 && voice.currentTime < voice.duration) {
        voice.play().catch(() => {});
      }
      scheduleAuto();
    }
    stage.classList.toggle("paused", paused);   // замораживает анимацию букв
    syncToggles();
  }

  // ---------- титры: кинематографический ролл ----------
  // Появляются в конце серии САМИ (Иван 2026-10-24), вручную — кнопкой «Титры»
  // на экране конца серии. Крутятся снизу вверх; скорость считается от высоты
  // ролла, чтобы длинные титры не пролетали мимо глаз за пяток секунд.
  const CR_SPEED = 44;                            // px/сек (было 52 — титры стали тише, «грустнее»)
  const CR_POS = parseFloat(qp.get("crpos"));     // ?crpos=0.45 — замер кадра для скриншота
  let crT = null;
  function crOpen() { return creditsEl.classList.contains("show"); }
  function crEl(tag, cls, txt) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }
  function renderCredits() {
    if (!crList || crList.dataset.done === "1") return;
    const hero = crEl("div", "cr-hero");
    const emb = crEl("img", "cr-emb");            // жетон-значок над названием
    emb.src = "img/trans_logo.png?v=" + (D.emblemVer || D.voVer || 1);
    emb.alt = "";
    hero.appendChild(emb);
    hero.appendChild(crEl("p", "cr-title", D.title || "ЗАРЯНКА"));
    if (D.episode) hero.appendChild(crEl("p", "cr-ep", D.episode));
    if (D.byline) hero.appendChild(crEl("p", "cr-by", D.byline));
    crList.appendChild(hero);
    (D.credits || []).forEach(function (g) {
      const blk = crEl("div", "crgrp");
      if (g.h) blk.appendChild(crEl("p", "crh", g.h));
      (g.rows || []).forEach(function (r) {
        const p = crEl("div", "crrow");
        const cut = r.indexOf("|");
        if (cut > 0) {                       // «роль|исполнитель» → роль над именем
          p.appendChild(crEl("span", "crrole", r.slice(0, cut).trim()));
          p.appendChild(crEl("span", "crname", r.slice(cut + 1).trim()));
        } else {
          p.appendChild(crEl("span", "crname", r));
        }
        blk.appendChild(p);
      });
      (g.notes || []).forEach(function (n) { blk.appendChild(crEl("p", "crnote", n)); });
      crList.appendChild(blk);
    });
    const fin = crEl("div", "crfin");
    fin.appendChild(crEl("p", "crfin-ttl", D.title || "ЗАРЯНКА"));
    fin.appendChild(crEl("p", "crfin-line", "Ждите следующих серий"));
    crList.appendChild(fin);
    crList.dataset.done = "1";
  }
  function runRoll() {
    if (!crList || !crView) return;
    clearTimeout(crT); crT = null;
    crList.classList.remove("run");
    crList.style.animationDelay = "";
    crList.style.animationPlayState = "";
    const h = crList.offsetHeight || crList.scrollHeight || 0;
    const vh = crView.clientHeight || window.innerHeight || 0;
    const dur = Math.min(90, Math.max(10, (vh + h) / CR_SPEED));
    crList.style.setProperty("--cr-dur", dur.toFixed(2) + "s");
    void crList.offsetWidth;                 // рестарт анимации с начала
    crList.classList.add("run");
    if (isFinite(CR_POS)) {                  // режим скриншота: замер на доле пути
      crList.style.animationDelay = (-CR_POS * dur).toFixed(2) + "s";
      crList.style.animationPlayState = "paused";
      return;
    }
    crT = setTimeout(finishCredits, dur * 1000 + 350);   // страховка, если animationend не придёт
  }
  function stopRoll() {
    clearTimeout(crT); crT = null;
    if (!crList) return;
    crList.classList.remove("run");
    crList.style.animationDelay = "";
    crList.style.animationPlayState = "";
  }
  function openCredits() {
    renderCredits();
    endScr.classList.remove("show");        // титры — поверх пустого кадра, не поверх кнопок
    creditsEl.classList.add("show");
    creditsEl.setAttribute("aria-hidden", "false");
    runRoll();
  }
  function finishCredits() {
    if (!crOpen()) return;
    closeCredits();
    if (started) { endScr.classList.add("show"); fitScreens(); }
  }
  function closeCredits() {
    creditsEl.classList.remove("show");
    creditsEl.setAttribute("aria-hidden", "true");
    stopRoll();
  }
  if (crList) crList.addEventListener("animationend", (e) => {
    if (e.animationName === "crUp") finishCredits();
  });

  // ---------- ввод ----------
  $("start").onclick = (e) => { e.stopPropagation(); start(); };
  $("teaser").onclick = (e) => { e.stopPropagation(); playCinema(AVM); };
  if ($("toc-open")) $("toc-open").onclick = (e) => { e.stopPropagation(); tocOpen(); };
  if ($("toc-x")) $("toc-x").onclick = (e) => { e.stopPropagation(); tocClose(); };
  if ($("toc-reset")) $("toc-reset").onclick = (e) => { e.stopPropagation(); resetProg(); };
  if (tocEl) tocEl.onclick = (e) => { if (e.target === tocEl) tocClose(); };   // клик мимо списка — закрыть
  $("e-menu").onclick = (e) => { e.stopPropagation(); goMenu(); };
  $("e-credits").onclick = (e) => { e.stopPropagation(); openCredits(); };
  $("cr-skip").onclick = (e) => { e.stopPropagation(); finishCredits(); };
  creditsEl.onclick = () => { finishCredits(); };     // клик по титрам — пропустить
  $("e-teaser").onclick = (e) => { e.stopPropagation(); playCinema(AVM); };
  prevBtn.onclick = (e) => { e.stopPropagation(); prev(); };
  nextBtn.onclick = (e) => { e.stopPropagation(); next(); };

  document.getElementById("stage").addEventListener("click", () => {
    if (tocShown) return;
    if (cinemaOpen || !vlayer.hidden || crOpen()) return;
    if (dedOpen()) { leaveDed(); return; }
    if (title.classList.contains("show") || endScr.classList.contains("show")) return;
    next();
  });
  addEventListener("keydown", (e) => {
    if (tocIsOpen()) {                   // оглавление: только Esc закрывает
      if (e.key === "Escape") { e.preventDefault(); tocClose(); }
      return;
    }
    if (dedOpen()) {                     // посвящение: любой « далее» уводит к прологу
      if ([" ", "Enter", "ArrowRight", "PageDown", "Escape"].includes(e.key)) { e.preventDefault(); leaveDed(); }
      return;
    }
    if (crOpen()) {                      // титры: листаются сами, любой « далее» — пропустить
      if ([" ", "Enter", "ArrowRight", "PageDown", "Escape"].includes(e.key)) { e.preventDefault(); finishCredits(); }
      return;
    }
    if (e.key === "Escape" && cinemaOpen) { skip.click(); return; }
    if (e.key === "Escape" && endScr.classList.contains("show")) { goMenu(); return; }
    if (cinemaOpen) return;
    if (!vlayer.hidden) {
      if (e.key === "Escape" || [" ", "Enter", "ArrowRight", "PageDown"].includes(e.key)) { e.preventDefault(); vskip.click(); }
      return;
    }
    if ([" ", "Enter", "ArrowRight", "PageDown"].includes(e.key)) {
      e.preventDefault();
      if (title.classList.contains("show")) return start();
      next();
    } else if (["ArrowLeft", "Backspace", "PageUp"].includes(e.key)) {
      e.preventDefault();
      if (title.classList.contains("show") || endScr.classList.contains("show")) return;
      prev();
    } else if (e.key === "p" || e.key === "P" || e.key === "\\u043f") {
      if (autoOn) { e.preventDefault(); togglePause(); }
    }
  });

  // свайп (тач) — слушаем весь документ: в портрете текст живёт вне 16:9-сцены
  let sx = 0, sy = 0, sw = false, swipedAt = 0;
  const stage = document.getElementById("stage");
  document.body.addEventListener("touchstart", (e) => {
    if (e.touches.length !== 1) return; sx = e.touches[0].clientX; sy = e.touches[0].clientY; sw = true;
  }, { passive: true });
  document.body.addEventListener("touchend", (e) => {
    if (!sw) return; sw = false;
    const dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
    if (cinemaOpen || crOpen() || dedOpen() || title.classList.contains("show") || endScr.classList.contains("show")) return;
    if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy)) {
      swipedAt = Date.now();
      dx < 0 ? next() : prev();
    }
  }, { passive: true });

  // ---------- вписать экраны в высоту (короткий ландшафт / портрет) ----------
  // Контент титула в em/процентах — на телефоне он выше вьюпорта, поэтому
  // масштабируем блок целиком, а не режем кнопки (раньше так терялся «Тизер»).
  let fitT = null;
  function fitScreens() {
    ["title", "end"].forEach((id) => {
      const sc = $(id); if (!sc) return;
      const inner = sc.querySelector(".title-inner"); if (!inner) return;
      inner.style.transform = "none";
      const avail = sc.clientHeight * 0.94;
      const h = inner.scrollHeight;
      if (avail > 0 && h > avail) inner.style.transform = "scale(" + (avail / h).toFixed(4) + ")";
    });
  }
  addEventListener("resize", () => { clearTimeout(fitT); fitT = setTimeout(fitScreens, 80); });
  addEventListener("orientationchange", () => setTimeout(fitScreens, 200));

  // ---------- полный экран (убрать адресную строку) ----------
  const fsBtn = $("t-full"), toastEl = $("toast");
  let toastT = null;
  function toast(msg, ms) {
    toastEl.textContent = msg; toastEl.classList.add("on");
    clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove("on"), ms || 4500);
  }
  const fsEl = () => document.fullscreenElement || document.webkitFullscreenElement || null;
  function fsSync() { if (fsBtn) fsBtn.classList.toggle("on", !!fsEl()); }
  // Фуллскрин ПО КНОПКЕ «Начать» (Иван 2026-10-21). Требует жеста пользователя — клик
  // как раз он, так что можно сразу, без отдельного тумблера. Не трогаем iOS Safari:
  // там фуллскрина для элемента нет (только для <video>), поэтому молча пропускаем.
  function tryFullscreen() {
    if (qp.get("fs") === "0" || INSTANT || fsEl()) return false;
    const root = document.documentElement;
    const req = root.requestFullscreen || root.webkitRequestFullscreen;
    if (!req) return false;
    fsTried++;
    try {
      const p = req.call(root);
      if (p && p.catch) p.catch(() => {});
      return true;
    } catch (e) { return false; }
  }
  // Экран не гаснет во время чтения. Wake Lock API: Chrome/Edge (Android и десктоп),
  // Safari 16.4+ (iOS 16.4+). Нужен HTTPS или localhost — на GitHub Pages это есть.
  // Отключается адресом ?wake=0. После сворачивания вкладки браузер снимает лок
  // сам, поэтому возвращаем его по visibilitychange.
  const WAKE_OK = "wakeLock" in navigator && qp.get("wake") !== "0";
  let wakeLock = null, wakeWant = false, fsTried = 0;
  function wakeOn() {
    wakeWant = true;
    if (!WAKE_OK || wakeLock || document.visibilityState !== "visible") return;
    navigator.wakeLock.request("screen").then((l) => {
      wakeLock = l;
      l.addEventListener("release", () => { wakeLock = null; });
    }).catch(() => {});
  }
  function wakeOff() {
    wakeWant = false;
    try { if (wakeLock) wakeLock.release(); } catch (e) {}
    wakeLock = null;
  }
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && wakeWant) wakeOn();
  });
  function toggleFs() {
    if (fsEl()) { (document.exitFullscreen || document.webkitExitFullscreen || function () {}).call(document); return; }
    const root = document.documentElement;
    const req = root.requestFullscreen || root.webkitRequestFullscreen;
    if (req) { try { const p = req.call(root); if (p && p.catch) p.catch(() => {}); return; } catch (e) {} }
    const v = cinemaOpen ? avm : (!vlayer.hidden ? znak : null);   // iPhone: фуллскрин только для <video>
    if (v && v.webkitEnterFullscreen) { v.webkitEnterFullscreen(); return; }
    toast("На iPhone страницу во весь экран не развернуть: адресную строку убирает только запуск с иконки «На экран Домой».");
  }
  if (fsBtn) fsBtn.onclick = (e) => { e.stopPropagation(); toggleFs(); };
  document.addEventListener("fullscreenchange", fsSync);
  document.addEventListener("webkitfullscreenchange", fsSync);
  fsSync();

  // в портрете подстрочник живёт ВНЕ 16:9-сцены → тап по нему тоже листает
  // (после свайпа клик игнорируем, иначе страница уезжает на две вперёд)
  $("box").addEventListener("click", (e) => {
    if (cinemaOpen || !vlayer.hidden || dedOpen()) return;
    if (title.classList.contains("show") || endScr.classList.contains("show")) return;
    e.stopPropagation();
    if (Date.now() - swipedAt < 450) return;
    next();
  });

  // ---------- init ----------
  if (INSTANT) stage.classList.add("nofx");
  $("tt").textContent = D.title;
  $("tep").textContent = D.episode;
  $("byline").textContent = D.byline;
  $("e-byline").textContent = D.byline;
  // голос дочитал страницу → не ждём полный расчётный таймер
  voice.addEventListener("ended", () => {
    if (voQ.length) { playVoNext(); return; }   // ещё сегменты той же страницы
    if (!autoOn || cinemaOpen) return;
    const s = SCENES[pos]; if (!s) return;
    const nd = NODES[s.n], pg = nd.pages[s.p];
    if (curVo && voList(pg, nd).join("|") === curVo) scheduleAuto();
  });
  syncToggles();
  updateStartBtn();                // «Продолжить» вместо «Начать», если прогресс сохранён
  // Значок перехода берётся с версией (D.emblemVer = хеш файла): иначе Pages отдаёт
  // старую картинку из кеша и форма (круг/пятиугольник) не меняется после пересборки.
  if (transLogo) transLogo.src = "img/trans_logo.png?v=" + (D.emblemVer || D.voVer || 1);
  plBuild();                       // запускаем фоновую предзагрузку с гл. экрана
  fitScreens();                    // титул/конец серии — вписать в высоту экрана
  if (location.protocol === "http:" || location.protocol === "https:") {
    // без service worker Chrome не ставит «на Домой» в режиме без адресной строки
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
  }
  // отладочные хуки для автотестов движка (без влияния на работу)
  window.__PL = { img: plImg, aud: plAud, vid: plVid, miss: plMiss,
                  queue: () => plQ.length, off: () => PRELOAD_OFF };
  window.__DBG = { get pos() { return pos; }, get node() { return curNode; },
                   get typing() { return !!typing; },
                   get started() { return started; }, get inBreak() { return inBreak; },
                   get paused() { return paused; }, get voQ() { return voQ.length; },
                   get wake() { return { want: wakeWant, held: !!wakeLock, ok: WAKE_OK }; },
                   get fs() { return !!fsEl(); },
                   get fsTried() { return fsTried; },
                   // состояние музыки — для проверок «трек не рвётся» (_music_probe.py)
                   get music() { return { paused: music.paused, t: music.currentTime,
                                          vol: music.volume, dur: music.duration,
                                          key: musicKey, duck: duck,
                                          src: (music.currentSrc || "").split("/").pop() }; } };
  window.__TOC = { open: tocOpen, close: tocClose, jump: tocJump, reset: resetProg,
                   render: renderToc, get max() { return progMax; },
                   get shown() { return tocShown; },
                   counts: () => TOC.map((c) => c.t + ":" + c.items.reduce((s, it) => s + nodePages(it[0]), 0)) };
  if (SHOT) {                      // режим скриншота: сразу к нужному узлу
    started = true;
    const ni = parseInt(qp.get("node"), 10);
    const nd = NODES[ni];
    if (nd && nd.t === "scene") {
      const base = scriptStart[ni] || 0;
      enterPos(base + parseInt(qp.get("page") || "0", 10));
    } else if (nd && nd.t === "znak") { enterZnak(nd); }
    else if (nd && nd.t === "ded") { enterDed(); }
    else if (nd && nd.t === "title") { enterTitle(); }
    else { enterEnd(); }
    if (qp.get("credits") === "1") openCredits();   // ?node=99&credits=1 — снимок титров
  }
  if (qp.get("toc") === "1") tocOpen();             // ?toc=1 — снимок оглавления без клика
})();
