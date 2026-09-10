"use strict";

const elements = {
  board: document.querySelector("#maze-board"),
  pathLayer: document.querySelector("#path-layer"),
  fileInput: document.querySelector("#file-input"),
  fileName: document.querySelector("#file-name"),
  saveState: document.querySelector("#save-state"),
  rows: document.querySelector("#rows-input"),
  columns: document.querySelector("#columns-input"),
  import: document.querySelector("#import-button"),
  export: document.querySelector("#export-button"),
  resize: document.querySelector("#resize-button"),
  generate: document.querySelector("#generate-button"),
  sample: document.querySelector("#sample-button"),
  undo: document.querySelector("#undo-button"),
  redo: document.querySelector("#redo-button"),
  restart: document.querySelector("#restart-button"),
  previous: document.querySelector("#previous-button"),
  play: document.querySelector("#play-button"),
  next: document.querySelector("#next-button"),
  timeline: document.querySelector("#timeline"),
  speed: document.querySelector("#speed"),
  stepCounter: document.querySelector("#step-counter"),
  phase: document.querySelector("#phase-badge"),
  minimum: document.querySelector("#minimum-steps"),
  resultCopy: document.querySelector("#result-copy"),
  activeCell: document.querySelector("#active-cell"),
  distance: document.querySelector("#current-distance"),
  visited: document.querySelector("#visited-count"),
  frontier: document.querySelector("#frontier-count"),
  queue: document.querySelector("#queue-list"),
  liveStatus: document.querySelector("#live-status"),
  toast: document.querySelector("#toast"),
  tools: [...document.querySelectorAll("[data-tool]")],
};

const state = {
  maze: [],
  start: [0, 0],
  tool: "wall",
  trace: [],
  path: [],
  minimumSteps: null,
  step: -1,
  playing: false,
  timer: null,
  history: [],
  future: [],
  dragging: false,
  dragChanged: false,
};

const cloneSnapshot = () => ({ maze: state.maze.map((row) => [...row]), start: [...state.start] });
const keyOf = ([row, column]) => `${row}:${column}`;
const displayCell = ([row, column]) => `(${row + 1}, ${column + 1})`;
const clampSize = (value) => Math.max(3, Math.min(12, Number(value) || 3));

async function api(path, payload) {
  const options = payload === undefined ? {} : {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  };
  const response = await fetch(path, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Aplikasi tidak dapat memproses permintaan.");
  return result;
}

function announce(message) {
  elements.liveStatus.textContent = message;
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("is-visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => elements.toast.classList.remove("is-visible"), 2800);
}

function stopPlayback() {
  state.playing = false;
  window.clearTimeout(state.timer);
  state.timer = null;
  elements.play.classList.remove("is-playing");
  elements.play.setAttribute("aria-label", "Mulai BFS");
}

function clearSearch(message = "Maze berubah. Jalankan BFS untuk menghitung ulang.") {
  stopPlayback();
  state.trace = [];
  state.path = [];
  state.minimumSteps = null;
  state.step = -1;
  elements.timeline.max = "0";
  elements.timeline.value = "0";
  elements.phase.textContent = "EDITING";
  elements.phase.className = "phase-badge";
  elements.minimum.textContent = "—";
  elements.resultCopy.textContent = "Tekan Play untuk menjalankan pencarian.";
  announce(message);
  renderFrame();
}

function loadMaze(maze, start, name, remember = false) {
  if (remember && state.maze.length) pushHistory();
  state.maze = maze.map((row) => [...row]);
  state.start = [...start];
  state.future = [];
  elements.rows.value = state.maze.length;
  elements.columns.value = state.maze[0].length;
  elements.fileName.textContent = name;
  elements.saveState.textContent = "Siap";
  clearSearch(`Maze ${state.maze.length} × ${state.maze[0].length} siap. Titik awal ${displayCell(state.start)}.`);
  renderGrid();
  updateHistoryButtons();
}

function pushHistory() {
  state.history.push(cloneSnapshot());
  if (state.history.length > 50) state.history.shift();
  state.future = [];
  updateHistoryButtons();
}

function applySnapshot(snapshot) {
  state.maze = snapshot.maze.map((row) => [...row]);
  state.start = [...snapshot.start];
  elements.rows.value = state.maze.length;
  elements.columns.value = state.maze[0].length;
  clearSearch();
  renderGrid();
  updateHistoryButtons();
}

function undo() {
  if (!state.history.length) return;
  state.future.push(cloneSnapshot());
  applySnapshot(state.history.pop());
}

function redo() {
  if (!state.future.length) return;
  state.history.push(cloneSnapshot());
  applySnapshot(state.future.pop());
}

function updateHistoryButtons() {
  elements.undo.disabled = state.history.length === 0;
  elements.redo.disabled = state.future.length === 0;
}

function setTool(tool) {
  state.tool = tool;
  for (const button of elements.tools) {
    const active = button.dataset.tool === tool;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  }
  announce(`Mode editor: ${tool === "wall" ? "dinding" : tool === "open" ? "jalan" : "titik mulai"}.`);
}

function paintCell(row, column) {
  const isStart = state.start[0] === row && state.start[1] === column;
  if (state.tool === "start") {
    if (state.maze[row][column] === -1) {
      showToast("Buka petak ini sebelum menjadikannya titik mulai.");
      return false;
    }
    if (isStart) return false;
  }
  if (state.tool === "wall" && isStart) {
    showToast("Titik mulai tidak dapat dijadikan dinding.");
    return false;
  }

  if (state.tool === "start") state.start = [row, column];
  else state.maze[row][column] = state.tool === "wall" ? -1 : 0;
  elements.saveState.textContent = "Diubah";
  clearSearch();
  renderGrid();
  return true;
}

function beginPaint(row, column) {
  state.dragging = true;
  state.dragChanged = false;
  pushHistory();
  state.dragChanged = paintCell(row, column);
  if (!state.dragChanged) {
    state.history.pop();
    updateHistoryButtons();
  }
}

function continuePaint(row, column, event) {
  if (!state.dragging || event.buttons !== 1 || state.tool === "start") return;
  const changed = paintCell(row, column);
  state.dragChanged ||= changed;
}

function renderGrid() {
  if (!state.maze.length) return;
  const rows = state.maze.length;
  const columns = state.maze[0].length;
  elements.board.style.setProperty("--rows", rows);
  elements.board.style.setProperty("--columns", columns);
  elements.board.style.setProperty("--maze-ratio", columns / rows);
  elements.board.replaceChildren();

  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const cell = document.createElement("button");
      cell.type = "button";
      cell.className = "maze-cell";
      cell.dataset.row = row;
      cell.dataset.column = column;
      cell.setAttribute("role", "gridcell");
      cell.addEventListener("pointerdown", () => beginPaint(row, column));
      cell.addEventListener("pointerenter", (event) => continuePaint(row, column, event));
      cell.addEventListener("keydown", (event) => handleCellKey(event, row, column));
      elements.board.append(cell);
    }
  }
  renderFrame();
}

