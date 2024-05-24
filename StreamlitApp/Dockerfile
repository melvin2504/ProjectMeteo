FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

# Expose the port that Streamlit runs on
EXPOSE 8501

# Set the environment variable PORT
ENV PORT 8080

# Start the Streamlit app
CMD ["streamlit", "run", "--server.port", "8080", "streamlit_app.py"]
