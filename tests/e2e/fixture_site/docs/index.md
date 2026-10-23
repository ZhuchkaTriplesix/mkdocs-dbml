# Home

```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null, unique]
  email varchar(255) [note: 'login email']
  Note: 'Application users'
  indexes {
    email [unique]
  }
}

Table posts {
  id integer [primary key]
  user_id integer [ref: > users.id]
  title varchar(200) [not null]
}

Table comments {
  id integer [primary key]
  post_id integer [ref: > posts.id]
  user_id integer [ref: > users.id]
  body text
}
```

## Groups

```dbml
Table hub {
  id integer [primary key]
}

Table spoke_a {
  id integer [primary key]
  hub_id integer [ref: > hub.id]
}

Table spoke_b {
  id integer [primary key]
  hub_id integer [ref: > hub.id]
}

Table spoke_c {
  id integer [primary key]
  hub_id integer [ref: > hub.id]
}

TableGroup edge {
  spoke_a
  spoke_c
}
```

[Other page](other.md)
