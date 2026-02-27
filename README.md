# MkDocs DBML Plugin

Плагин для MkDocs, который позволяет встраивать красивые диаграммы баз данных из DBML (Database Markup Language) прямо в вашу документацию.

## Возможности

- 🎨 Красивое отображение схем баз данных
- 📊 Автоматическая генерация таблиц с полями, типами данных и связями
- 🔗 Визуализация связей между таблицами (foreign keys)
- 💅 Современный и адаптивный дизайн
- 🚀 Простая интеграция с MkDocs

## Установка

```bash
pip install mkdocs-dbml-plugin
```

## Использование

### 1. Добавьте плагин в `mkdocs.yml`:

```yaml
plugins:
  - search
  - dbml
```

### 2. Используйте DBML в ваших markdown-файлах:

````markdown
```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null, unique]
  email varchar(100) [not null]
  created_at timestamp [default: `now()`]
  
  indexes {
    email [unique]
  }
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200) [not null]
  content text
  created_at timestamp [default: `now()`]
}

Table comments {
  id integer [primary key]
  post_id integer [ref: > posts.id]
  user_id integer [ref: > users.id]
  content text [not null]
  created_at timestamp
}
```
````

### 3. Плагин автоматически преобразует DBML в красивые HTML-таблицы!

## Конфигурация

В `mkdocs.yml` можно настроить дополнительные параметры:

```yaml
plugins:
  - dbml:
      theme: default  # default, dark, minimal
      show_indexes: true  # показывать индексы
      show_notes: true  # показывать заметки
```

## Пример вывода

Плагин генерирует:
- Карточки таблиц с полями и их типами
- Визуальные индикаторы для primary keys, foreign keys, unique, not null
- Список связей между таблицами
- Индексы и заметки

## Лицензия

MIT License
