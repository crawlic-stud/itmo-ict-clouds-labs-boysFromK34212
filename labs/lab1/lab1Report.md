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
    server_name localhost;

    ssl_certificate      C:/nginx/cert/selfsigned.crt;
    ssl_certificate_key  C:/nginx/cert/selfsigned.key;

    location / {
        root   C:/Users/bymrw/Downloads/test/project1/templates;
        index  index.html index.htm;
    }
}
```
7. Закинем в папку project1 код гитхаба одностраничника, найденного на просторах интернета (https://github.com/VaibhavModi/Flask_SPA)

![image](https://github.com/user-attachments/assets/0515cdbe-f75c-42f2-93f8-5954c76ac587)

8. Запускаем app.py, заглядываем на project1.ru. Ничего не запустилось. Пробуем перезагрузить nginx командой
```
nginx -s reload
```
Выскакивает ошибка
```
nginx: [emerg] "server" directive is not allowed here in C:\Users\bymrw\Downloads\nginx\conf\nginx.conf:1
```
9. После пары минут гугления, обновим файл конфигурации
```
events {
    worker_connections  1024;
}
http {
    server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate      C:/Users/bymrw/Downloads/nginx/cert/selfsigned.crt;
    ssl_certificate_key  C:/Users/bymrw/Downloads/nginx/cert/selfsigned.key;

    location / {
        root   C:/Users/bymrw/Downloads/test/project1/templates;
        index  index.html index.htm;
        }
    }
}
```
10. Перезапустим nginx, перейдем на https://localhost

![image](https://github.com/user-attachments/assets/efb48f68-3cb0-4d3e-828e-c239157fa696)

11. Все заработало! Но кривовато. Добавим alias для того, чтобы подгрузить картинки
```
location /static/ {
    alias C:/Users/bymrw/Downloads/test/project1/static/;
}
```
12. Проделаем то же самое, но со вторым сайтом, test/project2. Добавим в конфиг информацию об адресах и портах проектов. Первый проект - 5000 порт, второй проект - порт 5001
```
events {
    worker_connections  1024;
}
http {
    server {
    	listen 443 ssl;
    	server_name project1.example.com;

    	ssl_certificate      C:/Users/bymrw/Downloads/nginx/cert/selfsigned.crt;
    	ssl_certificate_key  C:/Users/bymrw/Downloads/nginx/cert/selfsigned.key;

    	root   C:/Users/bymrw/Downloads/test/project1/templates/;
    	index  index.html index.htm;

    	location /static/ {
        		alias C:/Users/bymrw/Downloads/test/project1/static/;
        	}
 	location / {
        		proxy_pass http://127.0.0.1:5000;
        	}
    }
    server {
    	listen 443 ssl;
    	server_name project2.example.com;

    	ssl_certificate      C:/Users/bymrw/Downloads/nginx/cert/selfsigned.crt;
    	ssl_certificate_key  C:/Users/bymrw/Downloads/nginx/cert/selfsigned.key;

    	root   C:/Users/bymrw/Downloads/test/project2/templates/;
    	index  index.html index.htm;

    	location /static/ {
        		alias C:/Users/bymrw/Downloads/test/project2/static/;
        	}
 	location / {
        		proxy_pass http://127.0.0.1:5001;
        	}
    }
}
```
13. Открываем оба сайта

![image](https://github.com/user-attachments/assets/3eb3d4e5-fe2a-4d82-93cf-be4294a1c1f1)

![image](https://github.com/user-attachments/assets/d38596ea-9938-4a07-9833-9cfcf41662ce)


# Лабораторная 1*

Попробовать взломать nginx другой команды. Проверить минимум три уязвимости - например path traversal, перебор страниц через ffuf и/или любые другие на ваш выбор

## Ход работы

1. Попробуем взломать nginx команды 20. Скачиваем .conf файл
```
server {

    listen 80;

    server_name project1.example.com; return 301 https://$host$request_uri; }

server {

    listen 443 ssl;

    server_name project1.example.com;

    ssl_certificate /etc/letsencrypt/live/project1.example.com/fullchain.pem; ssl_certificate_key /etc/letsencrypt/live/project1.example.com/privkey.pem;

    root /var/www/project1; index index.html;

    location /static/ {

        alias /var/www/project1/static/; }

}

server {

    listen 80;

    server_name project2.example.com; return 301 https://$host$request_uri; }

server {

    listen 443 ssl;

    server_name project2.example.com;

    ssl_certificate /etc/letsencrypt/live/project2.example.com/fullchain.pem; ssl_certificate_key /etc/letsencrypt/live/project2.example.com/privkey.pem;

    root /var/www/project2; index index.html;

    location /assets/ {

        alias /var/www/project2/assets/; }

}
``` 
2. Скачиваем инструмент Burp Suite с официального сайта и заходим на сайт project1.example.com

![image](https://github.com/user-attachments/assets/974e8d95-c92d-4078-9ef8-17e2cd232acd)

3. Как мы видим, все возможные адреса он выдал. Попробуем перейти на project1.example.com/blogs

![image](https://github.com/user-attachments/assets/02529a68-a58d-44de-8cda-7b2c52cf92d6)

4. Можно запустить sniper attack на поиск дат на сайте

![image](https://github.com/user-attachments/assets/7b6d0adf-805f-49aa-802f-51a96170355a)

И вообще очень мощный инструмент, правда нужно время, чтобы разобраться

5. Скачиваем словарь SecList под названием html-tags.txt. Скачиваем ffuf, запускаем поиск html тегов командой
```
ffuf -u https://project1.example.com/FUZZ -w html-tags.txt
```
![image](https://github.com/user-attachments/assets/735ef781-7eef-40b2-93b0-e363a93393e9)

Адреса он не вывел, значит ничего не найдено

6. Можно еще проверить на уязвимость XSS, вставим в поле ввода код
```
<script>alert('XSS');</script>
```

![image](https://github.com/user-attachments/assets/6f98fabf-abaa-4349-9012-fc29935a580d)

Нажимаем Send Message, и ничего не происходит :) Скорее всего логика отправки сообщений не реализована

