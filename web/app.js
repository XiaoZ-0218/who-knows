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

function card(game, compact) {
  const node = document.createElement("a");
  node.className = compact ? "deal" : "card";
  node.href = game.store_url || "#";
  node.target = "_blank";
  node.rel = "noreferrer";
  const img = game.cover
    ? `<img src="${game.cover}" alt="" />`
    : compact
      ? ""
      : `<div class="cover"></div>`;
  const sale = game.discount > 0 ? `<span class="sale">-${Math.round(game.discount)}%</span>` : "";
  const price = money(game.price);
  const was = game.discount > 0 ? `<span class="was">${money(game.original_price)}</span>` : "";
  if (compact) {
    node.innerHTML = `${img || '<div class="cover" style="width:64px;height:64px"></div>'}
      <div>
        <strong>${escapeHtml(game.title)}</strong>
        <div class="meta">${PLATFORM_LABELS[game.platform] || game.platform}</div>
        <div class="price">${sale} ${price}</div>
      </div>`;
    return node;
  }
  node.innerHTML = `
    <div class="cover" style="${game.cover ? `background-image:url('${game.cover}')` : ""}"></div>
    <div class="body">
      <h3>${escapeHtml(game.title)}</h3>
      <div class="meta">${PLATFORM_LABELS[game.platform] || game.platform} · ${(game.genres || []).map((g) => GENRE_LABELS[g] || g).join(" / ") || "未分类"}</div>
      <div class="price">${sale} ${price}${was}</div>
    </div>`;
  return node;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderStatus(status) {
  const node = $("status");
  node.innerHTML = "";
  for (const key of ["steam", "ps5", "switch"]) {
    const item = status[key] || {};
    const row = document.createElement("div");
    row.innerHTML = `<span class="dot ${item.ok ? "ok" : "bad"}"></span>${PLATFORM_LABELS[key]} ${item.ok ? "在刷新" : item.error ? "这轮失败" : "还没拉到"}`;
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
  renderStatus(payload.status || {});
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
