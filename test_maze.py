"""Pengujian solusi Tugas 1 Maze."""

from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import textwrap
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json

from api.index import app as vercel_app
from app import MazeRequestHandler
from http.server import ThreadingHTTPServer
from maze import (
    find_escape_path,
    minimum_escape_steps,
    read_maze,
    search_maze,
    validate_maze_data,
)


SAMPLE_1 = """
8 10
-1 -1 -1 -1 -1 -1 -1 -1 -1 -1
-1 0 0 0 0 0 -1 0 0 0
-1 0 0 -1 -1 0 0 0 -1 -1
-1 -1 0 0 -1 -1 -1 0 0 -1
-1 0 0 0 -1 0 -1 -1 -1 -1
-1 0 -1 0 -1 0 -1 0 0 -1
-1 0 -1 0 0 0 0 0 -1 -1
-1 -1 -1 -1 -1 -1 -1 -1 -1 -1
7 5
"""

SAMPLE_2 = """
8 10
-1 0 -1 -1 -1 -1 -1 -1 -1 -1
-1 0 0 0 0 0 -1 0 0 0
-1 0 0 -1 -1 0 0 0 -1 -1
-1 -1 0 0 -1 -1 -1 0 0 -1
-1 0 0 0 -1 0 -1 -1 -1 -1
-1 0 -1 0 -1 0 -1 0 0 -1
-1 0 -1 0 0 0 0 0 -1 -1
-1 -1 -1 -1 -1 -1 -1 -1 -1 -1
7 5
"""

SAMPLE_3 = """
8 10
-1 -1 -1 -1 -1 -1 -1 -1 -1 -1
-1 0 0 0 0 0 -1 0 0 -1
-1 0 0 -1 -1 0 0 0 -1 -1
-1 -1 0 0 -1 -1 -1 0 0 -1
-1 0 0 0 -1 0 -1 -1 -1 -1
-1 0 -1 0 -1 0 -1 0 0 -1
-1 0 -1 0 0 0 0 0 -1 -1
-1 -1 -1 -1 -1 -1 -1 -1 -1 -1
7 5
"""


