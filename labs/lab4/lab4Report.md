# 4 лабораторная работа "Плохой и хороший CI/CD"

## Задание

1. Написать “плохой” CI/CD файл, который работает, но в нем есть не менее пяти “bad practices” по написанию CI/CD
2. Написать “хороший” CI/CD, в котором эти плохие практики исправлены
3. Описать каждую из плохих практик в плохом файле, почему она плохая и как в хорошем она была исправлена, как исправление повлияло на результат

## Ход работы

Для выполнения работы был выбран способ настройки CI/CD через Github Actions. Перед началом работы был написан небольшой API сервис, тесты для него, а также Dockerfile для запуска сервиса:

<details>

<summary>Сервис на FastAPI</summary>

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}
```
</details>

<details>

<summary>Тесты для сервиса</summary>

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
<summary>Dockerfile</summary>

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

### Плохой CI/CD файл

В качестве плохих практик для CI/CD пайплайна были выбраны следующие:

1. Запуск всех билдов и тестов при пуше на любую ветку
2. Запуск проекта без привязки к тестам, то есть возможный запуск при условии, что тесты будут провалены
3. Хардкод секретных переменных прямо в файле конфигурации
4. Логгирование переменных окружения в консоли
5. Отсутствие разделения "сред", то есть отдельная настройка окружения под разные ветки и ивенты 

Для реализации были выбраны Github Actions, а в качестве конечного пункта назначения для билда был выбран DockerHub, куда отправляется собранное изображение для последней версии проекта. "Плохой" файл был реализован в стандартном YML формате согласно документации github и docker и выглядел следующим образом:

```yml
name: Push to DockerHub
on:
 # its not good to run ci/cd on every push to every branch
 push:
  branches:
      - '*'
jobs:
  run_tests:
    runs-on: [ubuntu-latest]
    steps:
      - uses: actions/checkout@master
      - uses: actions/setup-python@v1
        with:
          python-version: '3.11'
          architecture: 'x64'
      - name: Install requirements
        run: pip install -r ./labs/lab4/requirements.txt
      - name: Run tests
        run: pytest ./labs/lab4/src/tests.py

  build:
    # no dependency so it wont fail when tests fail
    runs-on: ubuntu-latest
    steps:
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          # hardcoded secrets
          username: username
          password: password
      
      # showing secrets in console
      - name: Check password 
        run: echo ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ vars.DOCKER_USERNAME }}/${{ github.event.repository.name }}:latest
          
```

### Разбор плохих практик
 
Разберем каждый пункт по отдельности:

1. `Запуск на всех ветках при каждом пуше:`

```yml
on:
 push:
  branches:
      - '*'
```

Это является плохой практикой, так как практически для любого проекта, даже самого маленького - необходимо разделение разработки на разные стадии. Чаще всего, это делается через разные ветки, которые потом мерджатся в основную, либо, как альтернатива настроить другие ивенты, например Github предоставляет возможность запускать CI/CD каждый раз, когда делается новый релиз.

2. `Билд без привязки к тестам:`

```yml
build:
    # no dependency so it wont fail when tests fail
    runs-on: ubuntu-latest
    steps:
```

Данный пункт является плохой практикой, так как практически в любом более менее серьезном проекте есть автоматические тесты, которые проверяют работоспособность функционала кода. Данные тесты запускаются перед основным билдом проекта, и если они фейлят - то билд должен отменяться, то есть "плохой" код не должен попадать к конечным пользователям.

3. `Хардкод секретов:`

```yml
steps:
  - name: Login to Docker Hub
    uses: docker/login-action@v3
    with:
      # hardcoded secrets
      username: username
      password: password
```

Это является вполне очевидной плохой практикой для любого разработчика. В любом месте, где нужны секретные переменные - необходимо передавать их через переменные окружения непосредственно там, где запускается конечный код. Передавать их в файлах конфигурации или в коде проекта крайне небезопасно и может привести к увольнению с рабочего места.

4. `Логгирование секретов`

```yml
- name: Check password 
    run: echo ${{ secrets.DOCKERHUB_TOKEN }}
```

Данный пункт явлется плохой практикой, так как опять же компрометирует секретные переменные, хоть и не так очевидно. Например, если у кого-то появится каким-то чудесным образом доступ к логам CI/CD, то такое логгирование поможет нарушителям нанести вред, после которого уже можно и не восстановиться. 

> [!NOTE]
> Важно заметить, что Github автоматически маскирует вывод любых переменных, которые сохранены в Secrets (секретных переменных), однако если совершить ошибку и поместить секретную переменную в Variables, то тогда ее логггирование не будет скрыто: 

![image](https://github.com/user-attachments/assets/e05926e4-61e8-4856-aeaa-4992ea0ec993)

5. `Отсутствие разделения на среды разработки:`

Данный пункт подразумевает более серьезный подход к разделению CI/CD на различные шаги для разных веток. Например, для ветки DEV - добавить автоматические тесты, для ветки QA - тесты и автоматический билд на тестовом сервере при пуше на ветку, для ветки MASTER - тесты, билд на проде при условии релиза или аппрува от конкретного пользователя (также часто делают билд для Master ветки только через ручное нажатие на кнопку билда).


