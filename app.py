"""Server lokal untuk Maze BFS Studio."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
import webbrowser

from maze import parse_maze_text, read_maze, search_maze, validate_maze_data


ROOT = Path(__file__).parent
WEB_ROOT = ROOT / "web"
MAX_REQUEST_SIZE = 128 * 1024
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
}


class MazeRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/api/maze":
            try:
                maze, start = read_maze(str(ROOT / "maze.txt"))
                self.send_json({"maze": maze, "start": start})
            except ValueError as exc:
                self.send_json({"error": str(exc)}, 500)
            return

        static = STATIC_FILES.get(self.path)
        if static is None:
            self.send_error(404)
            return
        filename, content_type = static
        content = (WEB_ROOT / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        if self.path not in ("/api/parse", "/api/search"):
            self.send_error(404)
            return
        try:
            payload = self.read_json()
            if self.path == "/api/parse":
                if not isinstance(payload.get("text"), str):
                    raise ValueError("teks maze tidak ditemukan")
                maze, start = parse_maze_text(payload["text"])
                self.send_json({"maze": maze, "start": start})
                return

            maze, start = validate_maze_data(payload.get("maze"), payload.get("start"))
            trace, path = search_maze(maze, start, include_frontier=True)
            self.send_json(
                {
                    "trace": trace,
                    "path": path,
                    "minimumSteps": len(path) if path else -1,
                }
            )
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, 400)

    def read_json(self) -> dict[str, object]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("ukuran request tidak valid") from exc
        if not 0 < length <= MAX_REQUEST_SIZE:
            raise ValueError("request kosong atau terlalu besar")
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request harus berupa objek JSON")
        return payload

    def send_json(self, payload: object, status: int = 200) -> None:
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(content)

    def send_security_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'",
        )

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), MazeRequestHandler)
    server.daemon_threads = True
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Maze BFS Studio berjalan di {url}")
    print("Tutup jendela terminal atau tekan Ctrl+C untuk menghentikan server.")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.4, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
