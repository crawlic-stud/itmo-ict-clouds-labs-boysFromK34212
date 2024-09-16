# 3 лабораторная работа "Локальное развертывание сервиса в Kubernetes с использованием Minikube" (задание со звездочкой)

## Задания

1. Создать helm chart на основе обычной 3 лабы
2. Задеплоить его в кластер
3. Поменять что-то в сервисе, задеплоить новую версию при помощи апгрейда
релиза
4. В отчете приложить скрины всего процесса, все использованные файлы, а
также привести три причины, по которым использовать хелм удобнее чем
классический деплой через кубернетес манифесты

## Ход работы

# Создание Helm Chart на основе 3-й лабораторной работы

Helm — это пакетный менеджер для Kubernetes, который позволяет создавать повторно используемые шаблоны для развертывания приложений.

В Helm основная цель заключается в управлении Kubernetes манифестами и их упрощении с помощью шаблонов и значений, 
что делает процесс деплоя и обновления приложений удобным и воспроизводимым.

<p align="center"><img src="https://github.com/user-attachments/assets/7b4ef8d1-b385-41a9-b09f-fe004a01a8bf" width=700></p>

Установим helm по <a href="https://helm.sh/docs/intro/install/">официальной инструкции</a>

```bash
sudo wget https://get.helm.sh/helm-v3.16.1-linux-amd64.tar.gz
sudo tar -xvzf helm-v3.16.1-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm
```

<p align="center"><img src="https://github.com/user-attachments/assets/c7d46dc7-87b0-470f-9b56-c9ab39066ba4" width=700></p>

Существует также <a href="https://artifacthub.io/">платформа helm</a> с множеством готовых решений

В корневой директории проекта выполним команду для создания шаблона Helm Chart:

```helm create hello-world```

Это создаст структуру папок и файлов в директории hello-world. 
По умолчанию Helm создаст базовые манифесты для деплоймента, сервиса и других ресурсов Kubernetes

<p align="center"><img src="https://github.com/user-attachments/assets/043ad28a-9bcf-4194-a182-f42bd0a488ac" width=700></p>
(файлы deployment.yaml и service.yaml для keberctl позже будут переписаны под helm chart)

Для адаптации текущего кода к Helm, используем параметры из values.yaml для динамического управления настройками приложения.
Это основной файл, в котором задаются параметры и конфигурации для Helm-чарта. Значения из этого файла могут быть использованы в других шаблонах.

* Количество реплик (replicaCount)
* Параметры контейнеров (имя образа, версия)
* Порты для сервисов
* Настройки ресурсов (CPU, память)
* Конфигурации для Service, Ingress и других ресурсов

В values.yaml управление настройками образа, портов и ресурсов вынесено в отдельные параметры, которые можно легко конфигурировать.


<details>

<summary>values.yaml</summary>

```Dockerfile
# Default values for hello-world.
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

# This will set the replicaset count more information can be found here: https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/
replicaCount: 2

# This sets the container image more information can be found here: https://kubernetes.io/docs/concepts/containers/images/
image:
  repository: my-hello-world-app
  tag: latest
  pullPolicy: IfNotPresent


serviceAccount:
  # Specifies whether a service account should be created
  create: true
  # If not set and create is true, a name is generated using the fullname template
  name: ""


# This is for setting up a service more information can be found here: https://kubernetes.io/docs/concepts/services-networking/service/
service:
  type: NodePort
  port: 5000
  targetPort: 5000
  nodePort: 30007

containerPort: 5000

ingress:
  enabled: false  # или true, если нужен Ingress
  annotations: {}
  hosts:
    - host: chart-example.local
      paths: []
  tls: []

resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"


autoscaling:
  enabled: false  # Установим в true, если хотим использовать HPA
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80


nodeSelector: {}

tolerations: []

affinity: {}
```
</details>

Chart.yaml используется для идентификации и управления версиями вашего Helm-чарта (содержит метаданные о чарте). 
Он не участвует напрямую в генерации Kubernetes-ресурсов, но важен для управления версиями и зависимостями чарта.

deployment.yaml (шаблон) использует значения из values.yaml для динамической генерации объекта Deployment, который будет применен в кластер Kubernetes. 

В service.yaml (шаблон) значения из values.yaml используются для определения типа сервиса (например, NodePort, ClusterIP), а также портов для публикации.

Для того чтобы обновить код из основной 3-ей лабораторной работы было необходимо подвязать загрузку параметров из values.yaml

<details>

<summary>deployment.yaml (шаблон)</summary>

```Dockerfile
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
  labels:
    app: {{ .Release.Name }}-app
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}-app
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-app
    spec:
      containers:
      - name: {{ .Chart.Name }}-container
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: {{ .Values.containerPort }}
        resources:
          requests:
            memory: "{{ .Values.resources.requests.memory }}"
            cpu: "{{ .Values.resources.requests.cpu }}"
          limits:
            memory: "{{ .Values.resources.limits.memory }}"
            cpu: "{{ .Values.resources.limits.cpu }}"

```
</details>

