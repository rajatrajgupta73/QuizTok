/* QuizTok cursor effects — ink-in-water fluid trail + soft spotlight glow.
   Shared by every prototype page; pure local JS, no dependencies. */
(function () {
  // ---- layers ----
  const glow = document.createElement("div");
  glow.id = "qt-glow";
  document.body.appendChild(glow);

  const cv = document.createElement("canvas");
  cv.id = "qt-ink";
  document.body.appendChild(cv);
  const ctx = cv.getContext("2d");
  function resize() { cv.width = innerWidth; cv.height = innerHeight; }
  resize();
  addEventListener("resize", resize);

  // ---- state ----
  const PALETTE = [[77,180,255],[0,136,206],[226,24,54],[255,194,51],[124,92,255],[0,201,167]];
  const drops = [];
  let tx = -600, ty = -600, x = tx, y = ty, lastSpawn = 0;

  document.addEventListener("mousemove", (e) => {
    tx = e.clientX; ty = e.clientY;
    glow.style.opacity = "1";
    const now = performance.now();
    if (now - lastSpawn < 18) return;               // spawn rate limit
    lastSpawn = now;
    const c = PALETTE[(Math.random() * PALETTE.length) | 0];
    drops.push({
      x: tx, y: ty,
      r: 5 + Math.random() * 9,                     // ink drop starts small…
      grow: 1.4 + Math.random() * 2.2,              // …and blooms outward
      a: 0.55,
      dx: (Math.random() - 0.5) * 1.4,              // slow drift
      dy: (Math.random() - 0.5) * 1.4 - 0.25,       // slight upward buoyancy
      swirl: Math.random() * 6.283, c,
    });
    if (drops.length > 130) drops.splice(0, drops.length - 130);
  });
  document.addEventListener("mouseleave", () => { glow.style.opacity = "0"; });

  // ---- paint loop ----
  (function loop() {
    x += (tx - x) * 0.16;                           // lerp = soft trailing glow
    y += (ty - y) * 0.16;
    glow.style.transform = `translate(${x - 230}px, ${y - 230}px)`;

    ctx.clearRect(0, 0, cv.width, cv.height);
    ctx.globalCompositeOperation = "lighter";       // additive = luminous fluid
    for (let i = drops.length - 1; i >= 0; i--) {
      const d = drops[i];
      d.r += d.grow; d.grow *= 0.985;               // diffusion slows over time
      d.a *= 0.955;                                 // ink fades as it spreads
      d.swirl += 0.05;
      d.x += d.dx + Math.cos(d.swirl) * 0.7;        // curling water currents
      d.y += d.dy + Math.sin(d.swirl * 0.8) * 0.55;
      if (d.a < 0.012) { drops.splice(i, 1); continue; }
      const g = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r);
      g.addColorStop(0, `rgba(${d.c[0]},${d.c[1]},${d.c[2]},${d.a})`);
      g.addColorStop(1, `rgba(${d.c[0]},${d.c[1]},${d.c[2]},0)`);
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, 6.283); ctx.fill();
    }
    requestAnimationFrame(loop);
  })();
})();
