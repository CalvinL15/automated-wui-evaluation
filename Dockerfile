# Stage 1: Build the environment
FROM continuumio/miniconda3:latest AS builder

WORKDIR /backend

COPY backend/environment.yaml ./
RUN conda env create -f environment.yaml && \
    conda clean --all --yes && \
    rm -rf /opt/conda/pkgs/* /root/.cache/pip

# Stage 2: Build the image
FROM continuumio/miniconda3:latest

WORKDIR /backend

# Install Google Chrome and its dependencies
RUN apt-get update && apt-get install -y wget gnupg2 && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb --fix-missing && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the env from the builder
COPY --from=builder /opt/conda /opt/conda

COPY backend/ ./

ENV PYTHONPATH=/backend/src

WORKDIR /backend/src

RUN apt-get update \
  && apt-get -y install tesseract-ocr

EXPOSE 8000

CMD ["conda", "run", "--no-capture-output", "-n", "wui-auto-eval", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