class MazeTest(unittest.TestCase):
    def solve_text(self, content: str) -> int:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "maze.txt"
            path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
            maze, start = read_maze(str(path))
        return minimum_escape_steps(maze, start)

    def test_official_examples(self) -> None:
        for content, expected in ((SAMPLE_1, 17), (SAMPLE_2, 10), (SAMPLE_3, -1)):
            with self.subTest(expected=expected):
                self.assertEqual(self.solve_text(content), expected)

    def test_start_on_boundary_counts_as_one_step(self) -> None:
        maze = [[-1, 0, -1], [-1, 0, -1], [-1, -1, -1]]
        self.assertEqual(minimum_escape_steps(maze, (0, 1)), 1)

    def test_chooses_nearest_of_multiple_exits_with_cycles(self) -> None:
        maze = [
            [-1, -1, 0, -1, -1],
            [-1, 0, 0, 0, -1],
            [0, 0, 0, 0, 0],
            [-1, 0, 0, 0, -1],
            [-1, -1, -1, 0, -1],
        ]
        self.assertEqual(minimum_escape_steps(maze, (3, 2)), 3)

    def test_visualization_path_is_contiguous_and_reaches_boundary(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "maze.txt"
            path.write_text(textwrap.dedent(SAMPLE_1).strip() + "\n", encoding="utf-8")
            maze, start = read_maze(str(path))
        visit_order, escape_path = find_escape_path(maze, start)

        self.assertEqual(len(escape_path), 17)
        self.assertEqual(escape_path[0], start)
        self.assertTrue(visit_order)
        self.assertTrue(
            escape_path[-1][0] in (0, len(maze) - 1)
            or escape_path[-1][1] in (0, len(maze[0]) - 1)
        )
        for current, following in zip(escape_path, escape_path[1:]):
            self.assertEqual(abs(current[0] - following[0]) + abs(current[1] - following[1]), 1)

    def test_search_trace_contains_frontier_snapshots(self) -> None:
        maze = [[-1, 0, -1], [-1, 0, -1], [-1, 0, -1]]
        trace, path = search_maze(maze, (1, 1), include_frontier=True)
        self.assertEqual(len(path), 2)
        self.assertIn("frontier", trace[0])
        self.assertEqual(trace[-1]["distance"], 2)

    def test_rejects_invalid_api_maze(self) -> None:
        with self.assertRaises(ValueError):
            validate_maze_data([[0, 0, 0], [0, True, 0], [0, 0, 0]], [1, 1])

    def test_rejects_missing_file(self) -> None:
        with self.assertRaisesRegex(ValueError, "file tidak ditemukan"):
            read_maze("file-yang-tidak-ada.txt")

    def test_rejects_invalid_input(self) -> None:
        cases = {
            "wrong row count": "3 3\n0 0 0\n0 0 0\n2 2\n",
            "wrong column count": "3 3\n0 0 0\n0 0\n0 0 0\n2 2\n",
            "invalid cell": "3 3\n0 0 0\n0 2 0\n0 0 0\n2 2\n",
            "coordinate outside": "3 3\n0 0 0\n0 0 0\n0 0 0\n4 2\n",
            "start on wall": "3 3\n0 0 0\n0 -1 0\n0 0 0\n2 2\n",
        }
        for name, content in cases.items():
            with self.subTest(name=name), TemporaryDirectory() as directory:
                path = Path(directory) / "maze.txt"
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_maze(str(path))


class MazeApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), MazeRequestHandler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request_json(self, path: str, payload: dict | None = None) -> tuple[int, dict]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"} if data else {},
        )
        try:
            with urlopen(request, timeout=2) as response:
                return response.status, json.loads(response.read())
        except HTTPError as exc:
            try:
                return exc.code, json.loads(exc.read())
            finally:
                exc.close()

    def test_default_maze_search_api(self) -> None:
        status, source = self.request_json("/api/maze")
        self.assertEqual(status, 200)
        status, result = self.request_json("/api/search", source)
        self.assertEqual(status, 200)
        self.assertEqual(result["minimumSteps"], 17)
        self.assertTrue(result["trace"][0]["frontier"])

    def test_api_rejects_bad_payload_and_unknown_route(self) -> None:
        status, result = self.request_json("/api/search", {"maze": [], "start": [0, 0]})
        self.assertEqual(status, 400)
        self.assertIn("error", result)
        with self.assertRaises(HTTPError) as context:
            urlopen(self.base_url + "/../maze.py", timeout=2)
        self.assertEqual(context.exception.code, 404)
        context.exception.close()


class VercelApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = vercel_app.test_client()

    def test_default_maze_and_search(self) -> None:
        source = self.client.get("/api/maze")
        self.assertEqual(source.status_code, 200)
        result = self.client.post("/api/search", json=source.get_json())
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.get_json()["minimumSteps"], 17)

    def test_serves_frontend_and_favicon(self) -> None:
        page = self.client.get("/")
        try:
            self.assertEqual(page.status_code, 200)
            self.assertIn(b"Maze BFS Studio", page.data)
        finally:
            page.close()
        icon = self.client.get("/favicon.svg")
        try:
            self.assertEqual(icon.status_code, 200)
            self.assertEqual(icon.mimetype, "image/svg+xml")
        finally:
            icon.close()

    def test_parse_and_invalid_payload(self) -> None:
        parsed = self.client.post("/api/parse", json={"text": textwrap.dedent(SAMPLE_2).strip()})
        self.assertEqual(parsed.status_code, 200)
        invalid = self.client.post("/api/search", json={"maze": [], "start": [0, 0]})
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("error", invalid.get_json())

    def test_rejects_oversized_request(self) -> None:
        response = self.client.post(
            "/api/parse",
            data=json.dumps({"text": "0" * (129 * 1024)}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.get_json()["error"], "request terlalu besar")


if __name__ == "__main__":
    unittest.main()
