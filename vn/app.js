// Зарянка — минимальный VN-движок (эпизод 1). Без зависимостей.
(function () {
  const D = window.ZARYANKA;
  const NAME = {
    "Сергей": "Лихнецкий Сергей",
    "Екатерина": "Екатерина Ивановна",
    "Лёша": "Лёша Савушкин",
  };
  const SPRITE = {
    "Сергей": "../assets/sprites/sergey.png",
    "Екатерина": "../assets/sprites/kate_overalls.png",
  };
  const KATE_SAD = "../assets/sprites/kate_sad.png";

  const $ = (id) => document.getElementById(id);
  const bgA = $("bg-a"), bgB = $("bg-b"), sprite = $("sprite");
  const box = $("box"), nameEl = $("name"), textEl = $("text"), chapter = $("chapter");
  const hud = $("hud"), title = $("title"), end = $("end");
  const bgm = $("bgm"), muteBtn = $("mute"), cinema = $("cinema"), avm = $("avm"), skip = $("skip");
  const AVM = "../out/avm_v3_epic.mp4";
  let bgmStarted = false, cinemaOpen = false;

  // плоский список шагов + метки начала сцен
  const steps = [];
  D.scenes.forEach((sc, si) => {
    sc.shots.forEach((sh, i) => steps.push({ sc, si, sh, first: i === 0 }));
  });

  let idx = 0, curBg = "", curSprite = null, bgActive = bgA, other = bgB, typing = null;

  function setBg(url) {
    if (url === curBg) return;
    curBg = url;
    other.style.backgroundImage = `url("${url}")`;
    other.classList.add("on");
    bgActive.classList.remove("on");
    [bgActive, other] = [other, bgActive];
  }

  function setSprite(url) {
    if (url === curSprite) return;
    curSprite = url;
    if (!url) { sprite.classList.remove("on"); return; }
    sprite.src = url;
    sprite.classList.add("on");
  }

  function typeText(s) {
    clearInterval(typing);
    textEl.textContent = "";
    let i = 0;
    typing = setInterval(() => {
      textEl.textContent += s[i++];
      if (i >= s.length) clearInterval(typing);
    }, 18);
  }

  function render() {
    const st = steps[idx];
    if (!st) return finish();
    const { sc, sh } = st;
    setBg(sh.bg);

    if (sh.who && SPRITE[sh.who]) setSprite(SPRITE[sh.who]);
    else if (!sh.who) {
      if (sc.id === "title") setSprite(null);
      // иначе оставляем текущего персонажа в кадре
    }
    if (sc.id === "kate" && /сникшая|потухшим взглядом/.test(sh.text)) setSprite(KATE_SAD);

    chapter.textContent = sc.title;
    if (sh.who) { nameEl.style.visibility = "visible"; nameEl.textContent = NAME[sh.who] || sh.who; }
    else nameEl.style.visibility = "hidden";

    typeText(sh.text);
  }

  function next() {
    if (typing && textEl.textContent.length < steps[idx].sh.text.length) {
      clearInterval(typing); textEl.textContent = steps[idx].sh.text; return; // досрочно дописать
    }
    idx++;
    if (idx >= steps.length) return finish();
    render();
  }

  function start() {
    idx = 0; curBg = ""; curSprite = "~"; setSprite(null);
    title.classList.remove("show"); end.classList.remove("show");
    hud.style.opacity = "";            // сбросить inline-стиль от finish()
    hud.classList.add("on"); startBgm(); render();
  }
  function finish() {
    hud.classList.remove("on");
    hud.style.opacity = 0;
    end.classList.add("show");
    setTimeout(() => { if (!cinemaOpen) playCinema(AVM); }, 650);   // тизер «дальше»
  }

  // --- звук и кинозал ---
  function startBgm() {
    if (bgmStarted) return;
    bgmStarted = true;
    bgm.volume = 0.5;
    bgm.play().catch(() => {});
  }
  function toggleMute(e) {
    e.stopPropagation();
    bgm.muted = !bgm.muted;
    muteBtn.textContent = bgm.muted ? "🔇" : "🔊";
  }
  function playCinema(src) {
    cinemaOpen = true;
    avm.src = src;
    cinema.hidden = false;
    requestAnimationFrame(() => cinema.classList.add("on"));
    bgm.pause();
    const done = () => {
      cinemaOpen = false;
      cinema.classList.remove("on");
      avm.pause(); avm.removeAttribute("src"); avm.load();
      setTimeout(() => { cinema.hidden = true; }, 400);
      if (bgmStarted && !bgm.muted) bgm.play().catch(() => {});
    };
    avm.onended = done;
    skip.onclick = (e) => { e.stopPropagation(); done(); };
    cinema.onclick = done;
    avm.play().catch((err) => { console.log("cinema:", err.message); });
  }

  $("start").onclick = (e) => { e.stopPropagation(); start(); };
  $("again").onclick = (e) => { e.stopPropagation(); start(); };
  $("teaser").onclick = (e) => { e.stopPropagation(); playCinema(AVM); };
  $("trailer").onclick = (e) => { e.stopPropagation(); playCinema(AVM); };
  muteBtn.onclick = toggleMute;
  document.getElementById("stage").addEventListener("click", (e) => {
    if (cinemaOpen) return;
    if (title.classList.contains("show") || end.classList.contains("show")) return;
    next();
  });
  addEventListener("keydown", (e) => {
    if (e.key === "Escape" && cinemaOpen) { skip.click(); return; }
    if (cinemaOpen) return;
    if ([" ", "Enter", "ArrowRight"].includes(e.key)) {
      e.preventDefault();
      if (title.classList.contains("show")) return start();
      if (end.classList.contains("show")) return start();
      next();
    }
  });

  $("byline").textContent = "по рассказу Александра «Котобус» Горбова";

  // PWA
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  }
})();
