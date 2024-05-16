FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY ./main.py ./
COPY ./weather.py ./  # Ensure weather.py is copied
COPY ./openai_utils.py ./  # Ensure any other necessary Python files are copied
COPY ./google_cloud_utils.py ./  # Ensure any other necessary Python files are copied
COPY ./config.py ./  # Ensure config.py is copied if it is used
COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt


ENTRYPOINT ["python"]
CMD ["main.py"]
