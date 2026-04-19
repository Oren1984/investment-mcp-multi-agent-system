/* ============================================================
   Investment MCP Multi-Agent System — Portfolio Site JS
   ============================================================ */

// ── Hero canvas — flowing market-activity particles ───────────────────────────
(function initHeroCanvas() {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  let particles = [];
  let W, H;

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }

  function spawnParticle() {
    return {
      x: Math.random() * W,
      y: H + 10,
      vx: (Math.random() - 0.5) * 0.6,
      vy: -(Math.random() * 0.8 + 0.3),
      size: Math.random() * 1.5 + 0.5,
      alpha: Math.random() * 0.6 + 0.2,
      color: Math.random() < 0.6 ? "#3b82f6" : Math.random() < 0.5 ? "#06b6d4" : "#10b981",
    };
  }

  function tick() {
    ctx.clearRect(0, 0, W, H);
    // Spawn
    if (particles.length < 120) particles.push(spawnParticle());

    particles = particles.filter(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.alpha -= 0.0015;
      if (p.alpha <= 0 || p.y < -10) return false;
      ctx.globalAlpha = p.alpha;
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
      return true;
    });

    ctx.globalAlpha = 1;
    requestAnimationFrame(tick);
  }

  resize();
  window.addEventListener("resize", resize);
  tick();
})();


// ── Animated counter ─────────────────────────────────────────────────────────
function animateCounter(el) {
  const target = parseInt(el.dataset.target, 10);
  const suffix = el.dataset.suffix || "";
  const duration = 1400;
  const start = performance.now();

  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(eased * target) + suffix;
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target + suffix;
  }
  requestAnimationFrame(step);
}

// ── Scroll-triggered animations ───────────────────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;

    const el = entry.target;

    // Counter elements
    if (el.classList.contains("counter")) {
      animateCounter(el);
      observer.unobserve(el);
    }

    // Progress bars
    if (el.classList.contains("test-bar-fill")) {
      el.style.width = el.dataset.width;
      observer.unobserve(el);
    }

    // Fade-in cards
    if (el.classList.contains("fade-in")) {
      el.style.opacity = "1";
      el.style.transform = "translateY(0)";
      observer.unobserve(el);
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll(".counter, .test-bar-fill, .fade-in").forEach(el => {
  if (el.classList.contains("fade-in")) {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    el.style.transition = "opacity .5s ease, transform .5s ease";
  }
  observer.observe(el);
});


// ── Tab switcher ─────────────────────────────────────────────────────────────
document.querySelectorAll(".tabs").forEach(tabGroup => {
  const buttons = tabGroup.querySelectorAll(".tab-btn");
  const parent  = tabGroup.closest("[data-tabs]") || tabGroup.parentElement;

  buttons.forEach((btn, i) => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      parent.querySelectorAll(".tab-content").forEach((c, j) => {
        c.classList.toggle("active", j === i);
      });
    });
  });
});


// ── Simulated demo panel ──────────────────────────────────────────────────────
const DEMO_STEPS = [
  { delay: 0,    cls: "info",  msg: msg => `[API] POST /api/v1/analyze  {"ticker":"${msg}","period":"1y"}` },
  { delay: 400,  cls: "",      msg: () => '[API] ← 202 Accepted  {"run_id":"a4f2c1...","status":"PENDING"}' },
  { delay: 900,  cls: "agent", msg: () => "[Crew] Research Agent starting — fetching price history & financials" },
  { delay: 2200, cls: "agent", msg: () => "[Crew] Technical Analyst — calculating RSI=62, MACD=bullish, SMA200 trend: UP" },
  { delay: 3600, cls: "agent", msg: () => "[Crew] Sector Analyst — XLK benchmark: stock +3.2% vs sector YTD" },
  { delay: 5000, cls: "agent", msg: () => "[Crew] Risk Analyst — β=1.24, Vol=24.5%, Sharpe=0.87, MaxDD=-18.3%" },
  { delay: 6400, cls: "agent", msg: () => "[Crew] Report Writer — synthesising 4 agent outputs → generating report" },
  { delay: 8200, cls: "info",  msg: () => "[MCP] save_report called — validating sections ✓ all 6 present" },
  { delay: 8800, cls: "ok",    msg: () => "[DB] Report persisted. status → COMPLETED" },
  { delay: 9200, cls: "done",  msg: () => "✅ Analysis complete. GET /api/v1/analyze/a4f2c1.../report" },
];

