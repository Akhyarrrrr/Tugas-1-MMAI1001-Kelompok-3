"""Mencari jumlah langkah minimum untuk keluar dari maze."""

from collections import deque
from pathlib import Path
import sys


def parse_maze_text(text: str) -> tuple[list[list[int]], tuple[int, int]]:
    """Memvalidasi teks maze dan mengubah koordinat awal menjadi 0-based."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("file maze kosong")

    try:
        dimensions = [int(value) for value in lines[0].split()]
    except ValueError as exc:
        raise ValueError("N dan M harus berupa bilangan bulat") from exc

    if len(dimensions) != 2:
        raise ValueError("baris pertama harus berisi N dan M")

    rows, columns = dimensions
    if not (3 <= rows <= 12 and 3 <= columns <= 12):
        raise ValueError("N dan M harus berada dalam rentang 3 sampai 12")
    if len(lines) != rows + 2:
        raise ValueError(f"maze harus memiliki tepat {rows} baris")

    maze: list[list[int]] = []
    for row_number, line in enumerate(lines[1 : rows + 1], start=1):
        try:
            row = [int(value) for value in line.split()]
        except ValueError as exc:
            raise ValueError(f"baris maze ke-{row_number} harus berisi bilangan bulat") from exc
        if len(row) != columns:
            raise ValueError(
                f"baris maze ke-{row_number} harus memiliki tepat {columns} kolom"
            )
        if any(value not in (-1, 0) for value in row):
            raise ValueError("setiap petak maze harus bernilai -1 atau 0")
        maze.append(row)

    try:
        start_values = [int(value) for value in lines[-1].split()]
    except ValueError as exc:
        raise ValueError("A dan B harus berupa bilangan bulat") from exc

    if len(start_values) != 2:
        raise ValueError("baris terakhir harus berisi A dan B")

    start_row, start_column = start_values
    if not (1 <= start_row <= rows and 1 <= start_column <= columns):
        raise ValueError("koordinat awal berada di luar maze")

    start = (start_row - 1, start_column - 1)
    if maze[start[0]][start[1]] != 0:
        raise ValueError("petak awal harus berupa ruang yang dapat dilalui")

    return maze, start


def read_maze(path: str = "maze.txt") -> tuple[list[list[int]], tuple[int, int]]:
    """Membaca file maze dan mengubah koordinat awal menjadi 0-based."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"file tidak ditemukan: {path}") from exc
    except OSError as exc:
        raise ValueError(f"file tidak dapat dibaca: {path}") from exc
    return parse_maze_text(text)


def validate_maze_data(
    maze: object, start: object
) -> tuple[list[list[int]], tuple[int, int]]:
    """Memvalidasi maze dan koordinat 0-based dari request aplikasi."""
    if not isinstance(maze, list) or not 3 <= len(maze) <= 12:
        raise ValueError("maze harus memiliki 3 sampai 12 baris")
    if not all(isinstance(row, list) for row in maze):
        raise ValueError("setiap baris maze harus berupa daftar")

    columns = len(maze[0])
    if not 3 <= columns <= 12 or any(len(row) != columns for row in maze):
        raise ValueError("setiap baris maze harus memiliki 3 sampai 12 kolom yang sama")
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value not in (-1, 0)
        for row in maze
        for value in row
    ):
        raise ValueError("setiap petak maze harus bernilai -1 atau 0")
    if (
        not isinstance(start, list)
        or len(start) != 2
        or any(isinstance(value, bool) or not isinstance(value, int) for value in start)
    ):
        raise ValueError("titik awal harus berisi dua bilangan bulat")

    start_row, start_column = start
    if not (0 <= start_row < len(maze) and 0 <= start_column < columns):
        raise ValueError("titik awal berada di luar maze")
    if maze[start_row][start_column] != 0:
        raise ValueError("petak awal harus berupa ruang yang dapat dilalui")
    return [row[:] for row in maze], (start_row, start_column)


def search_maze(
    maze: list[list[int]],
    start: tuple[int, int],
    include_frontier: bool = False,
) -> tuple[list[dict[str, object]], list[tuple[int, int]]]:
    """Menjalankan BFS dan mengembalikan trace serta lintasan terpendek."""
    rows, columns = len(maze), len(maze[0])
    queue = deque([(start[0], start[1], 1)])
    visited = {start}
    parents: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    trace: list[dict[str, object]] = []

    while queue:
        row, column, distance = queue.popleft()
        position = (row, column)
        is_exit = row in (0, rows - 1) or column in (0, columns - 1)

        if not is_exit:
            for row_delta, column_delta in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                next_row = row + row_delta
                next_column = column + column_delta
                next_position = (next_row, next_column)
                if maze[next_row][next_column] == 0 and next_position not in visited:
                    visited.add(next_position)
                    parents[next_position] = position
                    queue.append((next_row, next_column, distance + 1))

        step: dict[str, object] = {
            "current": position,
            "distance": distance,
            "visitedCount": len(visited),
        }
        if include_frontier:
            step["frontier"] = [(item[0], item[1]) for item in queue]
        trace.append(step)

        if is_exit:
            path = []
            current: tuple[int, int] | None = position
            while current is not None:
                path.append(current)
                current = parents[current]
            return trace, list(reversed(path))

    return trace, []


def find_escape_path(
    maze: list[list[int]], start: tuple[int, int]
) -> tuple[list[tuple[tuple[int, int], int]], list[tuple[int, int]]]:
    """Mengembalikan urutan BFS dan lintasan terpendek menuju batas maze."""
    trace, path = search_maze(maze, start)
    visit_order = [
        (step["current"], step["distance"])
        for step in trace
    ]
    return visit_order, path


def minimum_escape_steps(maze: list[list[int]], start: tuple[int, int]) -> int:
    """Mengembalikan jumlah petak minimum hingga batas maze, atau -1."""
    _, path = find_escape_path(maze, start)
    return len(path) if path else -1


def main() -> int:
    try:
        maze, start = read_maze()
        print(minimum_escape_steps(maze, start))
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
