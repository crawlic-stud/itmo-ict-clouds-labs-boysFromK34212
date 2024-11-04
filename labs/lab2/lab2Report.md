# 3 лабораторная работа "Локальное развертывание сервиса в Kubernetes с использованием Minikube"

## Задание

Поднять kubernetes кластер локально (например minikube), в нём развернуть свой сервис, используя 2-3 ресурса kubernetes. 
В идеале разворачивать кодом из yaml файлов одной командой запуска. Показать работоспособность сервиса.

## Ход работы

Для выполнения данного задания необходимы следущие инструменты:  
* Minikube (инструмент, который позволит запускать локальный кластер Kubernetes на компьютере)
* kubectl (он нужен для взаимодействия с кластером)

# Запуск Minikube  

На моем компьютере уже установлен minikube и можно его запустить командой ```minikube start```.
При запуске команды minikube start можно не указывать флаг ```--vm-driver=```, 
потому что Minikube автоматически выбирает подходящий драйвер виртуализации на основе операционной системы (в нашем случае ```--vm-driver=virtualbox```)

<p align="center"><img src="https://github.com/user-attachments/assets/a715e70e-b8ae-4174-aa1c-8d3f66b165e5" width=700></p>

Как можно видеть новая машина не создается, используется уже существующая, она прекрасно подойдет для установленных целей.

<p align="center"><img src="https://github.com/user-attachments/assets/0740b7eb-5a08-4150-89e7-7a1ec5c8b309" width=700></p>

При запуске minikube указывает на некоторые дополнения, что некоторые функции дашборда требуют дополнения metrics-server
и kubectl не установлен или не доступен системе
Как раз таки kubectl обязательно установим, он нужен для взаимодействия с будущим кластером

Пользуясь <a href="https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/">официальной инструкцией</a> установим его, дадим права на исполнение и перенесем в дирикторию к minikube

<p align="center"><img src="https://github.com/user-attachments/assets/e18337a4-7342-408c-aaaf-11e8f8b9e0e5" width=700></p>

<p align="center"><img src="https://github.com/user-attachments/assets/9567f3f4-8716-4cdf-95b3-fb3f0d970c43" width=700></p>

Команда ```minikube dashboard``` включает надстройку панели мониторинга и открывает прокси в веб-браузере по умолчанию. 
С ее помощью сможем создавать/проверять ресурсы Kubernetes на панели мониторинга, например такие как Deployment и Service.

# Создание простого веб-сервиса

<details>

<summary>Скрипт для запуска веб-приложения на Flask</summary>

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
```
</details>

<details>

<summary>Файл стилей для веб-страниц и шаблоны</summary>

```bash
user@user-HKFG-XX:~/ITMO/7-semestr/Cloud/itmo-ict-clouds-labs-boysFromK34212$ tree ./labs/lab3
./labs/lab3
├── app.py
├── deployment.yaml
├── deploy.sh
├── Dockerfile
├── report-lab3.md
├── requirements.txt
├── service.yaml
├── static
│   └── style.css
└── templates
    ├── base.html
    └── index.html
```
</details>

# Сборка Dockerfile

<details>
<summary>Dockerfile</summary>

```Dockerfile
FROM python:3.9

WORKDIR /app

# Сначала копируем и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копируем остальное приложение
COPY . /app

CMD ["python", "app.py"]
```
</details>

Указываем базовый образ, который содержит Python 3.9. 
Директива ```WORKDIR``` устанавливает рабочую директорию внутри контейнера. 
Все последующие команды будут выполняться относительно этой директории. В нашем случае рабочая директория называется ```/app```
Командой ```COPY requirements.txt /app/``` копируем файл requirements.txt из локальной системы в директорию ```/app``` внутри контейнера.
requirements.txt содержит некоторые Python-зависимостей, которые необходимы для работы приложения. 
После копирования файла requirements.txt, выполняется команда RUN, которая запускает менеджер пакетов Python для установки всех зависимостей. 
При запуске контейнера запускается python app.py

Соберем докер образ ```sudo docker build -t my-hello-world-app:latest .```

<p align="center"><img src="https://github.com/user-attachments/assets/e5a7d4b9-37e7-4d02-bea0-26e8f59ab554" width=700></p>

# Создание YAML файлов для деплоя в Kubernetes

<details>
<summary>Deployment (распределение приложения)</summary>

```Dockerfile
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-deployment
  labels:
    app: flask-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
      - name: flask-container
        image: my-hello-world-app:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```
</details>

* apiVersion и kind: Указывает на тип ресурса — Deployment.
* metadata: Определяет имя деплоймента (flask-deployment) и метки для группировки ресурсов.
* spec: Определяет, что будет создана 1 реплика контейнера
  * containers: Создает контейнер с именем flask-container, используя образ my-hello-world-app:latest, и маппингом порта 5000.
  * resources: Ограничивает использование ресурсов, задавая минимальные и максимальные значения для памяти и процессора.

<details>
<summary>Service (для доступа к приложению)</summary>

```Dockerfile
apiVersion: v1
kind: Service
metadata:
  name: flask-service
spec:
  type: NodePort
  selector:
    app: flask-app
  ports:
    - protocol: TCP
      port: 5000       
      targetPort: 5000 
      nodePort: 30007  

```
</details>

* apiVersion и kind: Определяет, что создается ресурс типа Service.
* metadata: Указывает имя сервиса — flask-service.
* spec: Определяет параметры сервиса
  * selector: Сопоставляет сервис с подами, имеющими метку app: flask-app.
  * ports: Настраивает порты:
    * port 5000: Внешний порт, на который обращаются клиенты.
    * targetPort 5000: Порт внутри контейнера.
    * nodePort 30007: Фиксированный порт узла для доступа к приложению.
   
# Настройка окружения Docker Minikube

```eval $(minikube docker-env)```

minikube status

```bash
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
docker-env: in-use
```
   
# Применение YAML-файлов в Kubernetes-кластере

<p align="center"><img src="https://github.com/user-attachments/assets/ccfe3e23-85fb-4cbb-85ed-fad2375ebb3a" width=700></p>

<p align="center"><img src="https://github.com/user-attachments/assets/3adf348d-f44b-4007-a34d-75d49d3ed463" width=700></p>

<p align="center"><img src="https://github.com/user-attachments/assets/692b2f68-ecf7-4fc0-bbf7-e6ed84550c61" width=700></p>

# Получение URL для доступа к сервису

<p align="center"><img src="https://github.com/user-attachments/assets/6002ffde-eaf3-4cbe-a4ac-0e2760c3990c" width=700></p>

# Результат работы

<p align="center"><img src="https://github.com/user-attachments/assets/471d03e0-def4-4fed-9683-7eac28a974c1" width=700></p>












