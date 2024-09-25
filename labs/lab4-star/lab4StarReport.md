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

Для начала, секреты для получения токена были добавлены в Hashicorp и автоматически засинхронизированы в Github:

![image](https://github.com/user-attachments/assets/92127e6d-b12a-4800-9779-4d3058862d20)

Предположим, что секретов для доступа в DockerHub нет в списке секретов Github, а они есть только в Hashicorp Vault. Для того чтобы их получить - необходимо добавить два шага к процессу сборки проекта:

1. Получение токена для доступа в Vault:

```yml
...
steps:
  - name: Get Hashicorp access token
    id: hcp_token
    run: |
      echo token=$(curl --location "https://auth.idp.hashicorp.com/oauth2/token" \
        --header "Content-Type: application/x-www-form-urlencoded" \
        --data-urlencode "client_id=${{ secrets.HCP_CLIENT_ID }}" \
        --data-urlencode "client_secret=${{ secrets.HCP_CLIENT_SECRET }}" \
        --data-urlencode "grant_type=client_credentials" \
        --data-urlencode "audience=https://api.hashicorp.cloud" | jq -r .access_token) >> $GITHUB_OUTPUT
```

> [!NOTE]
> Для получения токена используется ранее описанный запрос cURL, который возвращает поле `access_token` из тела ответа от API и помещает его в `$GITHUB_OUTPUT` в переменную с названием `token`. Далее эту переменную можно использовать в следующем шаге, при этом не показывая ее значение в логах.

2. Получение нужных переменных через API, используя полученный токен:

```yml
steps:
...
 - name: Use access token to get secrets
   id: hcp_secrets
   run: |
     secrets=("DOCKERHUB_TOKEN" "DOCKER_USERNAME")
     
     for item in ${secrets[@]}; do
       echo "Processing secret: $item"

       echo $item=$(curl \
         --location "https://api.cloud.hashicorp.com/secrets/2023-06-13/organizations/${{ secrets.HCP_VAULT_PATH }}/open/${item}" \
         --request GET \
         --header "Authorization: Bearer ${{ steps.hcp_token.outputs.token }}" | jq -r .secret.version.value) >> $GITHUB_OUTPUT
     done
```

> [!NOTE]
> В данном шаге задается список нужных секретов для получения, а именно `DOCKERHUB_TOKEN` и `DOCKER_USERNAME`, которые нужны для авторизации в DockerHub. Далее, по каждому значению делается запрос и помещается в переменную с таким же названием, аналогично пункту 1.

### Результаты

После добавления этих шагов - необходимо изменить шаги по деплою в DockerHub, добавив туда полученные переменные:

```yml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ steps.hcp_secrets.outputs.DOCKER_USERNAME }} 
    password: ${{ steps.hcp_secrets.outputs.DOCKERHUB_TOKEN }} 
    
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
- name: Build and push
  uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    file: ./labs/lab4/Dockerfile
    tags: ${{ steps.hcp_secrets.outputs.DOCKER_USERNAME }}/${{ inputs.image-name }}:latest
```


И в конечном итоге (спустя несколько десятков неудачных попыток), получается запустить билд точно так же, как при использовании Github Secrets, только в этот раз все секреты хранятся в облаке в Hashicorp Vault:

![image](https://github.com/user-attachments/assets/e1c9d137-efaa-4046-972f-be5b8822f529)
![image](https://github.com/user-attachments/assets/774a6ba8-2dd6-4275-b6a3-976ed2cbd5ec)

## Выводы

В результате работы получилось реализовать хранилище секретов через Hashicorp Vault, а также интегрировать его в пайплайн сборки на Github Actions. Данный способ хранения секретов является хорошей практикой, так как он не зависит от платформы, на которой реализовано CI/CD, что является огромным плюсом, так как при росте проекта скорее всего Github Actions будут обладать слишком ограниченным функционалом.
