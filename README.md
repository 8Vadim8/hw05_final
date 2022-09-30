# Проект «Yatube»
Yatube — это социальная сеть для блоггеров с возможностью публикации личных дневников
и возможностью оставлять комментарии и подписываться на авторов.

## Приложение имеет следующий функционал:
- публикация поста с возможностью прикрепить к нему изображение
- комментирование постов
- подписки на понравившихся авторов
- пагинация и кеширование
- Код проекта покрыт unit-тестами
## Технологии:
- Python 3.7
- Django 2.2
## Установка и запуск
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/8Vadim8/hw05_final.git
cd hw05_final
```
Создать и активировать виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
```
Обновить pip и установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Перейти в каталол проекта:

```
cd yatube
```

Cоздать в ней файл .env и прописать SECRET_KEY
```
echo "SECRET_KEY=YourSecretKey" > .env
```
Секретный ключ Джанго можно сгенерировать [здесь](https://djecrety.ir)

Выполнить миграции:

```
python manage.py migrate
```

Создаем суперпользователя:

```
python manage.py createsuperuser
```

Запустить проект:

```
python manage.py runserver
```