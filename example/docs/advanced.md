# Advanced examples

## Social network

A social network schema with many relationships:

```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null, unique]
  email varchar(100) [not null, unique]
  password_hash varchar(255) [not null]
  bio text
  avatar_url varchar(255)
  created_at timestamp
  
  Note: 'System users'
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  content text [not null]
  image_url varchar(255)
  likes_count integer [default: 0]
  created_at timestamp
  
  Note: 'User posts'
}

Table comments {
  id integer [primary key]
  post_id integer [ref: > posts.id]
  user_id integer [ref: > users.id]
  content text [not null]
  created_at timestamp
}

Table likes {
  id integer [primary key]
  user_id integer [ref: > users.id]
  post_id integer [ref: > posts.id]
  created_at timestamp
  
  indexes {
    (user_id, post_id) [unique]
  }
}

Table friendships {
  id integer [primary key]
  user_id integer [ref: > users.id]
  friend_id integer [ref: > users.id]
  status varchar(20)
  created_at timestamp
  
  indexes {
    (user_id, friend_id) [unique]
  }
}

Table messages {
  id integer [primary key]
  sender_id integer [ref: > users.id]
  receiver_id integer [ref: > users.id]
  content text [not null]
  is_read boolean [default: false]
  created_at timestamp
}
```

## Online learning system

```dbml
Table courses {
  id integer [primary key]
  title varchar(200) [not null]
  description text
  instructor_id integer [ref: > instructors.id]
  price decimal(10,2)
  created_at timestamp
}

Table instructors {
  id integer [primary key]
  name varchar(100) [not null]
  email varchar(100) [not null, unique]
  bio text
  rating decimal(3,2)
}

Table students {
  id integer [primary key]
  name varchar(100) [not null]
  email varchar(100) [not null, unique]
  enrolled_at timestamp
}

Table enrollments {
  id integer [primary key]
  student_id integer [ref: > students.id]
  course_id integer [ref: > courses.id]
  progress integer [default: 0]
  enrolled_at timestamp
  
  indexes {
    (student_id, course_id) [unique]
  }
}

Table lessons {
  id integer [primary key]
  course_id integer [ref: > courses.id]
  title varchar(200) [not null]
  content text
  video_url varchar(255)
  order_num integer
}

Table lesson_completions {
  id integer [primary key]
  student_id integer [ref: > students.id]
  lesson_id integer [ref: > lessons.id]
  completed_at timestamp
  
  indexes {
    (student_id, lesson_id) [unique]
  }
}
```

## TableGroup

You can group tables visually with DBML `TableGroup`. Grouped tables get a rounded border and label:

```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null]
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200)
}

Table tags {
  id integer [primary key]
  name varchar(50) [not null, unique]
}

TableGroup content {
  users
  posts
  tags
}
```

## Why visualize

1. **Clarity** — see the full database structure at a glance
2. **Relationships** — all foreign keys shown as lines with markers
3. **Cardinality** — 1:N, N:1, 1:1, N:M shown on the lines
4. **Interactivity** — hover a table to highlight its relationships
5. **Zoom** — scale the diagram in and out
6. **Professional look** — similar to dbdiagram.io or Lucidchart
