FROM python:3.11-slim

ARG FORGE_VERSION=1.1.1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV SKILL_FORGE_REPO_ROOT=/opt/skill-forge
ENV SKILL_FORGE_PROJECT_DIR=/workspace/project

LABEL org.opencontainers.image.title="skill-forge"
LABEL org.opencontainers.image.description="Containerized CLI for validating, rendering, and installing canonical skills"
LABEL org.opencontainers.image.version="${FORGE_VERSION}"

WORKDIR /opt/skill-forge

COPY pyproject.toml /opt/skill-forge/pyproject.toml
COPY src /opt/skill-forge/src
COPY canonical-skills /opt/skill-forge/canonical-skills
COPY docker/runtime-entrypoint.sh /usr/local/bin/skill-forge-container
COPY docker/runtime-shellrc /opt/skill-forge/docker/runtime-shellrc

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install . \
    && chmod +x /usr/local/bin/skill-forge-container

WORKDIR /workspace/project

ENTRYPOINT ["/usr/local/bin/skill-forge-container"]
