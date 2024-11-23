# 5 Лабораторная
## Задача

Сделать мониторинг сервиса, поднятого в кубере (использовать, например, prometheus и grafana). Показать хотя бы два рабочих графика, которые будут отражать состояние системы. Приложить скриншоты всего процесса настройки.

## Ход работы

Поднимаем локальный Kubernetes-кластер

```minikube start```

и создаем пространство имен для мониторинга

```kubectl create namespace monitoring```

Добавляем в наше пространство имен grafana для визуализации собранных меток, prometheus для сбора меток и robusta (для тестов, посмотреть что как там устроено)

* Grafana и prometheus

```bash
helm install first-prometheus prometheus-community/prometheus -f values/prometheus-values.yaml --namespace monitoring
helm install first-grafana grafana/grafana -f values/grafana-values.yaml --namespace monitoring
```

<p align="center"><img src="./Work_Img/795000000.png" width=700></p>


<p align="center"><img src="./Work_Img/013000000.png" width=700></p>


Добавляем ресурс, с которого будут собираться метрики, в моем случае это nginx

```bash
helm install my-nginx bitnami/nginx \
  --set metrics.enabled=true \
  --set metrics.serviceMonitor.enabled=true \
  --set metrics.serviceMonitor.namespace=monitoring \
  --set metrics.serviceMonitor.interval=5s \
  --set metrics.serviceMonitor.scrapeTimeout=5s
```

Прокинув порт увидим ```kubectl --namespace monitoring port-forward svc/my-nginx 9200:80``` nginx

<p align="center"><img src="./Work_Img/979000000.png" width=700></p>

<p align="center"><img src="./Work_Img/925000000.png" width=700></p>


<p align="center"><img src="./Work_Img/546000000.png" width=700></p>

<p align="center"><img src="./Work_Img/099000000.png" width=700></p>

<p align="center"><img src="./Work_Img/422000000.png" width=700></p>

Хотел настроить flask приложение с помощью prometheus_client, но никак не удавалось применить deployment.yaml для него, при том, что в 3-ей лабе проблем с этим не было (писал ошибку docker login, хоть я и был авторизован). Думал, что это связано с тем, что я в этот раз использовал драйвер docker для minikube. Но решение было проще, совсем забыл закинуть образ в minikube
```minikube image load flask-app:latest```
Образ был на локальной машине, поэтому он сохранялся в локальном Docker-реестре. Minikube использует свой собственный Docker-демон, поэтому он "не видел" образы, созданные на локальном Docker-демоне. Minikube не может находить их автоматически

Но заставить prometheus увидить метрики flask пока не удалось, а вот с robusta он их видит, почему я не знаю

<p align="center"><img src="./Work_Img/810000000.png" width=700></p>

<p align="center"><img src="./Work_Img/652000000.png" width=700></p>

<p align="center"><img src="./Work_Img/105000000.png" width=300></p>

## Задание со звездочкой

### Создание бота и алерт конфига

Создаем бота в telegram и получаем его токен

<p align="center"><img src="./Work_Img/850000000.png" width=300></p>

Конфигурация для настройки оповещений и мониторинга с Prometheus Alertmanager и Telegram для отправки уведомлений включает в себя настройки глобальных параметров, маршрутизации оповещений, получателей

<details>

<summary>Конфиг файл</summary>

```yaml
alertmanager:
  config:
    global:
      resolve_timeout: 1m
      telegram_api_url: "https://api.telegram.org"

    route:
      group_by: ['alertname']alertmanager:
      route:
        receiver: telegram

    receivers:
      - name: telegram
        telegram_configs:
          - chat_id: тут id
            bot_token: тут токен
            api_url: "https://api.telegram.org"
            send_resolved: true
            parse_mode: Markdown
            message: |-
              {{ range .Alerts }}
                🚨 *{{ .Annotations.summary }}*
                {{ .Annotations.description }}

                *Details:*
                {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
                {{ end }}
              {{ end }}

serverFiles:
  alerting_rules.yml:
    groups:
      - name: nginx_alerts
        rules:
          - alert: NginxDown
            expr: nginx_up == 0
            labels:
              severity: critical
            annotations:
              summary: "Nginx is down on {{ $labels.instance }}"
              description: "No response from Nginx exporter for more than 1 minute."
        
        rules:
          - alert: HighHttpRequests
            expr: nginx_http_requests_total > 1000
            for: 5m
            labels:
              severity: critical
            annotations:
              summary: "HTTP requests exceed 1000 on Nginx instance {{ $labels.instance }}"
              description: "The total number of HTTP requests on Nginx has exceeded 1000 for the last 5 minutes."
```
</details>

Применение конфига
```helm upgrade first-prometheus prometheus-community/prometheus -f alert.yaml -n monitoring```

В**message** написан шаблон сообщения, которое будет отправлено. В данном случае сообщение формируется с использованием Go-шаблонов
Каждое сообщение будет содержать символ 🚨 и выделенное жирным шрифтом краткое описание алерта.
А также полное описание алерта и подробности по меткам алерта, выводящиеся как пары "имя-значение", отформатированные с помощью Markdown.

**NginxDown** — алерт, который срабатывает, когда метрика nginx_up равна 0, то есть Nginx не отвечает.

**HighHttpRequests** — алерт, который срабатывает, если слишком много обращений.

<p align="center"><img src="./Work_Img/238000000.png" width=700></p>

После того, как прокинули порты с подов, можем открыть http://127.0.0.1:9091/alerts и увидеть, что наши алерты применились и пока находятся в ожидании

<p align="center"><img src="./Work_Img/010000000.png" width=700></p>

Проверяем

<p align="center"><img src="./Work_Img/093000000.png" width=700></p>

<p align="center"><img src="./Work_Img/654000000.png" width=700></p>

<p align="center"><img src="./Work_Img/691000000.png" width=700></p>

## Вывод 

Сделал мониторинг сервис, поднятый в кубере, настроил уведомления prometheus alert, познакомился с robusta 

<details>
<summary>не оформлено, пытался связать Slack и robusta, но видимо где то запутался, потом вернусь, не хочется удалять</summary>

------------------
Создаем канал Slack, аккаунт и токен

<p align="center"><img src="./Work_Img/182000000.png" width=400></p>

И устанавливаем Robusta

```bash
helm install robusta robusta/robusta -f ./robusta-values.yaml \
  --set clusterName=minikube \
  --namespace monitoring
```

<p align="center"><img src="./Work_Img/103000000.png" width=700></p>

<details>

<summary>robusta-values.yaml</summary>

```yaml
globalConfig:
  signing_key: <...>
  account_id: <...>
sinksConfig:
  - robusta_sink:
      name: robusta_ui_sink
      token: <...>
enablePrometheusStack: true
enablePlatformPlaybooks: true
runner:
  sendAdditionalTelemetry: true
enableHolmesGPT: true
holmes:
  additionalEnvVars:
    - name: ROBUSTA_AI
      value: "true"
prometheus:
  enabled: true

grafana:
  enabled: true
```
</details>

```kubectl get pods -A | grep robusta```

<p align="center"><img src="./Work_Img/951000000.png" width=700></p>


<p align="center"><img src="./Work_Img/972000000.png" width=700></p>

</details>