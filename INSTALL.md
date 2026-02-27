# Инструкция по установке и использованию

## Установка для разработки

1. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd dbml
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите плагин в режиме разработки:
```bash
pip install -e .
```

## Тестирование с примером

1. Перейдите в директорию с примером:
```bash
cd example
```

2. Запустите MkDocs сервер:
```bash
mkdocs serve
```

3. Откройте браузер по адресу `http://127.0.0.1:8000`

## Использование в вашем проекте

1. Установите плагин:
```bash
pip install mkdocs-dbml-plugin
```

2. Добавьте в `mkdocs.yml`:
```yaml
plugins:
  - search
  - dbml
```

3. Используйте DBML в markdown:
````markdown
```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null]
  email varchar(100) [not null, unique]
}
```
````

## Настройка

Доступные параметры конфигурации:

```yaml
plugins:
  - dbml:
      theme: default  # default или dark
      show_indexes: true  # показывать индексы
      show_notes: true  # показывать заметки
```

## Публикация пакета

Для публикации на PyPI:

```bash
python setup.py sdist bdist_wheel
pip install twine
twine upload dist/*
```
