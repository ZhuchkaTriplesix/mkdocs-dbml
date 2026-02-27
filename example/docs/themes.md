# Темы оформления

Плагин поддерживает несколько цветовых тем для диаграмм. Выберите ту, которая подходит к дизайну вашей документации!

## Default (по умолчанию)

Классическая фиолетовая тема с градиентом от индиго до пурпурного.

```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null]
  email varchar(100) [unique]
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200)
}
```

## Как изменить тему

В `mkdocs.yml`:

```yaml
plugins:
  - dbml:
      theme: ocean  # выберите: default, ocean, sunset, forest, dark
```

## Доступные темы

### 🌊 Ocean (Океан)
Голубая морская тема - идеальна для технической документации.

### 🌅 Sunset (Закат)
Розово-голубой градиент - яркая и современная тема.

### 🌲 Forest (Лес)
Зеленая природная тема - спокойная и профессиональная.

### 🌙 Dark (Темная)
Темная тема для dark mode интерфейсов.

## Кастомизация

Хотите свою тему? Легко! Отредактируйте `mkdocs_dbml_plugin/config.py`:

```python
THEMES = {
    'my_theme': {
        'gradient_start': '#FF6B6B',
        'gradient_end': '#4ECDC4',
        'line_color': '#45B7D1',
        'bg_color': '#f8f9fa',
        'border_color': '#dee2e6',
    }
}
```

Затем используйте:

```yaml
plugins:
  - dbml:
      theme: my_theme
```

## Советы по выбору темы

- **Default** - универсальная, подходит для любой документации
- **Ocean** - для технических проектов, API документации
- **Sunset** - для креативных проектов, стартапов
- **Forest** - для корпоративной документации
- **Dark** - для dark mode сайтов

Все темы адаптивны и хорошо смотрятся на любых экранах!
