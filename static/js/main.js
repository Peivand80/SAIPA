/* اسکریپت‌های سمت کاربر — بدون وابستگی به کتابخانه خارجی */
(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const csrf = () => ($('meta[name="csrf-token"]') || {}).content || "";
  const faDigits = (n) => String(n).replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[d]);
  const toLatin = (s) => String(s).replace(/[۰-۹]/g, (d) => "۰۱۲۳۴۵۶۷۸۹".indexOf(d)).replace(/[٠-٩]/g, (d) => "٠١٢٣٤٥٦٧٨٩".indexOf(d));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const root = document.documentElement;

  // ---------- حالت روشن / تیره ----------
  const themeMeta = $('meta[name="theme-color"]');
  const applyTheme = (t) => {
    root.setAttribute("data-theme", t);
    if (themeMeta) themeMeta.content = t === "light" ? "#F4F2EF" : "#131416";
  };
  applyTheme(root.getAttribute("data-theme") || "dark");
  $$("[data-theme-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      applyTheme(next);
      try { localStorage.setItem("saipa-theme", next); } catch (e) { /* حالت خصوصی مرورگر */ }
    });
  });

  // ---------- منوی موبایل و جستجو ----------
  $$("[data-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.toggle === "nav" ? $("#main-nav") : $("#search-panel");
      const open = target.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
      if (btn.dataset.toggle === "nav") document.body.style.overflow = open ? "hidden" : "";
      if (btn.dataset.toggle === "search" && open) $("#site-search").focus();
    });
  });

  // ---------- هدر، نوار پیشرفت و دکمه بازگشت به بالا ----------
  const header = $("[data-header]");
  const bar = $(".scroll-progress span");
  const toTop = $("[data-to-top]");
  let ticking = false;
  const onScroll = () => {
    const y = window.scrollY;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    if (header) header.classList.toggle("is-scrolled", y > 10);
    if (bar) bar.style.transform = `scaleX(${max > 0 ? Math.min(y / max, 1) : 0})`;
    if (toTop) toTop.classList.toggle("show", y > 600);
    ticking = false;
  };
  window.addEventListener("scroll", () => { if (!ticking) { requestAnimationFrame(onScroll); ticking = true; } }, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" }));

  // ---------- ظاهر شدن بخش‌ها هنگام اسکرول ----------
  const revealEls = $$("[data-reveal]");
  if ("IntersectionObserver" in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("in"));
  }

  // ---------- شمارنده آمار ----------
  const counters = $$("[data-count]");
  const runCounter = (el) => {
    const raw = toLatin(el.dataset.count);
    const m = raw.match(/[\d,٬]+/);
    if (!m) return;
    const target = parseInt(m[0].replace(/[,٬]/g, ""), 10);
    const [pre, post] = [raw.slice(0, m.index), raw.slice(m.index + m[0].length)];
    const sep = /[,٬]/.test(m[0]);
    const start = performance.now(), dur = 1600;
    const step = (now) => {
      const p = Math.min((now - start) / dur, 1);
      const val = Math.round(target * (1 - Math.pow(1 - p, 3)));
      const txt = sep ? val.toLocaleString("en-US").replace(/,/g, "٬") : String(val);
      el.textContent = faDigits(pre + txt + post);
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  if (counters.length && "IntersectionObserver" in window && !reduceMotion) {
    const co = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { runCounter(e.target); co.unobserve(e.target); } });
    }, { threshold: 0.6 });
    counters.forEach((el) => co.observe(el));
  }

  // ---------- ویدیوها: پخش خودکار بی‌صدا فقط وقتی در دید هستند ----------
  const vids = $$("video[data-autoplay]");
  vids.forEach((v) => { v.muted = true; v.setAttribute("muted", ""); });
  const tryPlay = (v) => { const p = v.play(); if (p && p.catch) p.catch(() => {}); };
  if ("IntersectionObserver" in window) {
    const vo = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        const v = e.target;
        if (e.isIntersecting) {
          if (v.preload === "none") v.preload = "auto";
          if (!reduceMotion) tryPlay(v);
        } else {
          v.pause();
        }
      });
    }, { threshold: 0.35 });
    vids.forEach((v) => vo.observe(v));
  } else if (!reduceMotion) {
    vids.forEach(tryPlay);
  }

  // ---------- چت‌بات ----------
  const bot = $("[data-chatbot]");
  if (bot) {
    const panel = $(".chat-panel", bot);
    const body = $("[data-chat-body]", bot);
    const form = $("[data-chat-form]", bot);
    const input = $("input", form);
    const chips = $("[data-chat-chips]", bot);
    const toggleBtn = $("[data-chat-toggle]", bot);
    let busy = false;

    const setOpen = (open) => {
      bot.classList.toggle("open", open);
      panel.setAttribute("aria-hidden", !open);
      toggleBtn.setAttribute("aria-expanded", open);
      if (open) { bot.classList.add("hint-off"); setTimeout(() => input.focus(), 250); }
    };
    toggleBtn.addEventListener("click", () => setOpen(!bot.classList.contains("open")));
    $("[data-chat-close]", bot).addEventListener("click", () => setOpen(false));
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && bot.classList.contains("open")) setOpen(false); });

    const scrollDown = () => { body.scrollTop = body.scrollHeight; };
    const addMsg = (text, who, links) => {
      const el = document.createElement("div");
      el.className = `msg msg-${who}`;
      el.textContent = text;
      if (links && links.length) {
        const wrap = document.createElement("div");
        wrap.className = "msg-links";
        links.forEach((l) => {
          const a = document.createElement("a");
          a.href = l.url; a.textContent = l.label;
          if (/^https?:/.test(l.url)) { a.target = "_blank"; a.rel = "noopener"; }
          wrap.appendChild(a);
        });
        el.appendChild(wrap);
      }
      body.appendChild(el);
      scrollDown();
    };
    const setChips = (items) => {
      if (!items || !items.length) return;
      chips.innerHTML = "";
      items.forEach((t) => { const b = document.createElement("button"); b.type = "button"; b.textContent = t; chips.appendChild(b); });
    };

    const ask = async (text) => {
      text = text.trim();
      if (!text || busy) return;
      busy = true;
      addMsg(text, "user");
      input.value = "";
      const typing = document.createElement("div");
      typing.className = "typing"; typing.innerHTML = "<span></span><span></span><span></span>";
      body.appendChild(typing); scrollDown();
      try {
        const res = await fetch(bot.dataset.url, {
          method: "POST",
          headers: { "X-CSRFToken": csrf(), "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ message: text }),
          credentials: "same-origin",
        });
        const data = await res.json();
        await new Promise((r) => setTimeout(r, 450));
        typing.remove();
        addMsg(data.answer || "پاسخی پیدا نشد.", "bot", data.links);
        setChips(data.suggestions);
      } catch (e) {
        typing.remove();
        addMsg("ارتباط برقرار نشد. لطفاً دوباره تلاش کنید.", "bot");
      } finally {
        busy = false;
      }
    };
    form.addEventListener("submit", (e) => { e.preventDefault(); ask(input.value); });
    chips.addEventListener("click", (e) => { if (e.target.tagName === "BUTTON") ask(e.target.textContent); });
  }

  // ---------- بستن پیام‌ها ----------
  $$("[data-dismiss]").forEach((btn) => btn.addEventListener("click", () => btn.closest(".alert").remove()));

  // ---------- لایک ----------
  $$("[data-like]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      try {
        const body = new URLSearchParams({ target: btn.dataset.target, id: btn.dataset.id });
        const res = await fetch("/interactions/like/", {
          method: "POST",
          headers: { "X-CSRFToken": csrf(), "Content-Type": "application/x-www-form-urlencoded" },
          body,
          credentials: "same-origin",
        });
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();
        btn.classList.toggle("liked", data.liked);
        btn.setAttribute("aria-pressed", data.liked);
        $("[data-like-count]", btn).textContent = faDigits(data.count);
        btn.classList.remove("pulse"); void btn.offsetWidth; btn.classList.add("pulse");
      } catch (e) {
        console.error("like failed", e);
      } finally {
        btn.disabled = false;
      }
    });
  });

  // ---------- گالری تصاویر خودرو ----------
  const mainImg = $("#gallery-main");
  $$("[data-gallery]").forEach((thumb) => {
    thumb.addEventListener("click", () => {
      mainImg.style.opacity = 0;
      setTimeout(() => { mainImg.src = thumb.dataset.gallery; mainImg.style.opacity = 1; }, 150);
      $$("[data-gallery]").forEach((t) => t.classList.toggle("active", t === thumb));
    });
  });

  // ---------- کپی لینک ----------
  $$("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        btn.title = "لینک کپی شد";
        btn.style.borderColor = "var(--brand)";
      } catch (e) { /* مرورگر اجازه نداد */ }
    });
  });

  // ---------- نوبت‌دهی: به‌روزرسانی ساعت‌های آزاد بر اساس روز ----------
  const booking = $("[data-booking]");
  if (booking) {
    const dateSel = $("select[name=date]", booking);
    const slotSel = $("select[name=slot]", booking);
    const hint = $("[data-slot-hint]", booking);

    const refresh = async () => {
      if (!dateSel.value) {
        $$("option", slotSel).forEach((o) => { if (o.value) o.disabled = true; });
        hint.textContent = "ابتدا روز مراجعه را انتخاب کنید.";
        return;
      }
      hint.textContent = "در حال بررسی ظرفیت…";
      try {
        const res = await fetch(`${booking.dataset.availabilityUrl}?date=${dateSel.value}`);
        const data = await res.json();
        const map = Object.fromEntries(data.slots.map((s) => [String(s.id), s]));
        let free = 0;
        $$("option", slotSel).forEach((o) => {
          if (!o.value) return;
          const s = map[o.value];
          const base = o.dataset.label || (o.dataset.label = o.textContent);
          if (!s) { o.disabled = true; o.textContent = base; return; }
          o.disabled = !s.available;
          o.textContent = s.available ? `${faDigits(base)} — ${faDigits(s.remaining)} ظرفیت خالی` : `${faDigits(base)} — تکمیل`;
          if (s.available) free++;
        });
        if (slotSel.selectedOptions[0] && slotSel.selectedOptions[0].disabled) slotSel.value = "";
        hint.textContent = free ? "" : "ظرفیت این روز تکمیل است. لطفاً روز دیگری انتخاب کنید.";
      } catch (e) {
        hint.textContent = "";
      }
    };
    dateSel.addEventListener("change", refresh);
    refresh();
  }
})();
