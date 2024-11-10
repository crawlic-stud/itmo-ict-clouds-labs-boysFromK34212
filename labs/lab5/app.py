from flask import Flask, render_template
from prometheus_client import generate_latest, Counter, Gauge, Summary
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# Примеры метрик
REQUEST_COUNT = Counter("request_count", "Total number of requests")
REQUEST_LATENCY = Summary("request_latency_seconds", "Request latency in seconds")

@app.route('/')
def index():
    REQUEST_COUNT.inc()  # Увеличивает счетчик запросов
    with REQUEST_LATENCY.time():  # Измеряет время выполнения запроса
        return render_template('index.html')

# Интеграция Prometheus метрик через WSGI
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
