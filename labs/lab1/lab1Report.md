# Лабораторная 1

## Требования к настройке nginx
1. Работает по https c сертификатом.
2. Настроено принудительное перенаправление HTTP-запросов (порт 80) на HTTPS (порт 443) для обеспечения безопасного соединения.
3. Использован alias для создания псевдонимов путей к файлам или каталогам на сервере.
4. Настроены виртуальные хосты для обслуживания нескольких доменных имен на одном сервере.

## Результат
Предположим, что у вас есть два пет проекта на одном сервере, которые должны быть доступны по https. Настроенный вами веб сервер умеет работать по https, относить нужный запрос к нужному проекту, переопределять пути исходя из требований пет проектов.

## Ход работы
1. Установим nginx на Windows. Скачиваем дистрибутив с сайта nginx.org, распаковываем в C:\nginx. Запускаем с помощью команды
```
C:\nginx>start nginx
```
2. Перейдем по адресу localhost, чтобы проверить работу nginx

![image](https://github.com/user-attachments/assets/9c3eae73-5921-4370-bd2c-59079e55b953)

3. Далее сгенерируем самоподписанный SSL сертификат командой
```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout selfsigned.key -out selfsigned.crt
```

![image](https://github.com/user-attachments/assets/d84dfa0c-5dab-4ce6-9403-0eb1cbd59d8c)

4. Перекидываем selfsigned.key и selfsigned.crt в C:\nginx\cert
5. Отредактируем файл конфигурации nginx, добавив серверный блок для первого проекта
```
server {
    listen 443 ssl;
    server_name myproject.local;

    ssl_certificate      C:/nginx/cert/selfsigned.crt;
    ssl_certificate_key  C:/nginx/cert/selfsigned.key;

    location / {
        root   C:/test/project1;
        index  index.html index.htm;
    }
}
```
6. Серверный блок для второго проекта
```
server {
    listen 443 ssl;
    server_name anotherproject.local;

    ssl_certificate      C:/nginx/cert/selfsigned.crt;
    ssl_certificate_key  C:/nginx/cert/selfsigned.key;

    location / {
        root   C:/test/project2;
        index  index.html index.htm;
    }
}
```
7. Закинем в папки project1 и project2 код с представленного сайта

![image](https://github.com/user-attachments/assets/a85d404d-7927-4554-ba01-762de607c4ef)

8. 



