FROM python:3.12-slim

WORKDIR /app

COPY server.py pyproject.toml ./

CMD ["python", "-u", "server.py"]
