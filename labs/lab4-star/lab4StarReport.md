# 4* лабораторная работа "Секреты в Hashicorp Vault"

## Задание

Сделать красиво работу с секретами. Например, поднять Hashicorp Vault и сделать так, чтобы ci/cd пайплайн (или любой другой ваш сервис) ходил туда, брал секрет, использовал его не светя в логах. В Readme аргументировать почему ваш способ красивый, а также описать, почему хранение секретов в CI/CD переменных репозитория не является хорошей практикой.

## Ход работы

Так как само по себе хранение переменных окружения в переменных Github - не является хорошей практикой по следующим причинам:
 - Ненадежность, так как нет возможности заселфхостить секреты, и в случае взлома Github - все данные будут в открытом доступе
 - Возможные утечки от ненадежных сотрудников с доступом к настройкам репозитория
 - Отсутствие возможности создания "централизованного" хранилища секретов
 - Отсутствие возможности модерировать доступ к секретам через ключи доступа и роли
 - Меньшая масштабируемость
 - Отсутствие возможностей хранения более сложных структур данных
 - Отсутствие сохранения версий секретов и истории их изменения кем и когда

Соответствено, было принято решение использовать хранилище от Hashicorp Vault, а затем [интегрировать импорт секретов](https://github.com/hashicorp/vault-action) из их бесплатного облачного решения через Github Actions.

### Создание хранилища

Для создания хранилища секретов был использован [бесплатный сервис](https://www.hashicorp.com/cloud) от Hashicorp. В нем был создан аккаунт и приложение для секретов:

![image](https://github.com/user-attachments/assets/ac05f44d-ebe8-4368-85a3-c8b93688ccbf)


### Синхронизация с Github Secrets

Также, помимо импорта секретов из Hashicorp Vault можно настроить синхронизацию секретов с Github:

![image](https://github.com/user-attachments/assets/f66340be-26ae-42a6-8f6a-4520064d24bd)

После создания синхронизации для репозитория - будет автоматически запущена синхронизация и переменные появятся в Github Secrets:


Секреты в Hashicorp:

![image](https://github.com/user-attachments/assets/2d6df902-8a0e-4577-93e0-363913b6815c)


Секреты в Github:

![image](https://github.com/user-attachments/assets/90f4c30e-dbf1-4ee2-b18e-76a72ea4ff9b)


### Получение секретов в Github Actions

Для авторизации для получения секретов необходимо было получить токен доступа к API. Для этого необходимо было использовать client_id и client_secret, заранее созданные на дашборде Hashicorp Vault:

![image](https://github.com/user-attachments/assets/3a605fc8-cb78-404d-8066-cc01735de0b8)

Выполнив команды из гайда, возвращается access_token, который потом можно использовать для получения секретов:

```sh
$ curl --location "https://auth.idp.hashicorp.com/oauth2/token" --header "Content-Type: application/x-www-form-urlencoded" --data-urlencode "client_id=..." --data-urlencode "client_secret=..." --data-urlencode
"grant_type=client_credentials" --data-urlencode "audience=https://api.hashicorp.cloud"
```
```json
{"access_token":"eyJhb...","token_type":"Bearer","expires_in":3600}
```

При запросе в организацию с методом `/open` возвращаются все ранее заполненные секреты, а именно данные для входа в DockerHub. Помимо этого, также возвращается информации о версиях переменных, их тип, время создания, данные пользователя, а также данные о синхронизации с Github:

```sh
$ curl \
> --location "https://api.cloud.hashicorp.com/secrets/2023-06-13/organizations/c8ebd130-6e1f-4fcb-abe3-3a9a4f33228b/projects/f0048f83-1ab5-4e96-8b4b-2367b94f512f/apps/sample-app/open" \
> --request GET \
> --header "Authorization: Bearer eyJhb..."
```
```json
{
  "secrets": [
    {
      "name": "DOCKERHUB_TOKEN",
      "version": {
        "version": "1",
        "type": "kv",
        "created_at": "2024-09-25T08:46:58.951615Z",
        "value": "...",
        "created_by": {
          "name": "Nikita Kuznetsov",
          "type": "TYPE_USER",
          "email": "nikitosik0726@gmail.com"
        },
        "created_by_id": "7973798c-cc2c-4d4b-b4a2-1501980ba45a"
      },
      "created_at": "2024-09-25T08:46:58.951615Z",
      "latest_version": "1",
      "created_by": {
        "name": "Nikita Kuznetsov",
        "type": "TYPE_USER",
        "email": "nikitosik0726@gmail.com"
      },
      "sync_status": {
        "e48bff22-258f-497d-93cc-9c55588bab51": {
          "status": "SYNCED",
          "updated_at": "2024-09-25T08:47:40.697653Z",
          "last_error_code": ""
        }
      },
      "created_by_id": "7973798c-cc2c-4d4b-b4a2-1501980ba45a"
    },
    {
      "name": "DOCKER_USERNAME",
      "version": {
        "version": "1",
        "type": "kv",
        "created_at": "2024-09-25T08:46:58.929719Z",
        "value": "crawlic",
        "created_by": {
          "name": "Nikita Kuznetsov",
          "type": "TYPE_USER",
          "email": "nikitosik0726@gmail.com"
        },
        "created_by_id": "7973798c-cc2c-4d4b-b4a2-1501980ba45a"
      },
      "created_at": "2024-09-25T08:46:58.929719Z",
      "latest_version": "1",
      "created_by": {
        "name": "Nikita Kuznetsov",
        "type": "TYPE_USER",
        "email": "nikitosik0726@gmail.com"
      },
      "sync_status": {
        "e48bff22-258f-497d-93cc-9c55588bab51": {
          "status": "SYNCED",
          "updated_at": "2024-09-25T08:47:40.710246Z",
          "last_error_code": ""
        }
      },
      "created_by_id": "7973798c-cc2c-4d4b-b4a2-1501980ba45a"
    }
  ]
}
```

> [!NOTE]
> Все важные переменные были зацензурены :)

### Написание Github Actions для получения секретов


