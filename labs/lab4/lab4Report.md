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
5. Отсутствие параллельных окружений

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

Данный пункт подразумевает более серьезный подход к разделению CI/CD на различные шаги для разных веток. Например: 
 - для ветки `DEV` - добавить автоматические тесты,
 - для ветки `QA` - тесты и автоматический билд на тестовом сервере при пуше на ветку,
 - для ветки `MASTER` - тесты, билд на проде при условии релиза или аппрува от конкретного пользователя (также часто делают билд для Master ветки только через ручное нажатие на кнопку билда).


### Дополнительные плохие практики

Для более сложных и реальных проектов существует также несколько плохих практик, которые можно отразить в CI/CD файле:

 - Неправильная конфигурация зависимостей сервисов (при микросервисной архитектуре или, например, при запуске БД для проекта)
 - Отсутствие контроля за потреблением (например, ненастроенные лимиты на потребление CPU, RAM у контейнеров)
 - Отсутствие алертов и системы мониторинга (неактуально для Github Actions, так как автоматически прилетают уведомления на неудачный билд)

### Исправление плохих практик

Для исправления плохих практик был выбран модульный подход для построения CI/CD. Сначала были созданы два workflow файла, которые изолировали шаги теста и деплоя приложения:

 - `deploy-workflow.yml` - файл для деплоя приложения на DockerHub, который принимает на вход название образа (нужно, чтобы разделять версии приложения на тест и прод)

```yml
name: Push to DockerHub

on:
  workflow_call:
    inputs:
      image-name:
        required: true
        type: string

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ vars.DOCKER_USERNAME }} 
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          platforms: linux/amd64,linux/arm64
          push: true
          file: ./labs/lab4/Dockerfile
          tags: ${{ vars.DOCKER_USERNAME }}/${{ inputs.image-name }}:latest
```

 - `tests-workflow.yml` - файл для тестирования приложения, без каких-либо входных переменных, нужен, как зависимость для проверки работоспособности перед деплоем

```yml
name: Run app tests

on:
  workflow_call:


jobs:
  tests:
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
```

Далее, шаги из этих файлов можно переиспользовать для уже самих Github Actions:

 - `cicd_dev.yml` - файл CI/CD для ветки DEV - на данной ветке собираются все фичи, которые находятся в активном процессе разработки, поэтому для них необходимо прогонять тесты при каждом пуше нового кода

```yml
name: Push to DockerHub
on:
  push:
    branches:
        - dev
jobs:
  run_tests:
    uses: crawlic-stud/itmo-ict-clouds-labs-boysFromK34212/.github/workflows/tests-workflow.yml@main
```

 - `cicd_qa.yml` - файл CI/CD для ветки QA - на данной ветке собираются тестовые версии приложения, которые собираются на тестовом сервере, и соответственно проверяются все новые фичи перед тем, как выпуститься в прод

```yml
name: Push to DockerHub
on:
  push:
    branches:
        - qa
jobs:
  run_tests:
    uses: crawlic-stud/itmo-ict-clouds-labs-boysFromK34212/.github/workflows/tests-workflow.yml@main

  build:
    needs: run_tests 
    uses: crawlic-stud/itmo-ict-clouds-labs-boysFromK34212/.github/workflows/deploy-workflow.yml@main
    with:
      image-name: itmo-ict-cloud-lab4-qa
    secrets: inherit
```
> [!NOTE]
> В данном файле мы передаем названия изображения для докер образа, чтобы отличать версии приложения в DockerHub (в реальной жизни, скорее всего, это будет билд на тестовом сервере)

 - `cicd_master.yml` - файл CI/CD для ветки MASTER - на данной ветке хранятся все стабильные версии приложения, поэтому сборка запускается только при релизе, а также собирается на прод сервере 

```yml
name: Push to DockerHub
on:
  release:
    types: [published]
    branches:
        - main
jobs:
  run_tests:
    uses: crawlic-stud/itmo-ict-clouds-labs-boysFromK34212/.github/workflows/tests-workflow.yml@main

  build:
    needs: run_tests 
    uses: crawlic-stud/itmo-ict-clouds-labs-boysFromK34212/.github/workflows/deploy-workflow.yml@main
    with:
      image-name: itmo-ict-cloud-lab4-master
    secrets: inherit
```

> [!NOTE]
> Данный файл отличается от предыдущего измененным названием триггером для запуска, а также image для DockerHub (опять же, в реальности это будет сборка на прод сервере) 


### Тестирование CI/CD

После написания всех файлов, создания веток QA и DEV - заработали Github Actions при пушах на `QA` и `DEV`, а также при релизе на `MASTER`:
![image](https://github.com/user-attachments/assets/ef8686d8-31a8-43bf-b95e-fd0f0ca6cb0b)

А также, образы проекта были автоматически залиты на DockerHub:
![image](https://github.com/user-attachments/assets/75fe5abc-ede2-458f-a811-42d6ad9ad1f3)



## Выводы

Таким образом, благодаря систематическому подходу в создании файлов для CI/CD были исправлены следующие плохие практики:
1. Запуск на всех ветках был заменен на раздельные файлы для каждой из веток
2. Сборка без привязки к тестам была изменена на сборку с привязкой к тестам через инструкцию `needs`
3. Хардкод секретных переменных был заменен на секреты и переменные от Github Actions
4. Логгирование переменных окружения в консоли было удалено (также, предотвращено стандартной защитой от Github)
5. Были созданы параллельные окружения, которые отвечают за разные стадии проекта - `MASTER`, `QA` и `DEV`, у которых значительно отличаются процессы CI/CD  

Помимо этого, процессы workflow были разделены на отдельные файлы, что упрощает поддержку пайплайна в будущем. А также были рассмотрены дополнительные плохие практики, которые можно будет избежать при дальнейшем развитии проекта.
