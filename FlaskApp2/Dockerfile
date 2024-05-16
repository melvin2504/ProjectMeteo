FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY main.py ./
COPY weather.py ./
COPY openai_utils.py ./
COPY google_cloud_utils.py ./
COPY config.py ./
COPY requirements.txt ./

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["main.py"]
