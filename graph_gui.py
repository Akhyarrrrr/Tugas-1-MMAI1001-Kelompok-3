"""Antarmuka Tkinter untuk membandingkan dan mengamati shortest path."""

from __future__ import annotations

import math
from pathlib import Path
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from shortest_path import (
    Graph,
    GraphInput,
    NegativeCycleError,
    SearchResult,
    SearchStep,
    bellman_ford,
    dijkstra,
    has_negative_edge,
    read_graph,
)


BG = "#f4f7f6"
PANEL = "#ffffff"
INK = "#18313b"
MUTED = "#5b7078"
CANVAS = "#fbfcfb"
EDGE = "#a0b1b7"
CYAN = "#c88744"
AMBER = "#1d7388"
GREEN = "#25846e"
RED = "#be6c59"
ACTIVE = "#f2d5b6"
BORDER = "#dce5e5"


def layout_graph(graph: Graph) -> dict[str, tuple[float, float]]:
    """Tata letak stabil tanpa pustaka tambahan; graf besar memakai lingkaran."""
    vertices = sorted(graph)
    count = len(vertices)
    if set(vertices) == {f"V{i}" for i in range(1, 16)}:
        return {
            "V1": (.08, .49), "V2": (.23, .34), "V3": (.40, .38),
            "V4": (.24, .70), "V5": (.40, .15), "V6": (.53, .59),
            "V7": (.58, .31), "V8": (.43, .86), "V9": (.58, .12),
            "V10": (.68, .67), "V11": (.77, .35), "V12": (.76, .12),
            "V13": (.88, .53), "V14": (.78, .85), "V15": (.91, .21),
        }
    if count == 1:
        return {vertices[0]: (0.5, 0.5)}
    if count > 80:
        return {v: (0.5 + 0.42 * math.cos(2 * math.pi * i / count),
                    0.5 + 0.42 * math.sin(2 * math.pi * i / count))
                for i, v in enumerate(vertices)}
    rng = random.Random(2026)
    points = {v: [rng.uniform(100, 700), rng.uniform(90, 510)] for v in vertices}
    links = {tuple(sorted((u, v))) for u in graph for v in graph[u] if u != v}
    spacing = math.sqrt(800 * 600 / count)
    for turn in range(180):
        forces = {v: [0.0, 0.0] for v in vertices}
        for i, left in enumerate(vertices):
            for right in vertices[i + 1:]:
                dx = points[left][0] - points[right][0]
                dy = points[left][1] - points[right][1]
                distance = max(1.0, math.hypot(dx, dy))
                force = spacing * spacing / distance
                fx, fy = dx / distance * force, dy / distance * force
                forces[left][0] += fx
                forces[left][1] += fy
                forces[right][0] -= fx
                forces[right][1] -= fy
        for left, right in links:
            dx = points[left][0] - points[right][0]
            dy = points[left][1] - points[right][1]
            distance = max(1.0, math.hypot(dx, dy))
            force = distance * distance / spacing
            fx, fy = dx / distance * force, dy / distance * force
            forces[left][0] -= fx
            forces[left][1] -= fy
            forces[right][0] += fx
            forces[right][1] += fy
        temperature = 24 * (1 - turn / 180) + 0.4
        for vertex in vertices:
            fx, fy = forces[vertex]
            length = max(1.0, math.hypot(fx, fy))
            points[vertex][0] = min(740, max(60, points[vertex][0] + fx / length * min(temperature, length)))
            points[vertex][1] = min(550, max(50, points[vertex][1] + fy / length * min(temperature, length)))
    # Pisahkan simpul yang berhimpit tanpa menambah dependensi layout.
    for _ in range(70):
        moved = False
        for i, left in enumerate(vertices):
            for right in vertices[i + 1:]:
                dx = points[right][0] - points[left][0]
                dy = points[right][1] - points[left][1]
                distance = max(0.01, math.hypot(dx, dy))
                if distance >= 88:
                    continue
                push = (88 - distance) / 2
                nx, ny = dx / distance, dy / distance
                points[left][0] = min(740, max(60, points[left][0] - nx * push))
                points[left][1] = min(550, max(50, points[left][1] - ny * push))
                points[right][0] = min(740, max(60, points[right][0] + nx * push))
                points[right][1] = min(550, max(50, points[right][1] + ny * push))
                moved = True
        if not moved:
            break
    return {v: (points[v][0] / 800, points[v][1] / 600) for v in vertices}


