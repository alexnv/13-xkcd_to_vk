# Публикация комикса XKCD в сообщество VK

Скрипт для публикации комикса XKCD в сообщество VK.

Для публикации комикса необходимо вызвать скрипт из командной строки. Для публикации комикса с конкретным id его необходимо указать в параметрах скрипта, если id не указан, то будет опубликован случайный комикс

Например:

```commandline
python main.py
```

```commandline
usage: main.py [-h] [id]                                                   
                                                                           
Программа загружает фото XKCD и публикует на стену VK                      
                                                                           
positional arguments:                                                      
  id          Номер комикса, если не указан будет сохранен случайный комикс
                                                                           
optional arguments:                                                        
  -h, --help  show this help message and exit 

```

### Как установить

1. Установить требуемые библиотеки для скрипта командой 
```
pip install -r requirements.txt
```
2. Создать группу в [VK](https://vk.com/groups?tab=admin), сохранить в файле `.env` в параметре `VK_GROUPID` идентификатор группы
3. Создать приложение в [VK](https://vk.com/dev). В качестве типа приложения следует указать `standalone` 
4. Пройти авторизацию
   1. Процедура [Implicit Flow](https://vk.com/dev/implicit_flow_user) 
   2. Так как вы используете standalone приложение, для получения ключа пользователя стоит использовать Implicit Flow 
   3. Убрать параметр redirect_uri у запроса на ключ 
   4. Параметр scope указать через запятую, вот так: `scope=photos,groups,wall`.
5. и сохранить `access_token` в файле `.env` в параметре `VK_ACCESS_TOKEN`
