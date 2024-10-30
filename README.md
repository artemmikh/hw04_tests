# Проект "Сейчас"

Проект представляет собой социальную сеть с функционалом постов, подписок, комментариев и групп пользователей.
Пользователь может создавать и редактировать свои записи, подписываться на других пользователей, оставлять комментарии и
просматривать посты по группам.

### Протестировать проект можно по [этой ссылке](https://now.viewdns.net)

## Основные функции

- **Регистрация и авторизация**: пользователи могут создавать аккаунты, входить в систему, менять пароли.
- **Создание постов**: авторизованные пользователи могут создавать посты с текстом и изображениями.
- **Комментирование**: пользователи могут оставлять комментарии к постам.
- **Группы**: посты могут быть привязаны к группам, и пользователи могут просматривать посты по группам.
- **Подписки**: пользователи могут подписываться на других пользователей и получать их обновления на странице подписок.

## Технологии

Проект разработан с использованием следующих технологий и библиотек:

- **Python 3.9** — основной язык программирования
- **Django 2.2.16** — основной фреймворк для разработки приложения
- **SQLite** — баз данных для хранения информации
- **HTML** и **CSS** — для построения интерфейса пользователя
- **Django ORM** — для взаимодействия с базой данных
- **Bootstrap** — для стилизации компонентов пользовательского интерфейса

## Установка

1. **Клонируйте репозиторий**:

   ```bash
   git clone https://github.com/artemmikh/hw04_tests.git
   ```

2. **Создайте и активируйте виртуальное окружение в директории с проектом**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # для Linux/macOS
   venv\Scripts\activate     # для Windows
   ```

3. **Установите зависимости**:

   ```bash
   pip install -r requirements.txt
   ```
4. **Настройки и переменные окружения**

   Создайте `.env` файл в корне проекта и добавте туда

5. **Настройка базы данных**:

   Примените миграции базы данных:

   ```bash
   python manage.py migrate
   ```

6. **Запустите сервер**:

   ```bash
   python manage.py runserver
   ```

7. **Создайте суперпользователя** (для доступа к панели администратора):

   ```bash
   python manage.py createsuperuser
   ```

После этого проект будет доступен по адресу `http://127.0.0.1:8000`.
Панель администратора будет доступна по адресу `http://127.0.0.1:8000/admin`.

## Примеры использования

### Добавление поста

Авторизованные пользователи могут создавать посты, выбрав группу и добавив изображение, используя форму на странице
создания поста.

### Подписки

На странице профиля пользователя доступна кнопка подписки или отписки. При подписке на автора его посты будут
отображаться на странице подписок текущего пользователя.

### Комментарии

Комментарии к постам могут оставлять только авторизованные пользователи.

## Администрирование

Панель администратора доступна по адресу `/admin/`. Администратор может управлять пользователями, постами, группами и
подписками.

## Лицензия

Проект открыт под лицензией MIT.
