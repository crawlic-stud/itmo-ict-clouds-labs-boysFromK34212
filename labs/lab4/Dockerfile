FROM python:3.11-slim

COPY labs/lab4/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /app

COPY labs/lab4/src .

CMD uvicorn app:app