function handleCellKey(event, row, column) {
  const moves = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
  if (moves[event.key]) {
    event.preventDefault();
    const [dr, dc] = moves[event.key];
    const nextRow = Math.max(0, Math.min(state.maze.length - 1, row + dr));
    const nextColumn = Math.max(0, Math.min(state.maze[0].length - 1, column + dc));
    elements.board.querySelector(`[data-row="${nextRow}"][data-column="${nextColumn}"]`)?.focus();
  }
}

function renderFrame() {
  if (!state.maze.length || !elements.board.children.length) return;
  const steps = state.step >= 0 ? state.trace.slice(0, state.step + 1) : [];
  const visited = new Set(steps.map((item) => keyOf(item.current)));
  const currentStep = state.step >= 0 ? state.trace[state.step] : null;
  const frontier = new Set((currentStep?.frontier || []).map(keyOf));
  const complete = state.trace.length > 0 && state.step === state.trace.length - 1;
  const finalPath = complete ? new Set(state.path.map(keyOf)) : new Set();
  const exit = complete && state.path.length ? keyOf(state.path.at(-1)) : null;

  for (const cell of elements.board.children) {
    const row = Number(cell.dataset.row);
    const column = Number(cell.dataset.column);
    const key = keyOf([row, column]);
    const isStart = key === keyOf(state.start);
    cell.className = "maze-cell";
    cell.classList.toggle("is-wall", state.maze[row][column] === -1);
    cell.classList.toggle("is-visited", visited.has(key));
    cell.classList.toggle("is-frontier", frontier.has(key));
    cell.classList.toggle("is-current", key === keyOf(currentStep?.current || [-1, -1]));
    cell.classList.toggle("is-path", finalPath.has(key));
    cell.classList.toggle("is-exit", key === exit);
    cell.replaceChildren();
    if (isStart) {
      const marker = document.createElement("span");
      marker.className = "cell-start";
      marker.innerHTML = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="m10 3 5 14-5-3-5 3z"/></svg>';
      cell.append(marker);
    } else if (key === exit) {
      const marker = document.createElement("span");
      marker.className = "cell-exit";
      cell.append(marker);
    }
    const type = state.maze[row][column] === -1 ? "dinding" : "jalan";
    cell.setAttribute("aria-label", `Baris ${row + 1}, kolom ${column + 1}, ${isStart ? "titik mulai" : type}`);
  }

  renderInspector(currentStep, complete);
  window.requestAnimationFrame(() => renderPath(complete));
}

