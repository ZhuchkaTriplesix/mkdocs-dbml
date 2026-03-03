# Usage examples

## E-commerce system

A more complex example for an online store:

```dbml
Table customers {
  id integer [primary key]
  email varchar(255) [not null, unique]
  first_name varchar(100)
  last_name varchar(100)
  phone varchar(20)
  created_at timestamp [default: `now()`]
  
  indexes {
    email [unique]
  }
  
  Note: 'Store customers'
}

Table products {
  id integer [primary key]
  name varchar(200) [not null]
  description text
  price decimal(10,2) [not null]
  stock_quantity integer [default: 0]
  category_id integer [ref: > categories.id]
  created_at timestamp [default: `now()`]
  
  indexes {
    category_id
    name
  }
  
  Note: 'Product catalog'
}

Table categories {
  id integer [primary key]
  name varchar(100) [not null, unique]
  parent_id integer [ref: > categories.id]
  
  Note: 'Product categories (supports nesting)'
}

Table orders {
  id integer [primary key]
  customer_id integer [ref: > customers.id]
  status varchar(20) [not null, default: 'pending']
  total_amount decimal(10,2) [not null]
  created_at timestamp [default: `now()`]
  updated_at timestamp
  
  indexes {
    customer_id
    (customer_id, created_at)
    status
  }
  
  Note: 'Customer orders'
}

Table order_items {
  id integer [primary key]
  order_id integer [ref: > orders.id]
  product_id integer [ref: > products.id]
  quantity integer [not null]
  price decimal(10,2) [not null]
  
  indexes {
    (order_id, product_id) [unique]
  }
  
  Note: 'Order line items'
}

Table reviews {
  id integer [primary key]
  product_id integer [ref: > products.id]
  customer_id integer [ref: > customers.id]
  rating integer [not null]
  comment text
  created_at timestamp [default: `now()`]
  
  indexes {
    product_id
    customer_id
  }
  
  Note: 'Product reviews'
}
```

## Task management system

```dbml
Table projects {
  id integer [primary key]
  name varchar(200) [not null]
  description text
  owner_id integer [ref: > users.id]
  status varchar(20) [default: 'active']
  created_at timestamp [default: `now()`]
}

Table users {
  id integer [primary key]
  username varchar(50) [not null, unique]
  email varchar(100) [not null, unique]
  role varchar(20) [default: 'member']
}

Table tasks {
  id integer [primary key]
  project_id integer [ref: > projects.id]
  title varchar(200) [not null]
  description text
  assignee_id integer [ref: > users.id]
  status varchar(20) [default: 'todo']
  priority varchar(20) [default: 'medium']
  due_date date
  created_at timestamp [default: `now()`]
  
  indexes {
    project_id
    assignee_id
    (project_id, status)
  }
}

Table task_comments {
  id integer [primary key]
  task_id integer [ref: > tasks.id]
  user_id integer [ref: > users.id]
  comment text [not null]
  created_at timestamp [default: `now()`]
}
```

## Benefits

1. **Clarity** — the database schema appears right in your docs
2. **Up to date** — easy to keep the schema in sync with code
3. **Understandable** — relationships and constraints are visible at once
4. **Polished** — modern design with responsive layout
