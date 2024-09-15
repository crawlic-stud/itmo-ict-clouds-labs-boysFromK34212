#!/bin/bash

# Переключаем Docker на Minikube
eval $(minikube docker-env)

# Сборка
echo "Building Docker image..."
docker build -t my-hello-world-app:latest .

# Применение Kubernetes манифестов
echo "Applying Kubernetes manifests..."
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

echo "Fetching service URL..."
SERVICE_URL=$(minikube service flask-service --url)

echo "Service is running at: $SERVICE_URL"
