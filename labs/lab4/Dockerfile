FROM python:3.11-slim

RUN cd labs/lab4

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /app

COPY . .

CMD uvicorn app:app