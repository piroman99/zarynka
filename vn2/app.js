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
  const AUTO_BASE = 450, AUTO_PER_CHAR = 20, AUTO_GAP = 500;   // ~1.1–2.4 с на страницу

  const NODES = D.nodes;
  // плоский список страниц всех сцен → единая навигация вперёд/назад
  const SCENES = [];
  NODES.forEach((nd, ni) => {
    if (nd.t === "scene") nd.pages.forEach((_, pi) => SCENES.push({ n: ni, p: pi }));
  });
  const scriptStart = {};
  SCENES.forEach((s, i) => { if (!(s.n in scriptStart)) scriptStart[s.n] = i; });
  let pos = 0;

  // ---------- фон / спрайт ----------
  function setBg(url) {
    if (url === curBg) return;
    curBg = url;
    other.style.backgroundImage = url ? `url("${url}")` : "none";
    other.classList.add("on");
    if (INSTANT) { other.style.transition = "none"; other.style.opacity = 1; }
    bgActive.classList.remove("on");
    if (INSTANT) bgActive.style.opacity = 0;
    [bgActive, other] = [other, bgActive];
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
  function setMusic(key) {
    if (key === musicKey) return;
    musicKey = key;
    const src = D.music[key];
    if (!src) return;
    music.src = src;
    if (musicOn && started) music.play().catch(() => {});
  }

  // ---------- голос (постранично) ----------
  function playVoice(pg, nd) {
    voice.pause();
    voice.removeAttribute("src");
    curVo = "";
    if (!voiceOn) return;
    const src = (pg && pg.vo) || (nd && nd.vo);   // страница → узел (совместимость)
    if (!src) return;
    curVo = src;
    voice.src = src;
    voice.volume = 1.0;
    voice.play().catch(() => {});
  }

  // ---------- печать ----------
  function typeText(s, cb) {
    clearInterval(typing);
    ty = { full: s, i: 0, cb: cb };
    tyPaused = false;
    textEl.textContent = "";
    if (INSTANT) { textEl.textContent = s; ty.i = s.length; typing = null; if (cb) cb(); return; }
    typing = setInterval(typeTick, 18);
  }
  function typeTick() {
    if (tyPaused || !ty) return;
    textEl.textContent += ty.full[ty.i++];
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

  function enterPos(i) {
    if (i < 0) i = 0;
    if (i > SCENES.length - 1) return enterEnd();
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
    autoTimer = setTimeout(() => { if (t === playToken && autoOn) next(); }, delay);
  }

  // ---------- навигация ----------
  function next() {
    clearTimeout(autoTimer);
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
    paused = false; tyPaused = false;
    showHud(false);
    vlayer.hidden = true;
    title.classList.remove("show");
    endScr.classList.add("show");
    prevBtn.disabled = true;
    voice.pause();
  }
  function goMenu() {
    clearTimeout(autoTimer);
    playToken++;
    curNode = -1;
    clearCast();
    paused = false; tyPaused = false;
    showHud(false); hideScreens();
    setBg("");
    music.pause(); voice.pause();
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
    znak.src = nd.video;
    znak.currentTime = 0;
    znak.play().catch(() => {});
    const done = () => { vlayer.hidden = true; try { znak.pause(); } catch (e) {} znak.onended = null; enterPos(0); };
    znak.onended = done;
    vskip.onclick = (e) => { e.stopPropagation(); done(); };
  }

  function start() {
    started = true;
    hideScreens();
    if (music.src && musicOn) music.play().catch(() => {});
    enterZnak(NODES[1]);
  }

  // ---------- кинозал ----------
  function playCinema(src) {
    clearTimeout(autoTimer);
    cinemaOpen = true;
    avm.src = src; cinema.hidden = false;
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
    if (!musicOn) music.pause(); else if (started) music.play().catch(() => {});
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
    syncToggles();
  }

  // ---------- ввод ----------
  $("start").onclick = (e) => { e.stopPropagation(); start(); };
  $("teaser").onclick = (e) => { e.stopPropagation(); playCinema(AVM); };
  $("e-menu").onclick = (e) => { e.stopPropagation(); goMenu(); };
  $("e-teaser").onclick = (e) => { e.stopPropagation(); playCinema(AVM); };
  prevBtn.onclick = (e) => { e.stopPropagation(); prev(); };
  nextBtn.onclick = (e) => { e.stopPropagation(); next(); };

  document.getElementById("stage").addEventListener("click", () => {
    if (cinemaOpen || !vlayer.hidden) return;
    if (title.classList.contains("show") || endScr.classList.contains("show")) return;
    next();
  });
  addEventListener("keydown", (e) => {
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

  // свайп (тач)
  let sx = 0, sy = 0, sw = false;
  const stage = document.getElementById("stage");
  stage.addEventListener("touchstart", (e) => {
    if (e.touches.length !== 1) return; sx = e.touches[0].clientX; sy = e.touches[0].clientY; sw = true;
  }, { passive: true });
  stage.addEventListener("touchend", (e) => {
    if (!sw) return; sw = false;
    const dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
    if (cinemaOpen || title.classList.contains("show") || endScr.classList.contains("show")) return;
    if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy)) { dx < 0 ? next() : prev(); }
  }, { passive: true });

  // ---------- init ----------
  if (INSTANT) stage.classList.add("nofx");
  $("tt").textContent = D.title;
  $("tep").textContent = D.episode;
  $("byline").textContent = D.byline;
  $("e-byline").textContent = D.byline;
  // голос дочитал страницу → не ждём полный расчётный таймер
  voice.addEventListener("ended", () => {
    if (!autoOn || cinemaOpen) return;
    const s = SCENES[pos]; if (!s) return;
    const nd = NODES[s.n], pg = nd.pages[s.p];
    if (curVo && ((pg && pg.vo) || nd.vo) === curVo) scheduleAuto();
  });
  syncToggles();
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
  }
})();
