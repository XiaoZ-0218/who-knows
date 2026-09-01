const state = {
  mood: "hot",
  platform: "",
  players: "",
  genre: "",
};

const MOODS = [
  ["hot", "热门"],
  ["new", "新发"],
  ["sleeper", "冷门好活"],
];

const PLATFORMS = [
  ["", "全部平台"],
  ["steam", "Steam"],
  ["ps5", "PS5"],
  ["switch", "Switch"],
];

const PLAYERS = [
  ["", "人数不限"],
  ["solo", "单人"],
  ["duo", "双人"],
  ["multi", "多人"],
];

const GENRE_LABELS = {
  action: "动作",
  adventure: "冒险",
  rpg: "角色扮演",
  shooter: "射击",
  sports: "体育",
  racing: "竞速",
  puzzle: "解谜",
  horror: "恐怖",
  indie: "独立",
  strategy: "策略",
  simulation: "模拟",
  fighting: "格斗",
  music: "音乐",
};

const PLATFORM_LABELS = { steam: "Steam", ps5: "PS5", switch: "Switch" };

function $(id) {
  return document.getElementById(id);
}

function renderChips(node, items, current, onPick) {
  node.innerHTML = "";
  for (const [value, label] of items) {
    const button = document.createElement("button");
    button.textContent = label;
    button.className = value === current ? "active" : "";
    button.addEventListener("click", () => onPick(value));
    node.appendChild(button);
  }
}

function money(value) {
  if (value === null || value === undefined || value === "") return "";
  return "$" + Number(value).toFixed(2);
}

function moneyCny(value) {
  if (value === null || value === undefined || value === "") return "";
  return "¥" + Number(value).toFixed(0);
}

function ratingLine(game) {
  if (!game.rating) return "暂无评分";
  const people = game.popularity ? ` · ${Math.round(game.popularity)} 人评` : "";
  return `${Math.round(game.rating)}分${people}`;
}

function talk(game) {
  return (game.links || [])
    .map(
      (link) =>
        `<a class="talk-link" href="${link.url}" target="_blank" rel="noreferrer">${escapeHtml(link.label)}</a>`
    )
    .join("");
}

function card(game, compact) {
  const node = document.createElement(compact ? "a" : "article");
  node.className = compact ? "deal" : "card";
  if (compact) {
    node.href = game.store_url || "#";
    node.target = "_blank";
    node.rel = "noreferrer";
  }
  const sale = game.discount > 0 ? `<span class="sale">-${Math.round(game.discount)}%</span>` : "";
  const cny = moneyCny(game.price_cny);
  const usd = money(game.price);
  const was = game.discount > 0 ? `<span class="was">${moneyCny(game.original_price_cny)}</span>` : "";
  if (compact) {
    const img = game.cover
      ? `<img src="${game.cover}" alt="" />`
      : '<div class="cover" style="width:64px;height:64px"></div>';
    node.innerHTML = `${img}
      <div>
        <strong>${escapeHtml(game.title)}</strong>
        <div class="meta">${PLATFORM_LABELS[game.platform] || game.platform} · ${ratingLine(game)}</div>
        <div class="price">${sale} ${cny} <span class="fx">${usd}</span></div>
      </div>`;
    return node;
  }
  node.innerHTML = `
    <a class="cover" href="${game.store_url || "#"}" target="_blank" rel="noreferrer" style="${game.cover ? `background-image:url('${game.cover}')` : ""}"></a>
    <div class="body">
      <h3><a href="${game.store_url || "#"}" target="_blank" rel="noreferrer">${escapeHtml(game.title)}</a></h3>
      <div class="meta">${PLATFORM_LABELS[game.platform] || game.platform} · ${ratingLine(game)}</div>
      <div class="meta">${(game.genres || []).map((g) => GENRE_LABELS[g] || g).join(" / ") || "未分类"}</div>
      <div class="price">${sale} ${cny} <span class="fx">${usd}</span>${was}</div>
      <div class="talk">${talk(game)}</div>
    </div>`;
  return node;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderStatus(status, fx) {
  const node = $("status");
  node.innerHTML = "";
  for (const key of ["steam", "ps5", "switch"]) {
    const item = status[key] || {};
    const row = document.createElement("div");
    row.innerHTML = `<span class="dot ${item.ok ? "ok" : "bad"}"></span>${PLATFORM_LABELS[key]} ${item.ok ? "在刷新" : item.error ? "这轮失败" : "还没拉到"}`;
    node.appendChild(row);
  }
  if (fx && (fx.USD || fx.EUR)) {
    const row = document.createElement("div");
    row.textContent = `汇率 USD ${Number(fx.USD || 0).toFixed(2)} · EUR ${Number(fx.EUR || 0).toFixed(2)}`;
    node.appendChild(row);
  }
}

async function load() {
  const params = new URLSearchParams();
  if (state.mood) params.set("mood", state.mood);
  if (state.platform) params.set("platform", state.platform);
  if (state.players) params.set("players", state.players);
  if (state.genre) params.set("genre", state.genre);
  const payload = await fetch("/api/board?" + params.toString()).then((r) => r.json());
  renderStatus(payload.status || {}, payload.fx || {});
  renderChips($("moods"), MOODS, state.mood, (value) => {
    state.mood = value;
    load();
  });
  renderChips($("platforms"), PLATFORMS, state.platform, (value) => {
    state.platform = value;
    load();
  });
  renderChips($("players"), PLAYERS, state.players, (value) => {
    state.players = value;
    load();
  });
  const genres = [["", "全部分类"], ...(payload.genres || []).map((g) => [g, GENRE_LABELS[g] || g])];
  renderChips($("genres"), genres, state.genre, (value) => {
    state.genre = value;
    load();
  });

  const rail = $("deal-rail");
  rail.innerHTML = "";
  if (!payload.deals || payload.deals.length === 0) {
    rail.innerHTML = '<p class="meta">这一筛下没有特价。</p>';
  } else {
    payload.deals.forEach((game) => rail.appendChild(card(game, true)));
  }

  const grid = $("grid");
  grid.innerHTML = "";
  $("count").textContent = payload.games.length ? `今晚这批 ${payload.games.length} 款` : "这一筛是空的，换个口味试试。";
  payload.games.forEach((game) => grid.appendChild(card(game, false)));
}

load();
setInterval(load, 60 * 1000);
