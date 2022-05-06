FROM python:3.9-buster

ENV POETRY_VERSION=1.1.12 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="/root/.cargo/bin:$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y time && rm -rf /var/lib/apt-lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY . /root/

WORKDIR /root/

RUN poetry install
RUN maturin build --release
RUN poetry add $(find ./target/wheels/ -name "*.whl")
