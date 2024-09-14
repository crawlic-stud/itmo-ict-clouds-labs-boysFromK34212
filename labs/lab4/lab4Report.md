# 4 лабораторная работа "Плохой и хороший CI/CD"

## Условие

1. Написать “плохой” CI/CD файл, который работает, но в нем есть не менее пяти “bad practices” по написанию CI/CD
2. Написать “хороший” CI/CD, в котором эти плохие практики исправлены
3. Описать каждую из плохих практик в плохом файле, почему она плохая и как в хорошем она была исправлена, как исправление повлияло на результат

## Ход работы

Для выполнения работы был выбран способ настройки CI/CD через Github Actions. Перед началом работы был написан небольшой API сервис, тесты для него, а также Dockerfile для запуска сервиса.

<details>

<summary>Сервис на FastAPI:</summary>

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}
```
</details>

<details>

<summary>Тесты для сервиса:</summary>

```python
from fastapi.testclient import TestClient
import pytest

from app import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

def test_response_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```
</details>

<details>
<summary>Dockerfile:</summary>

```Dockerfile
FROM python:3.11-slim

COPY labs/lab4/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /app

COPY labs/lab4/src .

CMD uvicorn app:app
```
</details>

</details>

### 1. Плохой CI/CD файл
