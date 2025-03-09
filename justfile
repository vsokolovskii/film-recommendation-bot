default:
    @just --list --unsorted

# Start uvicorn server
server:
    @uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --env-file .env

# Start ollama server
ollama arg="":
    @ollama pull {{ arg }}

test:
    @uv run pytest -vv

lint:
    @just --fmt --unstable
    @ruff check --fix
    @ruff format

profile:
    @locust -f tests/locustfile.py --host=http://localhost:8080 --web-port 8086 -u 100 -r 5 -t 1m
