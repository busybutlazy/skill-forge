FROM python:3.11-slim

ARG TOOLKIT_VERSION=0.3.0

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV SKILL_TOOLKIT_REPO_ROOT=/opt/skill-toolkit
ENV SKILL_TOOLKIT_PROJECT_DIR=/workspace/project
ENV SKILL_TOOLKIT_OUTPUT_DIR=/workspace/output

LABEL org.opencontainers.image.title="skill-toolkit"
LABEL org.opencontainers.image.description="Containerized CLI for validating, rendering, and installing canonical skills"
LABEL org.opencontainers.image.version="${TOOLKIT_VERSION}"

WORKDIR /opt/skill-toolkit

COPY pyproject.toml /opt/skill-toolkit/pyproject.toml
COPY src /opt/skill-toolkit/src
COPY canonical-skills /opt/skill-toolkit/canonical-skills
COPY docker/runtime-entrypoint.sh /usr/local/bin/skill-toolkit-container
COPY docker/runtime-shellrc /opt/skill-toolkit/docker/runtime-shellrc

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install . \
    && chmod +x /usr/local/bin/skill-toolkit-container

WORKDIR /workspace/project

ENTRYPOINT ["/usr/local/bin/skill-toolkit-container"]