function renderPath(complete) {
  elements.pathLayer.replaceChildren();
  if (!complete || state.path.length < 2) return;
  const layerRect = elements.pathLayer.getBoundingClientRect();
  const points = state.path.map(([row, column]) => {
    const cell = elements.board.querySelector(`[data-row="${row}"][data-column="${column}"]`);
    const rect = cell.getBoundingClientRect();
    return `${rect.left - layerRect.left + rect.width / 2},${rect.top - layerRect.top + rect.height / 2}`;
  });
  const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
  polyline.setAttribute("class", "path-line");
  polyline.setAttribute("points", points.join(" "));
  elements.pathLayer.append(polyline);
}

function renderInspector(currentStep, complete) {
  elements.timeline.max = state.trace.length;
  elements.timeline.value = state.step + 1;
  elements.timeline.setAttribute("aria-valuetext", `${state.step + 1} dari ${state.trace.length} langkah pencarian`);
  elements.stepCounter.textContent = `${state.step + 1} / ${state.trace.length}`;
  elements.activeCell.textContent = currentStep ? displayCell(currentStep.current) : "—";
  elements.distance.textContent = currentStep?.distance ?? "—";
  elements.visited.textContent = currentStep?.visitedCount ?? 0;
  elements.frontier.textContent = currentStep?.frontier?.length ?? 0;

  if (!state.trace.length) {
    elements.phase.textContent = "EDITING";
    elements.phase.className = "phase-badge";
  } else if (complete) {
    elements.phase.textContent = "COMPLETE";
    elements.phase.className = "phase-badge is-complete";
    elements.minimum.textContent = state.minimumSteps;
    elements.resultCopy.textContent = state.minimumSteps === -1
      ? "Seluruh ruang terjangkau telah diperiksa; tidak ada exit."
      : `Exit pertama dicapai di ${displayCell(state.path.at(-1))}.`;
  } else {
    elements.phase.textContent = state.playing ? "RUNNING" : "PAUSED";
    elements.phase.className = "phase-badge is-running";
    elements.minimum.textContent = "—";
    elements.resultCopy.textContent = currentStep
      ? `BFS sedang memeriksa lapisan jarak ${currentStep.distance}.`
      : "Pencarian siap dijalankan.";
  }

  elements.queue.replaceChildren();
  const queue = currentStep?.frontier || [];
  if (!queue.length) {
    const empty = document.createElement("p");
    empty.className = "empty-copy";
    empty.textContent = complete ? "Antrean kosong. Pencarian selesai." : "Antrean akan muncul saat BFS berjalan.";
    elements.queue.append(empty);
  } else {
    for (const position of queue.slice(0, 18)) {
      const chip = document.createElement("span");
      chip.className = "queue-chip";
      chip.textContent = displayCell(position);
      elements.queue.append(chip);
    }
  }
}

async function ensureSearch() {
  if (state.trace.length) return true;
  try {
    announce("Menghitung trace BFS dengan Python...");
    const result = await api("/api/search", { maze: state.maze, start: state.start });
    state.trace = result.trace;
    state.path = result.path;
    state.minimumSteps = result.minimumSteps;
    state.step = -1;
    elements.timeline.max = state.trace.length;
    renderFrame();
    return true;
  } catch (error) {
    showToast(error.message);
    announce(`Kesalahan: ${error.message}`);
    return false;
  }
}

async function playPause() {
  if (state.playing) {
    stopPlayback();
    renderFrame();
    announce("Animasi dijeda.");
    return;
  }
  if (!(await ensureSearch())) return;
  if (state.step >= state.trace.length - 1) state.step = -1;
  state.playing = true;
  elements.play.classList.add("is-playing");
  elements.play.setAttribute("aria-label", "Jeda BFS");
  tick();
}

function tick() {
  if (!state.playing) return;
  if (state.step >= state.trace.length - 1) {
    stopPlayback();
    renderFrame();
    announce(state.minimumSteps === -1 ? "Pencarian selesai. Tidak ada jalan keluar." : `Pencarian selesai. Langkah minimum ${state.minimumSteps}.`);
    return;
  }
  state.step += 1;
  renderFrame();
  state.timer = window.setTimeout(tick, 650 - Number(elements.speed.value) * 60);
}

async function stepBy(amount) {
  stopPlayback();
  if (!(await ensureSearch())) return;
  state.step = Math.max(-1, Math.min(state.trace.length - 1, state.step + amount));
  renderFrame();
  announce(state.step < 0 ? "Kembali ke kondisi awal." : `Langkah pencarian ${state.step + 1} dari ${state.trace.length}.`);
}

function restart() {
  stopPlayback();
  state.step = -1;
  renderFrame();
  announce("Visualisasi dikembalikan ke awal.");
}

