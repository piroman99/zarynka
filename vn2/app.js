// Зарянка — VN-эп1 «Пролог + Приёмная». Движок без зависимостей.
// Тумблеры: текст (подстрочник) ⇄ голос закадра ⇄ музыка — независимы.
(function () {
  const D = window.VN;
  const $ = (id) => document.getElementById(id);
  const bgA = $("bg-a"), bgB = $("bg-b"), sprite = $("sprite");
  const box = $("box"), nameEl = $("name"), textEl = $("text"), chapter = $("chapter");
  const hud = $("hud"), title = $("title"), vlayer = $("vlayer"), znak = $("znak"), vskip = $("vskip");
  const music = $("music"), voice = $("voice");
  const cinema = $("cinema"), avm = $("avm"), skip = $("skip");
  const AVM = "../out/avm_v3_epic.mp4";

  const qp = new URLSearchParams(location.search);
  const INSTANT = qp.get("instant") === "1";     // не печатать по буквам (для скриншотов)
  const SHOT = qp.has("node");

  let nodeIdx = 0, pageIdx = 0, curBg = "", curSprite = "~";
  let bgActive = bgA, other = bgB, typing = null;
  let musicKey = "", cinemaOpen = false, started = false;
  let textOn = qp.get("text") !== "0";
  let voiceOn = qp.get("voice") !== "0";
  let musicOn = qp.get("music") !== "0";

  const NODES = D.nodes;

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
    if (!voiceOn || !node.vo) return;
    voice.src = node.vo;
    voice.volume = 1.0;
    voice.play().catch(() => {});
  }

  // ---------- печать ----------
  function typeText(s) {
    clearInterval(typing);
    if (INSTANT) { textEl.textContent = s; return; }
    textEl.textContent = "";
    let i = 0;
    typing = setInterval(() => {
      textEl.textContent += s[i++];
      if (i >= s.length) clearInterval(typing);
    }, 18);
  }

  // ---------- рендер узлов ----------
  function showHud(on) { hud.style.opacity = on ? "" : 0; hud.classList.toggle("on", on); }

  function enterNode(i) {
    const nd = NODES[i];
    if (!nd) return finish();
    if (nd.t === "title") return enterTitle();
    if (nd.t === "znak") return enterZnak(nd);
    // scene
    showHud(true);
    title.classList.remove("show");
    vlayer.hidden = true;
    setBg(nd.bg);
    setMusic(nd.music || musicKey);
    chapter.textContent = D.episode;
    playVoice(nd);
    pageIdx = 0;
    renderPage();
  }

  function renderPage() {
    const nd = NODES[nodeIdx];
    const pg = nd.pages[pageIdx];
    if (!pg) { nodeIdx++; return enterNode(nodeIdx); }
    // спрайт: у страницы есть говорящий → его фигура; иначе СОХРАНЯЕМ текущего
    // (иначе фигура мигала бы на вставках авторского текста)
    if (pg.who) setSprite(spriteFor(pg.who));
    if (pg.name) { nameEl.style.visibility = "visible"; nameEl.textContent = pg.name; }
    else nameEl.style.visibility = "hidden";
    suggestNext();
    typeText(pg.tx);
  }

  function spriteFor(who) {
    if (who === "Сергей") return "img/char/sergey.png";
    if (who === "Екатерина") return "img/char/kate.png";
    return null;
  }

  function suggestNext() {
    // держим текущего персонажа если у страницы нет who (нарратив по центру)
  }

  // ---------- навигация ----------
  function next() {
    if (NODES[nodeIdx].t === "znak") { vskip.click(); return; }
    if (typing && textEl.textContent.length < (NODES[nodeIdx].pages[pageIdx].tx || "").length) {
      clearInterval(typing); textEl.textContent = NODES[nodeIdx].pages[pageIdx].tx; return;
    }
    const nd = NODES[nodeIdx];
    if (pageIdx + 1 < nd.pages.length) { pageIdx++; renderPage(); }
    else { nodeIdx++; enterNode(nodeIdx); }
  }

  function finish() {
    showHud(false);
    title.classList.remove("show");
    vlayer.hidden = true;
    // конец эп1 → тизер
    setTimeout(() => { if (!cinemaOpen) playCinema(AVM); }, 500);
  }

  // ---------- титул / значок ----------
  function enterTitle() {
    showHud(false);
    vlayer.hidden = true;
    music.pause();
    title.classList.add("show");
  }
  function enterZnak(nd) {
    showHud(false);
    title.classList.remove("show");
    setMusic("prolog");
    vlayer.hidden = false;
    znak.src = nd.video;
    znak.play().catch(() => {});
    const done = () => { vlayer.hidden = true; znak.pause(); nodeIdx++; enterNode(nodeIdx); };
    znak.onended = done;
    vskip.onclick = (e) => { e.stopPropagation(); done(); };
  }

  function start() {
    started = true;
    nodeIdx = qp.has("node") ? parseInt(qp.get("node"), 10) : 1;
    if (musicOn && music.src) music.play().catch(() => {});
    enterNode(nodeIdx);
  }

  // ---------- кинозал ----------
  function playCinema(src) {
    cinemaOpen = true;
    avm.src = src; cinema.hidden = false;
    requestAnimationFrame(() => cinema.classList.add("on"));
    music.pause();
    const done = () => {
      cinemaOpen = false; cinema.classList.remove("on");
      avm.pause(); avm.removeAttribute("src"); avm.load();
      setTimeout(() => { cinema.hidden = true; }, 400);
      if (started && musicOn) music.play().catch(() => {});
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
    document.getElementById("stage").classList.toggle("notext", !textOn);
  }
  $("t-text").onclick = (e) => { e.stopPropagation(); textOn = !textOn; syncToggles(); };
  $("t-voice").onclick = (e) => {
    e.stopPropagation(); voiceOn = !voiceOn; syncToggles();
    if (!voiceOn) voice.pause(); else { const nd = NODES[nodeIdx]; if (nd.vo) playVoice(nd); }
  };
  $("t-music").onclick = (e) => {
    e.stopPropagation(); musicOn = !musicOn; syncToggles();
    if (!musicOn) music.pause(); else if (started) music.play().catch(() => {});
  };

  // ---------- ввод ----------
  $("start").onclick = (e) => { e.stopPropagation(); start(); };
  $("teaser").onclick = (e) => { e.stopPropagation(); playCinema(AVM); };
  document.getElementById("stage").addEventListener("click", () => {
    if (cinemaOpen) return;
    if (title.classList.contains("show")) return;
    next();
  });
  addEventListener("keydown", (e) => {
    if (e.key === "Escape" && cinemaOpen) { skip.click(); return; }
    if (cinemaOpen) return;
    if ([" ", "Enter", "ArrowRight"].includes(e.key)) {
      e.preventDefault();
      if (title.classList.contains("show")) return start();
      next();
    }
  });

  // ---------- init ----------
  if (INSTANT) document.getElementById("stage").classList.add("nofx");
  $("tt").textContent = D.title;
  $("tep").textContent = D.episode;
  $("byline").textContent = D.byline;
  syncToggles();
  if (SHOT) {                      // режим скриншота: сразу к нужному узлу
    started = true;
    nodeIdx = parseInt(qp.get("node"), 10);
    if (qp.has("page")) pageIdx = parseInt(qp.get("page"), 10);
    const nd = NODES[nodeIdx];
    if (nd && nd.t === "scene") { enterNode(nodeIdx); pageIdx = parseInt(qp.get("page") || "0", 10); renderPage(); }
    else enterNode(nodeIdx);
  }
})();
