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
  ["apple-cn", "App Store 国区"],
  ["apple-us", "App Store 外区"],
  ["epic", "Epic"],
  ["gog", "GOG"],
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

const PLATFORM_LABELS = {
  steam: "Steam",
  ps5: "PS5",
  switch: "Switch",
  "apple-cn": "App Store 国区",
  "apple-us": "App Store 外区",
  epic: "Epic",
  gog: "GOG",
};

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

function formatPrice(value, currency) {
  if (value === null || value === undefined || value === "") return "";
  const amount = Number(value);
  if (currency === "CNY") return "¥" + amount.toFixed(0);
  if (currency === "EUR") return "€" + amount.toFixed(2);
  return "$" + amount.toFixed(2);
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
  const original = formatPrice(game.price, game.currency);
  const was = game.discount > 0 ? `<span class="was">${moneyCny(game.original_price_cny)}</span>` : "";
  if (compact) {
    const img = game.cover
      ? `<img src="${game.cover}" alt="" />`
      : '<div class="cover" style="width:64px;height:64px"></div>';
    node.innerHTML = `${img}
      <div>
        <strong>${escapeHtml(game.title)}</strong>
        <div class="meta">${PLATFORM_LABELS[game.platform] || game.platform} · ${ratingLine(game)}</div>
        <div class="price">${sale} ${cny} <span class="fx">${original}</span></div>
      </div>`;
    return node;
  }
  node.innerHTML = `
    <a class="cover" href="${game.store_url || "#"}" target="_blank" rel="noreferrer" style="${game.cover ? `background-image:url('${game.cover}')` : ""}"></a>
    <div class="body">
      <h3><a href="${game.store_url || "#"}" target="_blank" rel="noreferrer">${escapeHtml(game.title)}</a></h3>
      <div class="meta">${PLATFORM_LABELS[game.platform] || game.platform} · ${ratingLine(game)}</div>
      <div class="meta">${(game.genres || []).map((g) => GENRE_LABELS[g] || g).join(" / ") || "未分类"}</div>
      <div class="price">${sale} ${cny} <span class="fx">${original}</span>${was}</div>
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

function updatedLabel(status) {
  let latest = 0;
  for (const item of Object.values(status || {})) {
    const stamp = Date.parse(item.fetched_at || "");
    if (!Number.isNaN(stamp) && stamp > latest) latest = stamp;
  }
  if (!latest) return "还没更新过";
  const minutes = Math.max(0, Math.round((Date.now() - latest) / 60000));
  if (minutes < 1) return "刚刚更新";
  if (minutes < 60) return minutes + " 分钟前更新";
  const hours = Math.round(minutes / 60);
  if (hours < 48) return hours + " 小时前更新";
  return Math.round(hours / 24) + " 天前更新";
}

function failedStores(status) {
  return Object.entries(status || {}).filter(([, item]) => item && item.ok === false);
}

function platformChips(payload) {
  const known = new Set(PLATFORMS.map(([value]) => value));
  const extra = [];
  for (const key of Object.keys(payload.status || {})) {
    if (!known.has(key)) extra.push([key, PLATFORM_LABELS[key] || key]);
  }
  return PLATFORMS.concat(extra);
}

function renderStatus(status, fx) {
  const node = $("status");
  node.innerHTML = "";
  const updated = document.createElement("div");
  updated.className = "updated";
  updated.textContent = updatedLabel(status);
  node.appendChild(updated);
  if (fx && (fx.USD || fx.EUR)) {
    const row = document.createElement("div");
    row.textContent = `汇率 USD ${Number(fx.USD || 0).toFixed(2)} · EUR ${Number(fx.EUR || 0).toFixed(2)}`;
    node.appendChild(row);
  }
  for (const [key, item] of failedStores(status)) {
    const row = document.createElement("div");
    row.className = "fail";
    row.textContent = (PLATFORM_LABELS[key] || key) + " 刷新失败";
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
  renderChips($("platforms"), platformChips(payload), state.platform, (value) => {
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
