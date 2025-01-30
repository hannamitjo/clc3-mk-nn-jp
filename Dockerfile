FROM python:3.11-slim

RUN apt-get update && apt-get install -y
RUN pip install -U streamlit minio

COPY ./src/ .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py"]