class GraphStudio:
    def __init__(self, root: tk.Tk, source: GraphInput, file_path: Path) -> None:
        self.root = root
        self.source = source
        self.file_path = file_path
        self.positions = layout_graph(source.graph)
        self.results: dict[str, SearchResult] = {}
        self.errors: dict[str, str] = {}
        self.steps: tuple[SearchStep, ...] = ()
        self.position = 0
        self.timer: str | None = None
        self.dragged: str | None = None
        self.setting_progress = False
        self.start_var = tk.StringVar(value=source.start)
        self.goal_var = tk.StringVar(value=source.goal)
        self.algorithm_var = tk.StringVar(value="Dijkstra")
        self.speed_var = tk.StringVar(value="Sedang")
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="Muat graf lalu pilih Hitung jalur.")
        self.file_var = tk.StringVar(value=file_path.name)
        self.step_var = tk.StringVar(value="0/0")
        self.detail_var = tk.StringVar(value="Graf siap dianalisis.")
        self._build()
        self._refresh_selectors()
        self.run_analysis()

    def _build(self) -> None:
        root = self.root
        root.title("Jalur Terpendek | MMAI1001 Kelompok 3")
        root.geometry("1280x800")
        root.minsize(900, 650)
        root.configure(bg=BG)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TCombobox", padding=5, fieldbackground=PANEL, background=PANEL)
        style.configure("TScale", background=PANEL)

        outer = tk.Frame(root, bg=BG, padx=18, pady=15)
        outer.pack(fill="both", expand=True)

        heading = tk.Frame(outer, bg=BG)
        heading.pack(fill="x", pady=(0, 13))
        tk.Label(heading, text="Jalur Terpendek", bg=BG, fg=INK,
                 font=("Segoe UI", 21, "bold")).pack(side="left")
        tk.Label(heading, text="MMAI1001  ·  Tugas 1  ·  Kelompok 3", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="right", pady=(10, 0))

        toolbar = tk.Frame(outer, bg=PANEL, highlightthickness=1,
                           highlightbackground=BORDER, padx=14, pady=11)
        toolbar.pack(fill="x", pady=(0, 11))
        tk.Button(toolbar, text="Buka file graf", command=self.open_file, bg="#eef3f3",
                  fg=INK, activebackground="#e1ebeb", relief="flat", bd=0,
                  font=("Segoe UI", 9), padx=12, pady=6, cursor="hand2").pack(side="left")
        tk.Label(toolbar, textvariable=self.file_var, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=(12, 22))
        tk.Label(toolbar, text="Awal", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
        self.start_box = ttk.Combobox(toolbar, textvariable=self.start_var, width=8,
                                      state="readonly")
        self.start_box.pack(side="left", padx=(0, 17))
        tk.Label(toolbar, text="Tujuan", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
        self.goal_box = ttk.Combobox(toolbar, textvariable=self.goal_var, width=8,
                                     state="readonly")
        self.goal_box.pack(side="left", padx=(0, 17))
        tk.Button(toolbar, text="Hitung jalur", command=self.run_analysis,
                  bg=AMBER, fg="white", activebackground="#155b6d",
                  activeforeground="white", relief="flat", bd=0,
                  font=("Segoe UI", 9, "bold"), padx=15, pady=6,
                  cursor="hand2").pack(side="left")

        tk.Label(outer, textvariable=self.status_var, bg=BG, fg=MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(side="bottom", fill="x", pady=(8, 0))

        transport = tk.Frame(outer, bg=PANEL, highlightthickness=1,
                             highlightbackground=BORDER, padx=11, pady=9)
        transport.pack(side="bottom", fill="x", pady=(10, 0))
        def control(text: str, command, *, primary: bool = False) -> tk.Button:
            return tk.Button(transport, text=text, command=command,
                             bg=AMBER if primary else "#eef3f3",
                             fg="white" if primary else INK,
                             activebackground="#155b6d" if primary else "#e1ebeb",
                             activeforeground="white" if primary else INK,
                             relief="flat", bd=0, font=("Segoe UI", 9, "bold") if primary
                             else ("Segoe UI", 9), padx=11, pady=6, cursor="hand2")
        control("Ke awal", self.reset).pack(side="left", padx=(0, 6))
        control("Mundur", lambda: self.step_by(-1)).pack(side="left", padx=6)
        self.play_button = control("Putar", self.play_pause, primary=True)
        self.play_button.pack(side="left", padx=6)
        control("Maju", lambda: self.step_by(1)).pack(side="left", padx=6)
        self.progress = ttk.Scale(transport, from_=0, to=1, variable=self.progress_var,
                                  command=self._on_progress)
        self.progress.pack(side="left", fill="x", expand=True, padx=(18, 12))
        tk.Label(transport, textvariable=self.step_var, bg=PANEL, fg=INK,
                 font=("Segoe UI", 9)).pack(side="left")
        tk.Label(transport, text="Kecepatan", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=(17, 6))
        ttk.Combobox(transport, textvariable=self.speed_var,
                     values=("Lambat", "Sedang", "Cepat"), state="readonly",
                     width=8).pack(side="left")

        workspace = ttk.PanedWindow(outer, orient="horizontal")
        workspace.pack(fill="both", expand=True)
        graph_frame = tk.Frame(workspace, bg=PANEL, highlightthickness=1,
                               highlightbackground=BORDER)
        graph_heading = tk.Frame(graph_frame, bg=PANEL, padx=13, pady=10)
        graph_heading.pack(fill="x")
        tk.Label(graph_heading, text="Graf berbobot", bg=PANEL, fg=INK,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(graph_heading, text="Seret simpul untuk mengatur posisi", bg=PANEL,
                 fg=MUTED, font=("Segoe UI", 8)).pack(side="right", pady=(3, 0))
        self.canvas = tk.Canvas(graph_frame, bg=CANVAS, highlightthickness=0, bd=0,
                                cursor="hand2")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _event: self.render())
        self.canvas.bind("<ButtonPress-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_move)
        self.canvas.bind("<ButtonRelease-1>", self._drag_end)

        results_host = tk.Frame(workspace, bg=PANEL, width=335,
                                highlightthickness=1, highlightbackground=BORDER)
        results_host.pack_propagate(False)
        result_canvas = tk.Canvas(results_host, bg=PANEL, highlightthickness=0, bd=0)
        result_scroll = ttk.Scrollbar(results_host, orient="vertical",
                                      command=result_canvas.yview)
        result_canvas.configure(yscrollcommand=result_scroll.set)
        result_scroll.pack(side="right", fill="y")
        result_canvas.pack(side="left", fill="both", expand=True)
        right = tk.Frame(result_canvas, bg=PANEL, padx=12, pady=12)
        content = result_canvas.create_window((0, 0), window=right, anchor="nw")
        right.bind("<Configure>", lambda _event: result_canvas.configure(
            scrollregion=result_canvas.bbox("all")))
        result_canvas.bind("<Configure>", lambda event: result_canvas.itemconfigure(
            content, width=event.width))
        workspace.add(graph_frame, weight=4)
        workspace.add(results_host, weight=1)

        tk.Label(right, text="Perbandingan hasil", bg=PANEL, fg=INK,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(right, text="Jalur, bobot minimum, dan waktu hitung", bg=PANEL,
                 fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 8))
        self.result_widgets = {}
        for name in ("Dijkstra", "Bellman-Ford"):
            card = tk.Frame(right, bg=PANEL, highlightthickness=1,
                            highlightbackground=BORDER, padx=11, pady=10)
            card.pack(fill="x", pady=(0, 8))
            top = tk.Frame(card, bg=PANEL)
            top.pack(fill="x")
            tk.Label(top, text=name, bg=PANEL, fg=INK,
                     font=("Segoe UI", 10, "bold")).pack(side="left", anchor="n")
            cost_box = tk.Frame(top, bg=PANEL)
            cost_box.pack(side="right")
            cost = tk.Label(cost_box, bg=PANEL, fg=AMBER,
                            font=("Segoe UI", 21, "bold"))
            cost.pack(anchor="e")
            tk.Label(cost_box, text="bobot minimum", bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 8)).pack(anchor="e")
            route = tk.Label(card, bg=PANEL, fg=INK, justify="left", anchor="w",
                             font=("Segoe UI", 9))
            route.pack(fill="x", pady=(9, 6))
            timing = tk.Label(card, bg=PANEL, fg=MUTED, anchor="w",
                              font=("Segoe UI", 9))
            timing.pack(fill="x")
            meta = tk.Label(card, bg=PANEL, fg=MUTED, anchor="w",
                            font=("Segoe UI", 8))
            meta.pack(fill="x", pady=(3, 0))
            self.result_widgets[name] = (cost, route, timing, meta)

        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=(7, 13))
        tk.Label(right, text="Langkah pencarian", bg=PANEL, fg=INK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 7))
        self.algorithm_box = ttk.Combobox(right, textvariable=self.algorithm_var,
                                          values=("Dijkstra", "Bellman-Ford"),
                                          state="readonly")
        self.algorithm_box.pack(fill="x")
        self.algorithm_box.bind("<<ComboboxSelected>>", lambda _event: self.select_algorithm())
        self.detail_label = tk.Label(right, textvariable=self.detail_var,
                                     bg="#ecf5f5", fg=INK, justify="left", anchor="nw",
                                     font=("Segoe UI", 9), padx=10, pady=9,
                                     wraplength=280)
        self.detail_label.pack(fill="x", pady=(10, 15))
        tk.Label(right, text="Keterangan", bg=PANEL, fg=INK,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 7))
        for color, meaning in ((GREEN, "Titik awal"), (RED, "Titik tujuan"),
                               (CYAN, "Sisi yang diperiksa"), (AMBER, "Jalur terbaik")):
            row = tk.Frame(right, bg=PANEL)
            row.pack(fill="x", pady=2)
            tk.Label(row, text="●", fg=color, bg=PANEL,
                     font=("Segoe UI", 13)).pack(side="left")
            tk.Label(row, text=meaning, fg=MUTED, bg=PANEL,
                     font=("Segoe UI", 9)).pack(side="left", padx=6)

        def resize_results(event: tk.Event) -> None:
            width = max(180, event.width - 36)
            for _cost, route, _timing, _meta in self.result_widgets.values():
                route.configure(wraplength=width)
            self.detail_label.configure(wraplength=width - 12)
        right.bind("<Configure>", resize_results, add="+")

        root.bind("<space>", self._space)
        root.bind("<Left>", self._left)
        root.bind("<Right>", self._right)
        root.protocol("WM_DELETE_WINDOW", self._close)

    def _refresh_selectors(self) -> None:
        values = sorted(self.source.graph)
        self.start_box.configure(values=values)
        self.goal_box.configure(values=values)

    def open_file(self) -> None:
        path = filedialog.askopenfilename(title="Pilih file graf", initialdir=self.file_path.parent,
                                           filetypes=(("File teks", "*.txt"), ("Semua file", "*.*")))
        if not path:
            return
        try:
            source = read_graph(path)
        except ValueError as exc:
            messagebox.showerror("File graf tidak valid", str(exc), parent=self.root)
            return
        self.pause()
        self.source = source
        self.file_path = Path(path)
        self.file_var.set(self.file_path.name)
        self.start_var.set(source.start)
        self.goal_var.set(source.goal)
        self.positions = layout_graph(source.graph)
        self._refresh_selectors()
        self.run_analysis()

    def run_analysis(self) -> None:
        self.pause()
        graph = self.source.graph
        start, goal = self.start_var.get(), self.goal_var.get()
        self.results.clear()
        self.errors.clear()
        if has_negative_edge(graph):
            self.errors["Dijkstra"] = "Tidak berlaku: graf memuat bobot negatif."
        else:
            self.results["Dijkstra"] = dijkstra(graph, start, goal)
        try:
            self.results["Bellman-Ford"] = bellman_ford(graph, start, goal)
        except NegativeCycleError as exc:
            self.errors["Bellman-Ford"] = str(exc)
        self._update_results()
        if self.algorithm_var.get() not in self.results and self.results:
            self.algorithm_var.set(next(iter(self.results)))
        self.select_algorithm()
        self.status_var.set(f"{len(graph)} simpul, {sum(map(len, graph.values()))} sisi berarah. "
                            "Waktu hitung tidak termasuk animasi.")

    def _update_results(self) -> None:
        for name, widgets in self.result_widgets.items():
            cost_label, route_label, time_label, meta_label = widgets
            if name in self.errors:
                cost_label.configure(text="—")
                route_label.configure(text=self.errors[name])
                time_label.configure(text="")
                meta_label.configure(text="")
                continue
            result = self.results[name]
            path = " → ".join(result.path) if result.path else "Tidak ada jalur"
            cost_label.configure(text=f"{result.cost:g}" if result.cost is not None else "—")
            route_label.configure(text=f"Jalur: {path}")
            time_label.configure(text=f"Waktu hitung: {result.elapsed_ns / 1000:.2f} µs")
            meta_label.configure(text=f"{result.examined} simpul diperiksa · "
                                      f"{result.relaxations} relaksasi")

    def select_algorithm(self) -> None:
        self.pause()
        name = self.algorithm_var.get()
        if name not in self.results:
            self.steps = ()
            self.position = 0
            self.detail_var.set(self.errors.get(name, "Tidak ada hasil."))
        else:
            algorithm = dijkstra if name == "Dijkstra" else bellman_ford
            self.steps = algorithm(self.source.graph, self.start_var.get(),
                                   self.goal_var.get(), trace=True).steps
            self.position = len(self.steps) + 1
        self.progress.configure(to=max(1, len(self.steps) + 1))
        self.render()

    def _max_position(self) -> int:
        return len(self.steps) + 1 if self.algorithm_var.get() in self.results else 0

    def render(self) -> None:
        if not hasattr(self, "canvas"):
            return
        canvas = self.canvas
        canvas.delete("all")
        graph = self.source.graph
        width = max(canvas.winfo_width(), 400)
        height = max(canvas.winfo_height(), 350)
        canvas.create_rectangle(0, 0, width, height, fill=CANVAS, outline="")
        xy = {v: (45 + x * (width - 90), 40 + y * (height - 80))
              for v, (x, y) in self.positions.items()}
        step = self.steps[self.position - 1] if 1 <= self.position <= len(self.steps) else None
        final = bool(self.results) and self.position == self._max_position()
        result = self.results.get(self.algorithm_var.get())
        path_edges = set(zip(result.path, result.path[1:])) if final and result else set()
        active_edge = step.edge if step else None
        handled: set[tuple[str, str]] = set()
        for source in sorted(graph):
            for target, weight in sorted(graph[source].items()):
                if source == target:
                    continue
                if (source, target) in handled:
                    continue
                reverse = graph[target].get(source)
                paired = reverse == weight
                handled.add((source, target))
                if paired:
                    handled.add((target, source))
                x1, y1 = xy[source]
                x2, y2 = xy[target]
                dx, dy = x2 - x1, y2 - y1
                length = max(1, math.hypot(dx, dy))
                nx, ny = dx / length, dy / length
                offset = 0 if paired or reverse is None else 7
                px, py = -ny * offset, nx * offset
                highlighted = ((source, target) in path_edges or
                               (paired and (target, source) in path_edges))
                active = active_edge == (source, target) or (paired and active_edge == (target, source))
                color = AMBER if highlighted else CYAN if active else EDGE
                canvas.create_line(x1 + nx * 22 + px, y1 + ny * 22 + py,
                                   x2 - nx * 22 + px, y2 - ny * 22 + py,
                                   fill=color, width=3.5 if highlighted else 2.8 if active else 1.6,
                                   arrow=tk.BOTH if paired else tk.LAST, arrowshape=(8, 9, 4))
                mx, my = (x1 + x2) / 2 + px - ny * 11, (y1 + y2) / 2 + py + nx * 11
                label = f"{weight:g}"
                half = max(13, len(label) * 3.6 + 5)
                canvas.create_rectangle(mx - half, my - 10, mx + half, my + 10,
                                        fill=CANVAS, outline="")
                canvas.create_text(mx, my, text=label, fill=INK,
                                   font=("Segoe UI", 9, "bold"))

        start, goal = self.start_var.get(), self.goal_var.get()
        visited = step.visited if step else frozenset()
        frontier = step.frontier if step else frozenset()
        for vertex in sorted(graph):
            x, y = xy[vertex]
            fill = PANEL
            if vertex in visited:
                fill = "#e8f0f2"
            if vertex in frontier:
                fill = "#dcebef"
            if step and vertex == step.current:
                fill = ACTIVE
            if final and result and vertex in result.path:
                fill = "#dceff1"
            outline = GREEN if vertex == start else RED if vertex == goal else "#88a0a8"
            if vertex == start and vertex == goal:
                outline = AMBER
            canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=fill,
                               outline=outline, width=2.5 if vertex in (start, goal) else 1.5)
            canvas.create_text(x, y, text=vertex, fill=INK,
                               font=("Segoe UI", 10, "bold"))
            if vertex == start:
                canvas.create_text(x, y - 32, text="AWAL", fill=GREEN,
                                   font=("Segoe UI", 8, "bold"))
            if vertex == goal:
                canvas.create_text(x, y + 32, text="TUJUAN", fill=RED,
                                   font=("Segoe UI", 8, "bold"))
        maximum = self._max_position()
        self.setting_progress = True
        self.progress_var.set(self.position)
        self.setting_progress = False
        self.step_var.set(f"{self.position}/{maximum}")
        if step:
            self.detail_var.set(step.description)
        elif final and result:
            self.detail_var.set("Jalur terbaik ditandai biru. Tekan Putar untuk melihat proses pencarian.")
        elif self.algorithm_var.get() in self.errors:
            self.detail_var.set(self.errors[self.algorithm_var.get()])
        else:
            self.detail_var.set("Belum ada langkah yang ditampilkan.")

    def _drag_start(self, event: tk.Event) -> None:
        width = max(self.canvas.winfo_width(), 400)
        height = max(self.canvas.winfo_height(), 350)
        for vertex, (nx, ny) in self.positions.items():
            x, y = 45 + nx * (width - 90), 40 + ny * (height - 80)
            if math.hypot(event.x - x, event.y - y) <= 25:
                self.dragged = vertex
                return

    def _drag_move(self, event: tk.Event) -> None:
        if self.dragged is None:
            return
        width = max(self.canvas.winfo_width(), 400)
        height = max(self.canvas.winfo_height(), 350)
        self.positions[self.dragged] = (
            min(0.96, max(0.04, (event.x - 45) / (width - 90))),
            min(0.96, max(0.04, (event.y - 40) / (height - 80))),
        )
        self.render()

    def _drag_end(self, _event: tk.Event) -> None:
        self.dragged = None

    def _on_progress(self, value: str) -> None:
        if self.setting_progress:
            return
        self.pause()
        self.position = min(self._max_position(), max(0, round(float(value))))
        self.render()

    def step_by(self, amount: int) -> None:
        self.pause()
        self.position = min(self._max_position(), max(0, self.position + amount))
        self.render()

    def reset(self) -> None:
        self.pause()
        self.position = 0
        self.render()

    def play_pause(self) -> None:
        if self.timer is not None:
            self.pause()
            return
        if self._max_position() == 0:
            return
        if self.position >= self._max_position():
            self.position = 0
        self.play_button.configure(text="Jeda")
        self._tick()

    def _tick(self) -> None:
        self.position = min(self._max_position(), self.position + 1)
        self.render()
        if self.position >= self._max_position():
            self.timer = None
            self.play_button.configure(text="Putar")
            return
        delay = {"Lambat": 900, "Sedang": 500, "Cepat": 180}.get(self.speed_var.get(), 500)
        self.timer = self.root.after(delay, self._tick)

    def pause(self) -> None:
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        if hasattr(self, "play_button"):
            self.play_button.configure(text="Putar")

    def _space(self, event: tk.Event) -> None:
        if event.widget in (self.root, self.canvas):
            self.play_pause()

    def _left(self, event: tk.Event) -> None:
        if event.widget in (self.root, self.canvas):
            self.step_by(-1)

    def _right(self, event: tk.Event) -> None:
        if event.widget in (self.root, self.canvas):
            self.step_by(1)

    def _close(self) -> None:
        self.pause()
        self.root.destroy()


def launch(source: GraphInput, file_path: Path) -> None:
    try:
        root = tk.Tk()
        GraphStudio(root, source, file_path)
        root.mainloop()
    except tk.TclError as exc:
        raise RuntimeError(f"Tkinter tidak dapat membuat jendela: {exc}") from exc
