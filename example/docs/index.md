# MkDocs DBML Plugin - Демонстрация

Добро пожаловать! Этот плагин позволяет встраивать красивые диаграммы баз данных прямо в вашу документацию MkDocs.

## Простой пример

Вот простая схема блога:

```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null, unique]
  email varchar(100) [not null]
  created_at timestamp [default: `now()`]
  
  Note: 'Таблица пользователей системы'
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200) [not null]
  content text
  published boolean [default: false]
  created_at timestamp [default: `now()`]
  
  indexes {
    user_id
    (user_id, created_at)
  }
  
  Note: 'Посты пользователей'
}

Table comments {
  id integer [primary key]
  post_id integer [ref: > posts.id]
  user_id integer [ref: > users.id]
  content text [not null]
  created_at timestamp
  
  Note: 'Комментарии к постам'
}
```

## Возможности

- ✅ Автоматический парсинг DBML
- ✅ Красивое отображение таблиц
- ✅ Визуализация связей (foreign keys)
- ✅ Поддержка индексов
- ✅ Отображение constraints (NOT NULL, UNIQUE, DEFAULT)
- ✅ Адаптивный дизайн
- ✅ Поддержка темной темы

Смотрите больше примеров на странице [Примеры](examples.md).
