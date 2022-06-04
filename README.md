# Отправка уведомления о проверке работ

Программа позволяет отправлять уведомление через телеграм бота, о результате проверки работ с сайта [dvmn.org](https://dvmn.org). 
  
### Как установить

Python3 должен быть уже установлен.
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```bash
pip install -r requirements.txt
```

### Первоначальная настройка

Скопируйте файл `.env.Example` и переименуйте его в `.env`.  

Заполните переменные окружения в файле `.env`:  
`DEVMAN_TOKEN` - API токен с сайта [dvmn.org](https://dvmn.org).  
`TELEGRAM_TOKEN` - токен телеграм бота.  
`TELEGRAM_CHAT_ID` - ID телеграм чата.  


### Как запускать
```bash
python main.py
```
