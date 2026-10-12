// Зарянка — VN-эп1 «Пролог + Приёмная». Движок без зависимостей.
// Тумблеры: текст (подстрочник) ⇄ голос закадра ⇄ музыка — независимы.
// Навигация: → далее, ← назад, «Авто» — само листается; конец серии = экран, не авто-тизер.
(function () {
  const D = window.VN;
  const $ = (id) => document.getElementById(id);
  const bgA = $("bg-a"), bgB = $("bg-b"), sprite = $("sprite");
  const box = $("box"), nameEl = $("name"), textEl = $("text"), chapter = $("chapter");
  const hud = $("hud"), title = $("title"), vlayer = $("vlayer"), znak = $("znak"), vskip = $("vskip");
  const music = $("music"), voice = $("voice");
  const cinema = $("cinema"), avm = $("avm"), skip = $("skip");
  const endScr = $("end"), prevBtn = $("prev"), nextBtn = $("next");
  const AVM = "../out/avm_v3_epic.mp4";

  const qp = new URLSearchParams(location.search);
  const INSTANT = qp.get("instant") === "1";     // не печатать по буквам (для скриншотов)
  const SHOT = qp.has("node");

  let curBg = "", curSprite = "~";
  let bgActive = bgA, other = bgB, typing = null;
  let musicKey = "", cinemaOpen = false, started = false, curNode = -1;
  let textOn = qp.get("text") !== "0";
  let voiceOn = qp.get("voice") !== "0";
  let musicOn = qp.get("music") !== "0";
  let autoOn = qp.get("auto") === "1";

  let autoTimer = null, playToken = 0;
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

  function curNodeND() { const s = SCENES[pos]; return s ? NODES[s.n] : null; }

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
  function setSprite(url) {
    if (url === curSprite) return;
    curSprite = url;
    if (!url) { sprite.classList.remove("on"); if (INSTANT) sprite.style.opacity = 0; return; }
    if (sprite.getAttribute("src") !== url) sprite.src = url;
    sprite.classList.add("on");
    if (INSTANT) { sprite.style.transition = "none"; sprite.style.opacity = 1; }
  }
  function spriteFor(who) {
    if (who === "Сергей") return "img/char/sergey.png";
    if (who === "Екатерина") return "img/char/kate.png";
    return null;
  }
  // спрайт на странице p = последний говорящий до этой страницы (устойчиво при листании назад)
  function spriteAt(nd, p) {
    for (let k = p; k >= 0; k--) { if (nd.pages[k].who) return spriteFor(nd.pages[k].who); }
    return null;
  }

  // ---------- музыка ----------
  function setMusic(key) {
    if (key === musicKey) return;
    musicKey = key;
    const src = D.music[key];
    if (!src) return;
    music.src = src;
    if (musicOn && started) music.play().catch(() => {});
  }

  // ---------- голос ----------
  function playVoice(node) {
    voice.pause();
    voice.removeAttribute("src");
    if (!voiceOn || !node || !node.vo) return;
    voice.src = node.vo;
    voice.volume = 1.0;
    voice.play().catch(() => {});
  }

  // ---------- печать ----------
  function typeText(s, cb) {
    clearInterval(typing);
    if (INSTANT) { textEl.textContent = s; if (cb) cb(); return; }
    textEl.textContent = "";
    let i = 0;
    typing = setInterval(() => {
      textEl.textContent += s[i++];
      if (i >= s.length) { clearInterval(typing); typing = null; if (cb) cb(); }
    }, 18);
  }
  function typingDone() { return !typing; }

  // ---------- рендер ----------
  function showHud(on) { hud.style.opacity = on ? "" : 0; hud.classList.toggle("on", on); }
  function hideScreens() {
    title.classList.remove("show"); endScr.classList.remove("show"); vlayer.hidden = true;
  }

  function enterPos(i, noVoiceRestart) {
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
      if (!noVoiceRestart) playVoice(nd);
      setSprite(spriteAt(nd, s.p) || null);
      curNode = s.n;
    } else {
      const sp = spriteAt(nd, s.p);
      if (sp) setSprite(sp);
    }
    if (pg.name) { nameEl.style.visibility = "visible"; nameEl.textContent = pg.name; }
    else nameEl.style.visibility = "hidden";
    typeText(pg.tx, scheduleAuto);
    prevBtn.disabled = (pos === 0);
  }

  // ---------- авто-режим ----------
  function scheduleAuto() {
    clearTimeout(autoTimer);
    if (!autoOn || cinemaOpen) return;
    const s = SCENES[pos]; if (!s) return;
    const nd = NODES[s.n], pg = nd.pages[s.p];
    const t = playToken;
    let delay = AUTO_BASE + Math.min(1900, pg.tx.length * AUTO_PER_CHAR);
    if (voiceOn && nd.vo && !voice.paused && isFinite(voice.duration)) {
      const remain = Math.max(0, (voice.duration - voice.currentTime)) * 1000;
      delay = Math.max(delay, remain + AUTO_GAP);
    }
    autoTimer = setTimeout(() => { if (t === playToken && autoOn) next(); }, delay);
  }

  // ---------- навигация ----------
  function next() {
    clearTimeout(autoTimer);
    if (!vlayer.hidden) { vskip.click(); return; }   // идёт интро-значок → пропустить
    if (!typingDone()) {                      // сперва дописать страницу
      const s = SCENES[pos]; const nd = NODES[s.n], pg = nd.pages[s.p];
      clearInterval(typing); typing = null; textEl.textContent = pg.tx;
      if (autoOn) scheduleAuto();
      return;
    }
    enterPos(pos + 1);
  }
  function prev() {
    clearTimeout(autoTimer);
    if (cinemaOpen) return;
    if (!vlayer.hidden) return;
    if (pos > 0) enterPos(pos - 1, true);
  }

  function enterEnd() {
    clearTimeout(autoTimer);
    playToken++;
    curNode = -1; curSprite = "~";
    showHud(false);
    vlayer.hidden = true;
    title.classList.remove("show");
    endScr.classList.add("show");
    prevBtn.disabled = true;
  }
  function goMenu() {
    clearTimeout(autoTimer);
    playToken++;
    curNode = -1; curSprite = "~";
    showHud(false); hideScreens();
    sprite.classList.remove("on");
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
    $("t-auto").classList.toggle("on", autoOn);
    $("t-auto").classList.toggle("off", !autoOn);
    document.getElementById("stage").classList.toggle("notext", !textOn);
  }
  $("t-text").onclick = (e) => { e.stopPropagation(); textOn = !textOn; syncToggles(); };
  $("t-voice").onclick = (e) => {
    e.stopPropagation(); voiceOn = !voiceOn; syncToggles();
    if (!voiceOn) voice.pause(); else { const nd = curNodeND(); if (nd && nd.vo) playVoice(nd); }
    if (autoOn) scheduleAuto();
  };
  $("t-music").onclick = (e) => {
    e.stopPropagation(); musicOn = !musicOn; syncToggles();
    if (!musicOn) music.pause(); else if (started) music.play().catch(() => {});
  };
  $("t-auto").onclick = (e) => {
    e.stopPropagation(); autoOn = !autoOn; syncToggles();
    if (autoOn) { if (typingDone()) scheduleAuto(); } else clearTimeout(autoTimer);
  };

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
  syncToggles();
  if (SHOT) {                      // режим скриншота: сразу к нужному узлу
    started = true;
    const ni = parseInt(qp.get("node"), 10);
    const nd = NODES[ni];
    if (nd && nd.t === "scene") {
      const base = scriptStart[ni] || 0;
      enterPos(base + parseInt(qp.get("page") || "0", 10), true);
    } else if (nd && nd.t === "znak") { enterZnak(nd); }
    else if (nd && nd.t === "title") { enterTitle(); }
    else { enterEnd(); }
  }
})();
