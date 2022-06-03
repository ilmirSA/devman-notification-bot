
# Что делает скрипт.

Скрипт отправляет уведомления  о проверке ваших работ  в телеграмм.

# Как настроить скрипт.
Скачайте репозиторий себе и распакуйте его.

1. Перейдите на сайт [devman](https://dvmn.org) зарегистрируйтесь и перейди во кладку API скопируйте свой api token перейдите в папку скрипта откройте документ ```.env.dist``` и вставьте в поле ```DEVMAN_TOKEN``` свой токен.
 
2. Так же вам нужно создать телеграмм бота и получить его токен как это сделать есть на этом [сайте](https://boto.agency/blog/kak-polychit-api-token-telegram/)  откройте файл ```.env.dist``` и вставьте свой токен телеграмм бота  в поле ```TG_TOKEN```.
3. Далее нам понадобиться еще ```chat_id``` что бы его узнать напишите боту ```@userinfobot``` в поле ```id``` будет ваш ```chat_id``` скопируйте и вставьте в файл ```.env.dist``` в поле ```TG_CHAT_ID```

# Запуск Скрипта.
После того как вы скачали репозиторий и настроили скрипт он готов к запуску.
Запустите следующую команду она установит все нужные библиотеки.
```python 
pip install -r requirements.txt
```
Далее уже запустите сам скрипт следующей командой.
```python
python main.py
```