# Table groups

Group tables visually with DBML `TableGroup`. The group is shown as a rounded border with a label.

**Interactive behavior:**
- **Drag any table** in a group — all tables in that group move together
- **Group resizes** — the border automatically expands when you move tables inside the group

```dbml
Table users {
  id integer [primary key]
  username varchar(50) [not null]
  email varchar(100) [unique]
}

Table roles {
  id integer [primary key]
  name varchar(50) [not null]
}

Table user_roles {
  user_id integer [ref: > users.id]
  role_id integer [ref: > roles.id]
}

Table products {
  id integer [primary key]
  name varchar(200) [not null]
  price decimal(10,2)
  category_id integer [ref: > categories.id]
}

Table categories {
  id integer [primary key]
  name varchar(100) [not null]
}

Table orders {
  id integer [primary key]
  user_id integer [ref: > users.id]
  total decimal(10,2)
  status varchar(20)
}

Table order_items {
  id integer [primary key]
  order_id integer [ref: > orders.id]
  product_id integer [ref: > products.id]
  quantity integer
}

TableGroup identity {
  users
  roles
  user_roles
}

TableGroup catalog {
  products
  categories
}

TableGroup sales {
  orders
  order_items
}
```

Drag a table in any group to see the whole group move and the border update.
