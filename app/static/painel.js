// Atualização automática do painel (RF02): busca /api/pontos e atualiza resumo e cards sem recarregar a página.
(function () {
  const TIPOS = { UNIDADE: "Unidade", WIFI: "Wi-Fi", CAMERA: "Câmera" };
  const TXT = { ONLINE: "ONLINE", OFFLINE: "FORA DO AR", SEM_TESTE: "SEM TESTE" };
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const tempo = (m) => (m === null || m === undefined ? "" : "há " + (m >= 60 ? Math.floor(m / 60) + " h " : "") + (m % 60) + " min");
  function cartao(p) {
    return `<a class="cartao ${p.status}" href="#" title="Detalhe do ponto: card W08 (Sprint 3)">` +
      `<span class="nome">${esc(p.nome)}${p.critico ? ' <span class="selo crit">CRÍTICO</span>' : ""}</span>` +
      `<span class="info">${TIPOS[p.tipo] || esc(p.tipo)} · ${esc(p.olt || "sem OLT")}${p.porta_gpon ? " · PON " + esc(p.porta_gpon) : ""}${p.cto ? " · " + esc(p.cto) : ""}</span>` +
      `<span class="estado"><span class="selo ${p.status}">${TXT[p.status]}</span>` +
      `${p.status === "OFFLINE" ? '<span class="tempo">' + tempo(p.min_no_status) + "</span>" : ""}</span></a>`;
  }
  async function atualizar() {
    try {
      const r = await fetch("/api/pontos", { credentials: "same-origin" });
      if (r.status === 401) { location.href = "/login"; return; }
      const d = await r.json();
      document.getElementById("r-total").textContent = d.resumo.total;
      document.getElementById("r-on").textContent = d.resumo.ONLINE;
      document.getElementById("r-off").textContent = d.resumo.OFFLINE;
      document.getElementById("grade").innerHTML = d.pontos.map(cartao).join("");
      document.getElementById("atualizado").textContent = new Date().toLocaleTimeString("pt-BR");
    } catch (e) {
      document.getElementById("atualizado").textContent = "sem conexão com o servidor";
    }
  }
  setInterval(atualizar, window.INTERVALO || 30000);
})();