const MOCK_METRICS = {
  AAPL: { rsi: "62", sharpe: "0.87", vol: "24.5%", beta: "1.24", rec: "HOLD", recClass: "metric-neu" },
  MSFT: { rsi: "58", sharpe: "1.10", vol: "22.1%", beta: "1.18", rec: "BUY",  recClass: "metric-up"  },
  NVDA: { rsi: "71", sharpe: "1.42", vol: "44.8%", beta: "1.88", rec: "BUY",  recClass: "metric-up"  },
  JPM:  { rsi: "54", sharpe: "0.74", vol: "19.3%", beta: "1.05", rec: "HOLD", recClass: "metric-neu" },
  XOM:  { rsi: "49", sharpe: "0.62", vol: "31.2%", beta: "0.95", rec: "HOLD", recClass: "metric-neu" },
};

let demoRunning = false;
let demoTimers  = [];

function clearDemo() {
  demoTimers.forEach(clearTimeout);
  demoTimers = [];
  demoRunning = false;
}

function runDemo() {
  const tickerInput  = document.getElementById("demo-ticker");
  const runBtn       = document.getElementById("demo-run");
  const logPanel     = document.getElementById("demo-log");
  const statusRow    = document.getElementById("demo-status");
  const metricsRow   = document.getElementById("demo-metrics");
  if (!tickerInput || !runBtn || !logPanel) return;

  if (demoRunning) { clearDemo(); }
  demoRunning = true;

  const ticker = tickerInput.value.trim().toUpperCase() || "AAPL";
  const metrics = MOCK_METRICS[ticker] || MOCK_METRICS["AAPL"];

  logPanel.innerHTML = "";
  metricsRow.innerHTML = "";
  statusRow.innerHTML = `<span class="status-chip chip-running"><span class="pulse"></span> RUNNING — ${ticker}</span>`;
  runBtn.disabled = true;
  runBtn.textContent = "Running…";

  function appendLog(cls, text) {
    const ts = new Date().toISOString().slice(11, 23);
    const line = document.createElement("div");
    line.className = `log-line ${cls}`;
    line.textContent = `${ts}  ${text}`;
    logPanel.appendChild(line);
    logPanel.scrollTop = logPanel.scrollHeight;
  }

  DEMO_STEPS.forEach(step => {
    const t = setTimeout(() => {
      appendLog(step.cls, step.msg(ticker));
    }, step.delay);
    demoTimers.push(t);
  });

  // Done
  const finishT = setTimeout(() => {
    statusRow.innerHTML = `<span class="status-chip chip-done"><span class="pulse"></span> COMPLETED — ${ticker}</span>`;

    metricsRow.innerHTML = `
      <div class="metric-card">
        <div class="metric-value metric-neu">${metrics.rsi}</div>
        <div class="metric-label">RSI 14-day</div>
      </div>
      <div class="metric-card">
        <div class="metric-value metric-up">${metrics.sharpe}</div>
        <div class="metric-label">Sharpe Ratio</div>
      </div>
      <div class="metric-card">
        <div class="metric-value metric-down">${metrics.vol}</div>
        <div class="metric-label">Annualised Vol</div>
      </div>
      <div class="metric-card">
        <div class="metric-value metric-neu">${metrics.beta}</div>
        <div class="metric-label">Beta vs SPY</div>
      </div>
      <div class="metric-card">
        <div class="metric-value ${metrics.recClass}">${metrics.rec}</div>
        <div class="metric-label">Recommendation</div>
      </div>
    `;

    runBtn.disabled = false;
    runBtn.textContent = "▶ Run Again";
    demoRunning = false;
  }, 10000);
  demoTimers.push(finishT);
}

const runBtn = document.getElementById("demo-run");
if (runBtn) runBtn.addEventListener("click", runDemo);


// ── Smooth active nav highlight ───────────────────────────────────────────────
const sections = document.querySelectorAll("section[id]");
const navLinks  = document.querySelectorAll(".nav-links a");

window.addEventListener("scroll", () => {
  let current = "";
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 80) current = s.id;
  });
  navLinks.forEach(a => {
    a.style.color = a.getAttribute("href") === `#${current}` ? "var(--text)" : "";
  });
}, { passive: true });
