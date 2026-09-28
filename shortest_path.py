"""Pembacaan graf dan dua algoritma jalur terpendek untuk Tugas 1 MMAI1001.

Graf berarah mengikuti daftar tetangga di graf.txt. Sisi balik hanya ada bila
ditulis tersendiri. Modul ini tidak membutuhkan antarmuka grafis.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import heapq
import math
from pathlib import Path
from time import perf_counter_ns


Graph = dict[str, dict[str, int | float]]


@dataclass(frozen=True)
class GraphInput:
    graph: Graph
    start: str
    goal: str


@dataclass(frozen=True)
class SearchStep:
    description: str
    current: str | None
    edge: tuple[str, str] | None
    visited: frozenset[str]
    frontier: frozenset[str]


@dataclass(frozen=True)
class SearchResult:
    algorithm: str
    path: tuple[str, ...]
    cost: int | float | None
    elapsed_ns: int
    examined: int
    relaxations: int
    steps: tuple[SearchStep, ...]


class NegativeCycleError(ValueError):
    """Siklus negatif terjangkau dapat menuju simpul tujuan."""


def parse_graph_text(text: str) -> GraphInput:
    """Baca satu assignment literal dan dua nama simpul pada baris terakhir.

    ``ast.literal_eval`` menerima angka dan dictionary Python tanpa mengeksekusi
    ekspresi atau pemanggilan fungsi di dalam file input.
    """
    lines = text.lstrip("\ufeff").splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) < 2:
        raise ValueError("graf.txt harus berisi dictionary dan baris simpul awal akhir")
    endpoint_line = lines[-1].strip()
    source = "\n".join(lines[:-1]).strip()
    try:
        module = ast.parse(source, mode="exec")
        if (
            len(module.body) != 1
            or not isinstance(module.body[0], ast.Assign)
            or len(module.body[0].targets) != 1
            or not isinstance(module.body[0].targets[0], ast.Name)
            or module.body[0].targets[0].id not in {"graph", "graf"}
        ):
            raise ValueError("isi graf harus berupa satu assignment graph = {...} atau graf = {...}")
        raw = ast.literal_eval(module.body[0].value)
    except (SyntaxError, TypeError, MemoryError, RecursionError) as exc:
        raise ValueError("struktur dictionary graf tidak valid") from exc
    if not isinstance(raw, dict) or not raw:
        raise ValueError("graf harus berupa dictionary yang tidak kosong")

    vertices = set(raw)
    if any(
        not isinstance(vertex, str)
        or not vertex
        or any(char.isspace() for char in vertex)
        for vertex in vertices
    ):
        raise ValueError("nama simpul harus berupa teks tidak kosong tanpa spasi")
    graph: Graph = {}
    for vertex, neighbors in raw.items():
        if not isinstance(neighbors, dict):
            raise ValueError(f"tetangga {vertex} harus berupa dictionary")
        graph[vertex] = {}
        for neighbor, weight in neighbors.items():
            if neighbor not in vertices:
                raise ValueError(f"simpul tujuan {neighbor!r} dari {vertex} belum dideklarasikan")
            if isinstance(weight, bool) or not isinstance(weight, (int, float)):
                raise ValueError(f"bobot {vertex} ke {neighbor} harus berupa angka")
            if isinstance(weight, float) and not math.isfinite(weight):
                raise ValueError(f"bobot {vertex} ke {neighbor} harus terhingga")
            graph[vertex][neighbor] = weight
    endpoints = endpoint_line.split()
    if (len(endpoints) == 1 and len(endpoint_line) == 2
            and endpoint_line not in graph
            and all(vertex in graph for vertex in endpoint_line)):
        # Contoh B-H pada soal menulis "BH" tanpa spasi.
        endpoints = list(endpoint_line)
    if len(endpoints) != 2:
        raise ValueError("baris terakhir harus berisi dua simpul dipisahkan spasi")
    start, goal = endpoints
    if start not in graph or goal not in graph:
        raise ValueError("simpul awal dan akhir harus ada dalam graf")
    return GraphInput(graph, start, goal)


def read_graph(path: str | Path) -> GraphInput:
    try:
        return parse_graph_text(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"file graf tidak dapat dibaca: {path}") from exc


def has_negative_edge(graph: Graph) -> bool:
    return any(weight < 0 for neighbors in graph.values() for weight in neighbors.values())


def _path(parent: dict[str, str | None], goal: str, count: int) -> tuple[str, ...]:
    if goal not in parent:
        return ()
    result = []
    node: str | None = goal
    while node is not None:
        result.append(node)
        if len(result) > count:
            raise NegativeCycleError("lintasan menuju tujuan memuat siklus negatif")
        node = parent[node]
    return tuple(reversed(result))


def dijkstra(graph: Graph, start: str, goal: str, *, trace: bool = False) -> SearchResult:
    """Dijkstra dengan heap; bobot sisi harus nonnegatif."""
    if has_negative_edge(graph):
        raise ValueError("Dijkstra tidak berlaku untuk graf dengan bobot negatif")
    begin = perf_counter_ns()
    distance: dict[str, int | float] = {start: 0}
    parent: dict[str, str | None] = {start: None}
    heap: list[tuple[int | float, str]] = [(0, start)]
    visited: set[str] = set()
    steps: list[SearchStep] = []
    relaxations = 0
    while heap:
        cost, node = heapq.heappop(heap)
        if node in visited or cost != distance[node]:
            continue
        visited.add(node)
        if trace:
            steps.append(SearchStep(f"Dijkstra menetapkan {node} dengan bobot {cost:g}", node, None,
                                    frozenset(visited), frozenset(distance.keys() - visited)))
        if node == goal:
            break
        for neighbor, weight in sorted(graph[node].items()):
            candidate = cost + weight
            if candidate < distance.get(neighbor, math.inf):
                distance[neighbor] = candidate
                parent[neighbor] = node
                heapq.heappush(heap, (candidate, neighbor))
                relaxations += 1
                if trace:
                    steps.append(SearchStep(
                        f"Relaksasi {node} ke {neighbor}: jarak sementara {candidate:g}",
                        node, (node, neighbor), frozenset(visited),
                        frozenset(distance.keys() - visited),
                    ))
    path = _path(parent, goal, len(graph))
    return SearchResult("Dijkstra", path, distance.get(goal), perf_counter_ns() - begin,
                        len(visited), relaxations, tuple(steps))


def bellman_ford(graph: Graph, start: str, goal: str, *, trace: bool = False) -> SearchResult:
    """Bellman–Ford dengan deteksi siklus negatif yang berpengaruh ke tujuan."""
    begin = perf_counter_ns()
    distance: dict[str, int | float] = {vertex: math.inf for vertex in graph}
    distance[start] = 0
    parent: dict[str, str | None] = {start: None}
    edges = [(source, target, weight) for source in sorted(graph)
             for target, weight in sorted(graph[source].items())]
    steps: list[SearchStep] = []
    relaxations = 0
    for iteration in range(1, len(graph)):
        updated: set[str] = set()
        for source, target, weight in edges:
            if distance[source] == math.inf:
                continue
            candidate = distance[source] + weight
            if candidate < distance[target]:
                distance[target] = candidate
                parent[target] = source
                updated.add(target)
                relaxations += 1
                if trace:
                    seen = frozenset(v for v, value in distance.items() if value < math.inf)
                    steps.append(SearchStep(
                        f"Iterasi {iteration}: {source} ke {target}, jarak {candidate:g}",
                        source, (source, target), seen, frozenset(updated),
                    ))
        if trace:
            seen = frozenset(v for v, value in distance.items() if value < math.inf)
            steps.append(SearchStep(f"Iterasi {iteration} selesai", None, None,
                                    seen, frozenset(updated)))
        if not updated:
            break

    affected = {target for source, target, weight in edges
                if distance[source] < math.inf and distance[source] + weight < distance[target]}
    if affected:
        stack = list(affected)
        while stack:
            node = stack.pop()
            for neighbor in graph[node]:
                if neighbor not in affected:
                    affected.add(neighbor)
                    stack.append(neighbor)
        if goal in affected:
            raise NegativeCycleError("siklus negatif dapat memengaruhi bobot ke tujuan")
    path = _path(parent, goal, len(graph))
    cost = None if distance[goal] == math.inf else distance[goal]
    examined = sum(value < math.inf for value in distance.values())
    return SearchResult("Bellman-Ford", path, cost, perf_counter_ns() - begin,
                        examined, relaxations, tuple(steps))


def path_cost(graph: Graph, path: tuple[str, ...]) -> int | float | None:
    """Hitung ulang bobot lintasan; berguna untuk verifikasi hasil."""
    if not path:
        return None
    return sum(graph[source][target] for source, target in zip(path, path[1:]))
