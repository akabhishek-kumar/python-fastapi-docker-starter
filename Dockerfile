# ── Stage 1: base image ──────────────────────────────────────────────────────
# We start from the official Python 3.11 slim image.
# "slim" = Debian-based but stripped of docs/tests (~50MB vs ~900MB for full).
FROM python:3.11-slim

# ── Working directory ─────────────────────────────────────────────────────────
# All subsequent commands run inside /app inside the container.
# The directory is created automatically if it doesn't exist.
WORKDIR /app

# ── Install dependencies FIRST (before copying app code) ─────────────────────
# Why this order? Docker builds in layers and caches each one.
# If we copy requirements.txt first and it hasn't changed,
# Docker reuses the cached "pip install" layer — much faster rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ─────────────────────────────────────────────────────
# Now copy everything else. This layer changes often (every code edit),
# but the pip install layer above is cached and skipped.
COPY . .

# ── Expose port ───────────────────────────────────────────────────────────────
# Documents which port the container listens on. Does NOT publish it —
# that's done in docker-compose with "ports: - 8000:8000".
EXPOSE 8000

# ── Start command ─────────────────────────────────────────────────────────────
# CMD is the default command when the container starts.
# --host 0.0.0.0  → listen on all interfaces inside container (required!)
#                   Without this, uvicorn binds to 127.0.0.1 and
#                   traffic from outside the container can't reach it.
# --port 8000     → match EXPOSE above
# No --reload     → reload is for dev only; wastes resources in containers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
