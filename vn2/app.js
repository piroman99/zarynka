// Зарянка — VN-эп1 «Пролог + Приёмная». Движок без зависимостей.
// Тумблеры: текст (подстрочник) ⇄ голос закадра ⇄ музыка — независимы.
// Навигация: → далее, ← назад, «Авто» — само листается; конец серии = экран, не авто-тизер.
// Голос — ПОСТРАНИЧНО (pg.vo), иначе 51 страница Приёмной не озвучивается.
(function () {
  const D = window.VN;
  const $ = (id) => document.getElementById(id);
  const bgA = $("bg-a"), bgB = $("bg-b");
  const castEls = Array.from(document.querySelectorAll("#cast .sprite"));
  const box = $("box"), nameEl = $("name"), textEl = $("text"), chapter = $("chapter");
  const hud = $("hud"), title = $("title"), vlayer = $("vlayer"), znak = $("znak"), vskip = $("vskip");
  const music = $("music"), voice = $("voice");
  const cinema = $("cinema"), avm = $("avm"), skip = $("skip");
  const endScr = $("end"), prevBtn = $("prev"), nextBtn = $("next");
  const creditsEl = $("credits"), crList = $("crlist");   // титры (благодарности)
  const brk = $("brk");                     // акварельная перебивка между сценами
  const transEl = $("trans"), transLogo = $("translogo");  // долгий переход + лого
  const AVM = "../out/avm_v3_epic.mp4";

  const qp = new URLSearchParams(location.search);
  const INSTANT = qp.get("instant") === "1";     // не печатать по буквам (для скриншотов)
  const SHOT = qp.has("node");

  let curBg = "", curVo = "";
  let bgActive = bgA, other = bgB, typing = null;
  let musicKey = "", cinemaOpen = false, started = false, curNode = -1;
  let textOn = qp.get("text") !== "0";
  let voiceOn = qp.get("voice") !== "0";
  let musicOn = qp.get("music") !== "0";
  let autoOn = qp.get("auto") === "1";

  let autoTimer = null, playToken = 0;
  let paused = qp.get("pause") === "1";
  let ty = null, tyPaused = false;
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
  function applySlot(i, who, emo) {
    const el = castEls[i]; if (!el) return;
    if (!who) { el.classList.remove("on", "dim", "breathe"); return; }
    const url = charUrl(who, emo);
    if (!url) { el.classList.remove("on", "dim", "breathe"); return; }
    el.dataset.base = charUrl(who, "neutral") || url;
    if (el.getAttribute("src") !== url) el.src = url;
    el.classList.add("on", "breathe");
    if (INSTANT) { el.style.transition = "none"; el.style.opacity = 1; }
  }
  function renderCast(c) {
    c = c || {};
    const l = c.l, r = c.r, sp = c.speak;
    applySlot(0, l && l[0], l && l[1]);
    applySlot(1, r && r[0], r && r[1]);
    const solo = !(l && r);
    castEls[0].classList.toggle("solo", solo);
    castEls[1].classList.toggle("solo", solo);
    castEls[0].classList.toggle("dim", !!(l && r && sp && l[0] !== sp));
    castEls[1].classList.toggle("dim", !!(l && r && sp && r[0] !== sp));
  }
  function clearCast() { castEls.forEach((el) => el.classList.remove("on", "dim", "breathe", "solo")); }
  // нет файла эмоции -> откат на базовый спрайт (движок готов к доб. эмоциям)
  castEls.forEach((el) => el.addEventListener("error", () => {
    if (el.dataset.base && el.getAttribute("src") !== el.dataset.base) el.src = el.dataset.base;
  }));

  // ---------- музыка ----------
  // Смена трека = короткий фейд-аут → подмена источника → фейд-ин.
  // Без этого переход пролог→кабинет Старика начинался с резкого обрыва трека.
  let fadeT = null;
  function fadeTo(v, ms, done) {
    clearInterval(fadeT);
    const from = music.volume, t0 = performance.now();
    fadeT = setInterval(() => {
      const k = Math.min(1, (performance.now() - t0) / Math.max(1, ms));
      music.volume = from + (v - from) * k;
      if (k >= 1) { clearInterval(fadeT); music.volume = v; if (done) done(); }
    }, 30);
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
      fadeTo(1, 700);
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
  // Версия озвучки в адресе (?v=N): иначе браузер и GitHub Pages отдают старый
  // mp3 из кеша даже после Ctrl+F5 — force-cache в предзагрузке перезагрузка не отменяет.
  function voUrl(u) { return D.voVer ? u + "?v=" + D.voVer : u; }
  function voList(pg, nd) {
    let l = [];
    if (pg && pg.vo) l = Array.isArray(pg.vo) ? pg.vo.slice() : [pg.vo];
    else if (nd && nd.vo) l = [nd.vo];
    return l.map(voUrl);
  }
  function playVoice(pg, nd) {
    voice.pause();
    voice.removeAttribute("src");
    curVo = "";
    voQ = [];
    if (!voiceOn) return;
    voQ = voList(pg, nd);                 // страница → узел (совместимость)
    if (!voQ.length) return;
    curVo = voQ.join("|");
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
    if (INSTANT) { textEl.textContent = s; ty.i = s.length; typing = null; if (cb) cb(); return; }
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
    if (ty.i >= ty.full.length) { clearInterval(typing); typing = null; if (ty.cb) ty.cb(); }
  }
  function typingDone() { return !ty || ty.i >= ty.full.length; }
  function skipTyping() {
    if (ty && ty.i < ty.full.length) {
      clearInterval(typing); typing = null; textEl.textContent = ty.full; ty.i = ty.full.length;
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
  // затемнение → лого в темноте → осветление. Дольше обычной перебивки.
  // Иван 2026-10-21: «переход с проходной на кабинет должен быть чуть подольше,
  // затемнением, а потом осветлением; может даже лого показать».
  const TR = { dark: 520, logoIn: 420, hold: 620, logoOut: 300, light: 720 };
  let transT = [];
  function sceneTrans(cb) {
    if (!transEl) { cb(); return; }
    brkCb = cb;
    clearTimeout(brkT);
    transT.forEach(clearTimeout); transT = [];
    const at = (ms, fn) => transT.push(setTimeout(fn, ms));
    transEl.classList.add("on");                       // затемнение
    at(TR.dark, () => { const f = brkCb; brkCb = null; if (f) f(); });
    at(TR.dark + 80, () => transLogo && transLogo.classList.add("on"));
    at(TR.dark + 80 + TR.logoIn + TR.hold, () => transLogo && transLogo.classList.remove("on"));
    at(TR.dark + 80 + TR.logoIn + TR.hold + TR.logoOut,
       () => transEl.classList.remove("on"));          // осветление
  }
  // клик во время перебивки = сразу пройти её (иначе на стыке сцен теряются нажатия)
  function finishBreak() {
    if (!brkCb) return;
    const f = brkCb; brkCb = null;
    clearTimeout(brkT);
    transT.forEach(clearTimeout); transT = [];
    if (brk) brk.classList.remove("on");
    if (transEl) transEl.classList.remove("on");
    if (transLogo) transLogo.classList.remove("on");
    inBreak = false;
    f();
  }

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
    const s = SCENES[i], nd = NODES[s.n], pg = nd.pages[s.p];
    clearTimeout(autoTimer);
    showHud(true);
    hideScreens();
    chapter.textContent = D.episode;
    if (s.n !== curNode) {
      setBg(nd.bg);
      setMusic(nd.music || musicKey);
      curNode = s.n;
    }
    renderCast(pg.cast);
    applyCam(pg);
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
    if (!autoOn || paused || cinemaOpen) return;
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
    clearCam();
    paused = false; tyPaused = false;
    showHud(false);
    vlayer.hidden = true;
    title.classList.remove("show");
    endScr.classList.add("show");
    prevBtn.disabled = true;
    voice.pause();
  }
  // Возврат в меню = сброс к «первому запуску». Без сброса started/starting
  // кнопка «Начать» после прохождения молчала (start() упирался в started=true),
  // работал только «Тизер».
  function goMenu() {
    clearTimeout(autoTimer);
    closeCredits();
    clearTimeout(brkT); brkCb = null; inBreak = false;
    transT.forEach(clearTimeout); transT = [];
    if (brk) brk.classList.remove("on");
    if (transEl) transEl.classList.remove("on");
    if (transLogo) transLogo.classList.remove("on");
    playToken++;
    curNode = -1;
    clearCast();
    clearCam();
    paused = false; tyPaused = false;
    pos = 0;
    started = false; starting = false; pendingGo = null;
    const btn = $("start");
    if (btn) { btn.textContent = "Начать"; btn.title = ""; }
    plStat();                        // вернуть полосу загрузки в актуальное состояние
    try { znak.onended = null; znak.pause(); } catch (err) {}
    showHud(false); hideScreens();
    setBg("");
    music.pause(); voice.pause();
    musicKey = null;                 // иначе setMusic() на рестарте решит «уже играет»
    title.classList.add("show");
    autoOn = false; syncToggles();
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
    const done = () => { vlayer.hidden = true; try { znak.pause(); } catch (e) {} znak.onended = null; enterPos(0); };
    znak.onended = done;
    vskip.onclick = (e) => { e.stopPropagation(); done(); };
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
      if (music.src && musicOn) music.play().catch(() => {});
      enterZnak(NODES[1]);
    };
    if (PRELOAD_OFF) return go();
    // ждём только КРИТИЧНОЕ (значок + S1 + его голос), не весь эп1
    const crit = [];
    NODES.forEach((nd) => { if (nd.t === "znak") crit.push(nd.video); });
    const first = SCENES[0];
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
    if (autoOn && !paused && typingDone()) scheduleAuto();
  };
  $("t-pause").onclick = (e) => { e.stopPropagation(); togglePause(); };

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

  // ---------- титры (благодарности) ----------
  function crOpen() { return creditsEl.classList.contains("show"); }
  function renderCredits() {
    if (!crList || crList.dataset.done === "1") return;
    (D.credits || []).forEach(function (g) {
      const blk = document.createElement("div"); blk.className = "crgrp";
      const h = document.createElement("p"); h.className = "crh"; h.textContent = g.h || "";
      blk.appendChild(h);
      (g.rows || []).forEach(function (r) {
        const p = document.createElement("p"); p.className = "crrow";
        const cut = r.indexOf("|");
        if (cut > 0) {                       // «роль|исполнитель» → две колонки
          const a = document.createElement("span"); a.className = "crrole"; a.textContent = r.slice(0, cut).trim();
          const b = document.createElement("span"); b.className = "crname"; b.textContent = r.slice(cut + 1).trim();
          p.appendChild(a); p.appendChild(b);
        } else {
          p.textContent = r;
        }
        blk.appendChild(p);
      });
      (g.notes || []).forEach(function (n) {
        const q = document.createElement("p"); q.className = "crnote"; q.textContent = n;
        blk.appendChild(q);
      });
      crList.appendChild(blk);
    });
    crList.dataset.done = "1";
  }
  function openCredits() {
    renderCredits();
    creditsEl.classList.add("show");
    creditsEl.setAttribute("aria-hidden", "false");
    if (crList) crList.parentElement.scrollTop = 0;
  }
  function closeCredits() {
    creditsEl.classList.remove("show");
    creditsEl.setAttribute("aria-hidden", "true");
  }

  // ---------- ввод ----------
  $("start").onclick = (e) => { e.stopPropagation(); start(); };
  $("teaser").onclick = (e) => { e.stopPropagation(); playCinema(AVM); };
  $("e-menu").onclick = (e) => { e.stopPropagation(); goMenu(); };
  $("e-credits").onclick = (e) => { e.stopPropagation(); openCredits(); };
  $("cr-back").onclick = (e) => { e.stopPropagation(); closeCredits(); };
  $("e-teaser").onclick = (e) => { e.stopPropagation(); playCinema(AVM); };
  prevBtn.onclick = (e) => { e.stopPropagation(); prev(); };
  nextBtn.onclick = (e) => { e.stopPropagation(); next(); };

  document.getElementById("stage").addEventListener("click", () => {
    if (cinemaOpen || !vlayer.hidden || crOpen()) return;
    if (title.classList.contains("show") || endScr.classList.contains("show")) return;
    next();
  });
  addEventListener("keydown", (e) => {
    if (crOpen()) {                      // титры: листаются колесом/стрелками сами
      if (e.key === "Escape" || e.key === "Enter") { e.preventDefault(); closeCredits(); }
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
    if (cinemaOpen || crOpen() || title.classList.contains("show") || endScr.classList.contains("show")) return;
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
    if (cinemaOpen || !vlayer.hidden) return;
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
  // Значок перехода берётся с версией (?v=N): иначе Pages отдаёт старую картинку
  // из кеша и форма (круг/пятиугольник) не меняется после пересборки.
  if (transLogo) transLogo.src = "img/trans_logo.png" + (D.voVer ? "?v=" + D.voVer : "");
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
                   get typing() { return !!typing; } };
  if (SHOT) {                      // режим скриншота: сразу к нужному узлу
    started = true;
    const ni = parseInt(qp.get("node"), 10);
    const nd = NODES[ni];
    if (nd && nd.t === "scene") {
      const base = scriptStart[ni] || 0;
      enterPos(base + parseInt(qp.get("page") || "0", 10));
    } else if (nd && nd.t === "znak") { enterZnak(nd); }
    else if (nd && nd.t === "title") { enterTitle(); }
    else { enterEnd(); }
    if (qp.get("credits") === "1") openCredits();   // ?node=99&credits=1 — снимок титров
  }
})();
