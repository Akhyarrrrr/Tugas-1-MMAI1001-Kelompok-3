"""Cek yang dapat dijalankan tanpa membuka GUI: python -m unittest -v."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from shortest_path import (
    NegativeCycleError, bellman_ford, dijkstra, parse_graph_text, path_cost, read_graph,
)


ROOT = Path(__file__).resolve().parent


class ShortestPathTest(unittest.TestCase):
    def assert_both(self, graph, start, goal, expected):
        for algorithm in (dijkstra, bellman_ford):
            with self.subTest(algorithm=algorithm.__name__):
                result = algorithm(graph, start, goal, trace=True)
                self.assertEqual(result.cost, expected)
                self.assertEqual(result.path[0], start)
                self.assertEqual(result.path[-1], goal)
                self.assertEqual(path_cost(graph, result.path), expected)
                self.assertTrue(result.steps)

    def test_official_examples_v1_v15_and_v1_v10(self):
        source = read_graph(ROOT / "graf.txt")
        self.assert_both(source.graph, "V1", "V15", 505)
        self.assert_both(source.graph, "V1", "V10", 400)

    def test_official_example_b_to_h(self):
        source = parse_graph_text("""graf = {
            'A': {'B': 4, 'C': 2},
            'B': {'A': 4, 'C': 1, 'D': 5},
            'C': {'A': 2, 'B': 1, 'E': 10, 'F': 3},
            'D': {'B': 5, 'E': 2, 'G': 4},
            'E': {'C': 10, 'D': 2, 'F': 2, 'H': 3},
            'F': {'C': 3, 'E': 2, 'I': 11},
            'G': {'D': 4, 'H': 1},
            'H': {'E': 3, 'G': 1, 'I': 5, 'J': 7},
            'I': {'F': 11, 'H': 5, 'J': 2},
            'J': {'H': 7, 'I': 2}
        }
        B H
        """)
        self.assert_both(source.graph, source.start, source.goal, 9)

    def test_compact_bh_from_assignment(self):
        original = (ROOT / "contoh" / "graf_BH.txt").read_text(encoding="utf-8")
        source = parse_graph_text(original.replace("\nB H", "\nBH"))
        self.assertEqual((source.start, source.goal), ("B", "H"))
        ambiguous = "graph = {'B': {}, 'H': {}, 'BH': {}}\nBH"
        with self.assertRaises(ValueError):
            parse_graph_text(ambiguous)

    def test_rejects_unreadable_encoding(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "graf.txt"
            path.write_bytes(b"\xff\xfe")
            with self.assertRaisesRegex(ValueError, "tidak dapat dibaca"):
                read_graph(path)

    def test_rejects_duplicate_graph_entries(self):
        cases = (
            ("graph = {'A': {'B': 2}, 'A': {}, 'B': {}}\nA B", "simpul"),
            ("graph = {'A': {'B': 2, 'B': 9}, 'B': {}}\nA B", "sisi"),
        )
        for text, entry in cases:
            with self.subTest(entry=entry), self.assertRaisesRegex(ValueError, entry):
                parse_graph_text(text)

    def test_unreachable_and_directed_edges(self):
        graph = {"A": {"B": 3}, "B": {}, "C": {"A": 1}}
        for algorithm in (dijkstra, bellman_ford):
            result = algorithm(graph, "A", "C")
            self.assertEqual(result.path, ())
            self.assertIsNone(result.cost)

    def test_same_start_and_goal(self):
        graph = {"A": {"B": 2}, "B": {}}
        for algorithm in (dijkstra, bellman_ford):
            result = algorithm(graph, "A", "A")
            self.assertEqual(result.path, ("A",))
            self.assertEqual(result.cost, 0)

    def test_tied_optima(self):
        graph = {"A": {"B": 1, "C": 1}, "B": {"D": 2},
                 "C": {"D": 2}, "D": {}}
        self.assert_both(graph, "A", "D", 3)

    def test_negative_weight_and_cycle_reaching_goal(self):
        graph = {"A": {"B": 2, "C": 5}, "B": {"C": -4}, "C": {}}
        with self.assertRaisesRegex(ValueError, "Dijkstra"):
            dijkstra(graph, "A", "C")
        result = bellman_ford(graph, "A", "C")
        self.assertEqual(result.path, ("A", "B", "C"))
        self.assertEqual(result.cost, -2)
        cycle = {"A": {"B": 1}, "B": {"C": -3}, "C": {"B": 1, "D": 2}, "D": {}}
        with self.assertRaises(NegativeCycleError):
            bellman_ford(cycle, "A", "D")

    def test_negative_cycle_not_reaching_goal(self):
        graph = {"A": {"B": 1, "D": 4}, "B": {"C": -3},
                 "C": {"B": 1}, "D": {}}
        result = bellman_ford(graph, "A", "D")
        self.assertEqual(result.cost, 4)
        self.assertEqual(result.path, ("A", "D"))

    def test_rejects_unsafe_or_incomplete_input(self):
        invalid = (
            "graph = __import__('os').system('echo bad')\nA B",
            "graph = {'A': {'B': 1}}\nA B",
            "graph = {'A': {'B': True}, 'B': {}}\nA B",
            "graph = {'A': {}, 'B': {}}\nA",
            "graph = {'A': {}, 'B': {}}\nA C",
        )
        for text in invalid:
            with self.subTest(text=text[:35]), self.assertRaises(ValueError):
                parse_graph_text(text)


if __name__ == "__main__":
    unittest.main()
