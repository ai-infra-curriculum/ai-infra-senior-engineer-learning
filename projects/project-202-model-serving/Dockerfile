FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y python3.10 python3-pip

# Install TensorRT
# TODO: Add TensorRT installation

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY src/ ./src/

CMD ["python3", "-m", "uvicorn", "src.serving.main:app", "--host", "0.0.0.0", "--port", "8000"]
