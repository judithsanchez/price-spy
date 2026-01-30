#!/bin/bash
# Wrapper to run commands either directly (if in Docker) or via docker compose (if on Host)

if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
    # Inside Docker container
    exec "$@"
else
    # On Host machine
    docker compose -f infrastructure/docker-compose.yml run --rm price-spy "$@"
fi