function resizeMaze() {
  const rows = clampSize(elements.rows.value);
  const columns = clampSize(elements.columns.value);
  pushHistory();
  const maze = Array.from({ length: rows }, () => Array(columns).fill(0));
  loadMaze(maze, [Math.floor(rows / 2), Math.floor(columns / 2)], "maze-baru.txt");
}

function generateMaze() {
  const rows = clampSize(elements.rows.value);
  const columns = clampSize(elements.columns.value);
  pushHistory();
  const maze = Array.from({ length: rows }, () => Array(columns).fill(-1));
  const start = [1 + Math.floor(Math.random() * (rows - 2)), 1 + Math.floor(Math.random() * (columns - 2))];
  const side = Math.floor(Math.random() * 4);
  const target = side === 0 ? [0, Math.floor(Math.random() * columns)]
    : side === 1 ? [rows - 1, Math.floor(Math.random() * columns)]
      : side === 2 ? [Math.floor(Math.random() * rows), 0]
        : [Math.floor(Math.random() * rows), columns - 1];
  let cursor = [...start];
  maze[cursor[0]][cursor[1]] = 0;
  while (cursor[0] !== target[0] || cursor[1] !== target[1]) {
    const choices = [];
    if (cursor[0] < target[0]) choices.push([cursor[0] + 1, cursor[1]]);
    if (cursor[0] > target[0]) choices.push([cursor[0] - 1, cursor[1]]);
    if (cursor[1] < target[1]) choices.push([cursor[0], cursor[1] + 1]);
    if (cursor[1] > target[1]) choices.push([cursor[0], cursor[1] - 1]);
    cursor = choices[Math.floor(Math.random() * choices.length)];
    maze[cursor[0]][cursor[1]] = 0;
  }
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      if (Math.random() < .34) maze[row][column] = 0;
    }
  }
  loadMaze(maze, start, "maze-acak.txt");
  announce("Maze acak dengan minimal satu jalan keluar telah dibuat.");
}

async function loadSample(remember = true) {
  try {
    const result = await api("/api/maze");
    loadMaze(result.maze, result.start, "maze.txt", remember);
  } catch (error) {
    showToast(error.message);
  }
}

async function importFile(file) {
  if (!file) return;
  try {
    const text = await file.text();
    const result = await api("/api/parse", { text });
    loadMaze(result.maze, result.start, file.name, true);
    showToast("Maze berhasil diimpor.");
  } catch (error) {
    showToast(error.message);
    announce(`Impor gagal: ${error.message}`);
  } finally {
    elements.fileInput.value = "";
  }
}

function exportMaze() {
  const rows = state.maze.length;
  const columns = state.maze[0].length;
  const text = [
    `${rows} ${columns}`,
    ...state.maze.map((row) => row.join(" ")),
    `${state.start[0] + 1} ${state.start[1] + 1}`,
    "",
  ].join("\n");
  const url = URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "maze.txt";
  link.click();
  URL.revokeObjectURL(url);
  elements.saveState.textContent = "Diekspor";
  showToast("maze.txt berhasil diekspor.");
}

elements.tools.forEach((button) => button.addEventListener("click", () => setTool(button.dataset.tool)));
elements.import.addEventListener("click", () => elements.fileInput.click());
elements.fileInput.addEventListener("change", () => importFile(elements.fileInput.files[0]));
elements.export.addEventListener("click", exportMaze);
elements.resize.addEventListener("click", resizeMaze);
elements.generate.addEventListener("click", generateMaze);
elements.sample.addEventListener("click", () => loadSample(true));
elements.undo.addEventListener("click", undo);
elements.redo.addEventListener("click", redo);
elements.restart.addEventListener("click", restart);
elements.previous.addEventListener("click", () => stepBy(-1));
elements.next.addEventListener("click", () => stepBy(1));
elements.play.addEventListener("click", playPause);
elements.timeline.addEventListener("input", () => {
  stopPlayback();
  state.step = Number(elements.timeline.value) - 1;
  renderFrame();
});
window.addEventListener("pointerup", () => { state.dragging = false; });
window.addEventListener("resize", () => renderPath(state.trace.length > 0 && state.step === state.trace.length - 1));
window.addEventListener("keydown", (event) => {
  if (["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) return;
  if (event.code === "Space") { event.preventDefault(); playPause(); }
  if (event.key === "ArrowLeft") { event.preventDefault(); stepBy(-1); }
  if (event.key === "ArrowRight") { event.preventDefault(); stepBy(1); }
  if (event.key === "Home") { event.preventDefault(); restart(); }
  if (event.ctrlKey && event.key.toLowerCase() === "z") { event.preventDefault(); undo(); }
  if (event.ctrlKey && event.key.toLowerCase() === "y") { event.preventDefault(); redo(); }
});

loadSample(false);
