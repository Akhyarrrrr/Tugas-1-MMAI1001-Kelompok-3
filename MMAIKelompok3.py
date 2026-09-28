"""Program utama Tugas 1 MMAI1001 Kelompok 3."""

from __future__ import annotations

import argparse
from pathlib import Path
from statistics import median
import sys

from shortest_path import GraphInput, NegativeCycleError, bellman_ford, dijkstra, has_negative_edge, read_graph


ROOT = Path(__file__).resolve().parent


def describe(result) -> None:
    print(f"Algoritma: {result.algorithm}")
    print(f"Jalur terpendek: {' -> '.join(result.path) if result.path else 'tidak ada'}")
    print(f"Bobot minimum: {result.cost:g}" if result.cost is not None else "Bobot minimum: tidak ada")
    print(f"Waktu runtime: {result.elapsed_ns / 1000:.2f} mikrodetik")
    print(f"Simpul diperiksa: {result.examined}; relaksasi: {result.relaxations}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Visualisasi dua algoritma jalur terpendek")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--cli", action="store_true", help="cetak hasil tanpa GUI")
    mode.add_argument("--benchmark", action="store_true", help="ukur median runtime kedua algoritma")
    parser.add_argument("file", nargs="?", type=Path, default=ROOT / "graf.txt",
                        help="file graf.txt; default adalah contoh resmi di folder program")
    parser.add_argument("--repetitions", type=int, default=1000,
                        help="pengulangan benchmark, default 1000")
    parser.add_argument("--start", help="simpul awal; default dari file graf")
    parser.add_argument("--goal", help="simpul tujuan; default dari file graf")
    args = parser.parse_args(argv)
    if args.repetitions < 1:
        parser.error("--repetitions harus positif")
    try:
        source = read_graph(args.file)
    except ValueError as exc:
        print(f"Kesalahan input: {exc}", file=sys.stderr)
        return 2
    start = args.start if args.start is not None else source.start
    goal = args.goal if args.goal is not None else source.goal
    if start not in source.graph or goal not in source.graph:
        print("Kesalahan input: simpul awal dan akhir harus ada dalam graf", file=sys.stderr)
        return 2

    if not args.cli and not args.benchmark:
        try:
            from graph_gui import launch
            launch(GraphInput(source.graph, start, goal), args.file)
        except (ImportError, RuntimeError) as exc:
            print(f"GUI tidak dapat dibuka: {exc}. Gunakan --cli untuk mode teks.", file=sys.stderr)
            return 2
        return 0

    print(f"Graf: {len(source.graph)} simpul; awal {start}; akhir {goal}")
    algorithms = []
    if has_negative_edge(source.graph):
        print("Dijkstra: tidak berlaku karena ada bobot negatif")
    else:
        algorithms.append(dijkstra)
    algorithms.append(bellman_ford)
    try:
        for algorithm in algorithms:
            if args.benchmark:
                for _ in range(100):
                    algorithm(source.graph, start, goal)
                timings = [algorithm(source.graph, start, goal).elapsed_ns
                           for _ in range(args.repetitions)]
            result = algorithm(source.graph, start, goal)
            describe(result)
            if args.benchmark:
                print(f"Median {args.repetitions} run setelah 100 pemanasan: "
                      f"{median(timings) / 1000:.2f} mikrodetik")
            print()
    except NegativeCycleError as exc:
        print(f"Jalur minimum tidak terdefinisi: {exc}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
