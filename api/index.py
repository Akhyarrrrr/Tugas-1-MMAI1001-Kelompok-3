"""Adapter HTTP Vercel untuk Maze BFS Studio."""

from pathlib import Path

from flask import Flask, jsonify, request

from maze import parse_maze_text, read_maze, search_maze, validate_maze_data


ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify(error="request terlalu besar"), 413


@app.get("/api/maze")
def get_maze():
    try:
        maze, start = read_maze(str(ROOT / "maze.txt"))
        return jsonify(maze=maze, start=start)
    except ValueError as exc:
        return jsonify(error=str(exc)), 500


@app.post("/api/parse")
def parse_maze():
    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
            raise ValueError("teks maze tidak ditemukan")
        maze, start = parse_maze_text(payload["text"])
        return jsonify(maze=maze, start=start)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400


@app.post("/api/search")
def run_search():
    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            raise ValueError("request harus berupa objek JSON")
        maze, start = validate_maze_data(payload.get("maze"), payload.get("start"))
        trace, path = search_maze(maze, start, include_frontier=True)
        return jsonify(trace=trace, path=path, minimumSteps=len(path) if path else -1)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