<details>

<summary>deployment.yaml (шаблон)</summary>

```Dockerfile
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-service
spec:
  type: NodePort
  selector:
    app: {{ .Release.Name }}-app
  ports:
    - protocol: TCP
      port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      nodePort: {{ .Values.service.nodePort }}
```
</details>

На данный момент директория проекта выглядит следующим образом

```bash
├── app.py                    # Flask приложение
├── Dockerfile                # Dockerfile для сборки образа
├── requirements.txt          # Зависимости Python
├── static/                   # Статические файлы (стили)
│   └── style.css
├── templates/                # HTML шаблоны для Flask
│   ├── base.html
│   └── index.html
├── hello-world/              # Helm chart директория
│   ├── Chart.yaml            # Основной файл описания Helm chart
│   ├── values.yaml           # Файл конфигураций по умолчанию
│   ├── templates/            # Директория с Kubernetes манифестами
│   │   ├── deployment.yaml   # Helm шаблон для деплоя
│   │   ├── service.yaml      # Helm шаблон для сервиса
│   │   ├── _helpers.tpl      # Вспомогательные шаблоны
│   │   ├── ingress.yaml      # Шаблон для Ingress (опционально)
│   │   ├── serviceaccount.yaml  # ServiceAccount для приложения (опционально)
│   │   ├── hpa.yaml          # Horizontal Pod Autoscaler (опционально)
│   │   └── tests/            # Тестовые файлы для проверки
│   │       └── test-connection.yaml  # Тест соединения
└── README.md                 # Информация о проекте

```

Применим наш релиз helm ```helm install flask-app ./hello-world```

<p align="center"><img src="https://github.com/user-attachments/assets/11176e1d-7cd8-499d-a9e5-3749b56d32a3" width=700></p>

Получаем данные IP-адрес узла и порта
```bash
export NODE_PORT=$(kubectl get --namespace default -o jsonpath="{.spec.ports[0].nodePort}" services flask-app-service)
export NODE_IP=$(kubectl get nodes --namespace default -o jsonpath="{.items[0].status.addresses[0].address}")
echo http://$NODE_IP:$NODE_PORT
```

<p align="center"><img src="https://github.com/user-attachments/assets/43bb6f5b-25be-493d-bcdc-781d501f31b3" width=700></p>

<p align="center"><img src="https://github.com/user-attachments/assets/3cb5cac4-e082-4997-9da3-7709e13926ee" width=700></p>

<p align="center"><img src="https://github.com/user-attachments/assets/214c051c-8dda-4afe-82fd-7eee45b7ef04" width=700></p>

Далее укажем replicaCount: 2 в файле values.yaml, изменив количество реплик приложения и обновим Helm-релиз. 

```helm upgrade flask-app ./hello-world```

<p align="center"><img src="https://github.com/user-attachments/assets/0e284c0c-75a7-4f58-b5db-048dbf6cacc6" width=700></p>

Увеличение replicaCount до 2 или более позволяет создать несколько экземпляров Pod-ов. Если один Pod выходит из строя, остальные продолжают работать, обеспечивая доступность приложения.

Они также позволят распределить входящий трафик или запросы между несколькими экземплярами приложения для более равномерного распределения нагрузки.

Kubernetes может использовать стратегию Rolling Update для постепенного обновления Pod-ов. Если есть несколько реплик, Kubernetes обновляет их по одной или небольшими группами, что помогает минимизировать время простоя.

<p align="center"><img src="https://github.com/user-attachments/assets/4ad0460b-647e-48ce-9ffd-0352bce336f6" width=700></p>

## Три причины, почему использовать Helm удобнее, чем классический деплой через Kubernetes манифесты
1. Helm позволяет легко обновлять приложения и их конфигурации, не редактируя вручную каждый YAML-файл
2. Чарты в Helm позволяют создавать шаблоны, которые можно легко адаптировать для разных окружений (например, для тестирования и продакшна) с минимальными изменениями
3. Все параметры приложения можно централизованно хранить в values.yaml, что упрощает настройку и масштабирование, а также минимизирует ошибки при редактировании нескольких манифестов

## Вывод

Helm позволяет легко управлять развертыванием приложений в Kubernetes, делая процесс автоматизированным и масштабируемым. За счет использования шаблонов и файла values.yaml можно управлять параметрами приложения.
В данной работе мы создали Helm-чарт на основе лабораторной работы с Kubernetes, развернули его в кластере, провели обновление через helm upgrade, что продемонстрировало гибкость Helm в управлении версиями и конфигурациями приложений.


