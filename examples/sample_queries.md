# Sample SQL Queries

Examples of common queries built with SQLTrans, showing the input steps and resulting SQL.

---

## Table of Contents

1. [Basic Queries](#basic-queries)
2. [Customer Lookups](#customer-lookups)
3. [Order Management](#order-management)
4. [User Management](#user-management)
5. [Pattern Matching](#pattern-matching)
6. [Date Filtering](#date-filtering)
7. [Complex Queries](#complex-queries)

---

## Basic Queries

### Select All from Table

**Inputs:**
```
Dialect: Generic SQL
Table: users
Columns: (none)
Filters: (none)
```

**Generated SQL:**
```sql
SELECT *
FROM "users"
```

**Use Case:** Quick view of all data in a table

---

### Select Specific Columns

**Inputs:**
```
Dialect: PostgreSQL
Table: customers
Columns: id, email, created_at
Filters: (none)
```

**Generated SQL:**
```sql
SELECT "id", "email", "created_at"
FROM "customers"
```

**Use Case:** Get specific fields only

---

## Customer Lookups

### Find Customer by Email

**Inputs:**
```
Dialect: PostgreSQL
Table: customers
Columns: (none - SELECT *)
Filters:
  - Column: email
    Operator: =
    Value: john.doe@example.com
```

**Generated SQL:**
```sql
SELECT *
FROM "customers"
WHERE "email" = 'john.doe@example.com'
```

**Use Case:** Look up customer account for support ticket

**Screenshot (ASCII):**
```
┌────────────────────────────────────────────────────┐
│ Table: customers                                   │
│ Columns: (none - SELECT *)                        │
│                                                    │
│ Filters:                                          │
│   email = 'john.doe@example.com'                  │
│                                                    │
│ SQL: SELECT * FROM "customers"                    │
│      WHERE "email" = 'john.doe@example.com'       │
└────────────────────────────────────────────────────┘
```

---

### Find Customer by ID

**Inputs:**
```
Dialect: Generic SQL
Table: customers
Columns: id, name, email, phone, status
Filters:
  - Column: id
    Operator: =
    Value: 12345
```

**Generated SQL:**
```sql
SELECT "id", "name", "email", "phone", "status"
FROM "customers"
WHERE "id" = 12345
```

**Use Case:** Direct customer lookup by ID

---

### Find Multiple Customers

**Inputs:**
```
Dialect: PostgreSQL
Table: customers
Columns: id, name, email
Filters:
  - Column: id
    Operator: IN
    Value: 1001,1002,1003,1004,1005
```

**Generated SQL:**
```sql
SELECT "id", "name", "email"
FROM "customers"
WHERE "id" IN (1001, 1002, 1003, 1004, 1005)
```

**Use Case:** Batch lookup of multiple customers

---

## Order Management

### Find Recent Orders

**Inputs:**
```
Dialect: PostgreSQL
Table: orders
Columns: id, customer_id, total, status, created_at
Filters:
  - Column: created_at
    Operator: >
    Value: 2024-11-01
```

**Generated SQL:**
```sql
SELECT "id", "customer_id", "total", "status", "created_at"
FROM "orders"
WHERE "created_at" > '2024-11-01'
```

**Use Case:** Find orders from last week/month

---

### Find High-Value Orders

**Inputs:**
```
Dialect: Generic SQL
Table: orders
Columns: id, customer_id, total, created_at
Filters:
  - Column: total
    Operator: >=
    Value: 1000
```

**Generated SQL:**
```sql
SELECT "id", "customer_id", "total", "created_at"
FROM "orders"
WHERE "total" >= 1000
```

**Use Case:** Find orders above certain amount for review

---

### Find Pending Orders

**Inputs:**
```
Dialect: PostgreSQL
Table: orders
Columns: id, customer_id, total, status
Filters:
  - Column: status
    Operator: =
    Value: pending
```

**Generated SQL:**
```sql
SELECT "id", "customer_id", "total", "status"
FROM "orders"
WHERE "status" = 'pending'
```

**Use Case:** Process pending orders

---

### Find Failed Orders in Date Range

**Inputs:**
```
Dialect: PostgreSQL
Table: orders
Columns: id, customer_id, total, status, created_at
Filters:
  - Column: status
    Operator: =
    Value: failed
  - Column: created_at
    Operator: >
    Value: 2024-11-01
```

**Generated SQL:**
```sql
SELECT "id", "customer_id", "total", "status", "created_at"
FROM "orders"
WHERE "status" = 'failed'
  AND "created_at" > '2024-11-01'
```

**Use Case:** Investigate recent payment failures

---

## User Management

### Find Active Users

**Inputs:**
```
Dialect: Generic SQL
Table: users
Columns: id, username, email, last_login
Filters:
  - Column: status
    Operator: =
    Value: active
```

**Generated SQL:**
```sql
SELECT "id", "username", "email", "last_login"
FROM "users"
WHERE "status" = 'active'
```

**Use Case:** Get list of active users

---

### Find Inactive Users

**Inputs:**
```
Dialect: PostgreSQL
Table: users
Columns: id, username, email, last_login
Filters:
  - Column: last_login
    Operator: <
    Value: 2024-01-01
```

**Generated SQL:**
```sql
SELECT "id", "username", "email", "last_login"
FROM "users"
WHERE "last_login" < '2024-01-01'
```

**Use Case:** Find users who haven't logged in this year

---

### Find Users Without Email Verification

**Inputs:**
```
Dialect: PostgreSQL
Table: users
Columns: id, email, created_at
Filters:
  - Column: verified_at
    Operator: IS NULL
```

**Generated SQL:**
```sql
SELECT "id", "email", "created_at"
FROM "users"
WHERE "verified_at" IS NULL
```

**Use Case:** Send verification reminder emails

---

### Find Admin Users

**Inputs:**
```
Dialect: Generic SQL
Table: users
Columns: id, username, email, role
Filters:
  - Column: role
    Operator: =
    Value: admin
  - Column: status
    Operator: =
    Value: active
```

**Generated SQL:**
```sql
SELECT "id", "username", "email", "role"
FROM "users"
WHERE "role" = 'admin'
  AND "status" = 'active'
```

**Use Case:** List active administrators

---

## Pattern Matching

### Find Users by Name Pattern

**Inputs:**
```
Dialect: PostgreSQL
Table: users
Columns: id, name, email
Filters:
  - Column: name
    Operator: LIKE
    Value: %Smith%
```

**Generated SQL:**
```sql
SELECT "id", "name", "email"
FROM "users"
WHERE "name" LIKE '%Smith%'
```

**Use Case:** Search for user by partial name

---

### Find Products by Category

**Inputs:**
```
Dialect: Generic SQL
Table: products
Columns: id, name, category, price
Filters:
  - Column: category
    Operator: LIKE
    Value: electronics%
```

**Generated SQL:**
```sql
SELECT "id", "name", "category", "price"
FROM "products"
WHERE "category" LIKE 'electronics%'
```

**Use Case:** Find all electronics products

---

### Find Email Addresses at Domain

**Inputs:**
```
Dialect: PostgreSQL
Table: users
Columns: id, username, email
Filters:
  - Column: email
    Operator: LIKE
    Value: %@example.com
```

**Generated SQL:**
```sql
SELECT "id", "username", "email"
FROM "users"
WHERE "email" LIKE '%@example.com'
```

**Use Case:** Find all users from specific domain

---

## Date Filtering

### Find Records After Date

**Inputs:**
```
Dialect: PostgreSQL
Table: events
Columns: id, event_type, user_id, created_at
Filters:
  - Column: created_at
    Operator: >
    Value: 2024-11-01
```

**Generated SQL:**
```sql
SELECT "id", "event_type", "user_id", "created_at"
FROM "events"
WHERE "created_at" > '2024-11-01'
```

**Use Case:** Get recent events

---

### Find Records Before Date

**Inputs:**
```
Dialect: Generic SQL
Table: subscriptions
Columns: id, user_id, plan, expires_at
Filters:
  - Column: expires_at
    Operator: <
    Value: 2024-12-01
```

**Generated SQL:**
```sql
SELECT "id", "user_id", "plan", "expires_at"
FROM "subscriptions"
WHERE "expires_at" < '2024-12-01'
```

**Use Case:** Find expiring subscriptions

---

## Complex Queries

### Customer Order Investigation

**Scenario:** Support ticket for refund - need to see customer's large orders

**Inputs:**
```
Dialect: PostgreSQL
Table: orders
Columns: id, customer_id, total, status, created_at
Filters:
  - Column: customer_id
    Operator: =
    Value: 12345
  - Column: total
    Operator: >=
    Value: 500
  - Column: status
    Operator: !=
    Value: refunded
```

**Generated SQL:**
```sql
SELECT "id", "customer_id", "total", "status", "created_at"
FROM "orders"
WHERE "customer_id" = 12345
  AND "total" >= 500
  AND "status" != 'refunded'
```

**Use Case:** Verify eligible orders for refund

---

### Active Premium Users

**Scenario:** Marketing campaign targeting active premium users

**Inputs:**
```
Dialect: PostgreSQL
Table: users
Columns: id, email, name, tier, status
Filters:
  - Column: status
    Operator: =
    Value: active
  - Column: tier
    Operator: =
    Value: premium
  - Column: last_login
    Operator: >
    Value: 2024-10-01
```

**Generated SQL:**
```sql
SELECT "id", "email", "name", "tier", "status"
FROM "users"
WHERE "status" = 'active'
  AND "tier" = 'premium'
  AND "last_login" > '2024-10-01'
```

**Use Case:** Target engaged premium users for upsell

---

### Security Audit Query

**Scenario:** Find admin accounts without 2FA

**Inputs:**
```
Dialect: PostgreSQL
Table: users
Columns: id, username, email, role, two_factor_enabled, last_login
Filters:
  - Column: role
    Operator: =
    Value: admin
  - Column: two_factor_enabled
    Operator: =
    Value: false
  - Column: last_login
    Operator: IS NOT NULL
```

**Generated SQL:**
```sql
SELECT "id", "username", "email", "role", "two_factor_enabled", "last_login"
FROM "users"
WHERE "role" = 'admin'
  AND "two_factor_enabled" = 'false'
  AND "last_login" IS NOT NULL
```

**Use Case:** Security compliance check

---

### Abandoned Cart Recovery

**Scenario:** Find abandoned high-value carts for recovery email

**Inputs:**
```
Dialect: Generic SQL
Table: shopping_carts
Columns: id, user_id, user_email, total, last_updated
Filters:
  - Column: status
    Operator: =
    Value: abandoned
  - Column: total
    Operator: >
    Value: 100
  - Column: last_updated
    Operator: >
    Value: 2024-11-04
```

**Generated SQL:**
```sql
SELECT "id", "user_id", "user_email", "total", "last_updated"
FROM "shopping_carts"
WHERE "status" = 'abandoned'
  AND "total" > 100
  AND "last_updated" > '2024-11-04'
```

**Use Case:** Recover abandoned carts with follow-up

---

## Tips for Building Queries

### Start Simple
1. Table name only
2. Add columns
3. Add one filter
4. Add more filters incrementally

### Use SELECT *
- See all columns first
- Then narrow to specific fields

### Test Incrementally
- Build filter by filter
- Verify SQL at each step
- Copy and test in database

### Common Patterns

**Single Record Lookup:**
```
WHERE id = [value]
WHERE email = '[value]'
```

**Date Range:**
```
WHERE created_at > '[date]'
WHERE created_at < '[date]'
```

**Status Filtering:**
```
WHERE status = '[value]'
WHERE status != '[value]'
WHERE status IN (value1, value2, value3)
```

**Pattern Search:**
```
WHERE name LIKE '%[term]%'        -- Contains
WHERE name LIKE '[term]%'         -- Starts with
WHERE name LIKE '%[term]'         -- Ends with
```

**Null Checks:**
```
WHERE field IS NULL               -- Missing data
WHERE field IS NOT NULL           -- Has data
```

---

## Dialect Differences

### PostgreSQL
```sql
SELECT "id", "email"
FROM "customers"
WHERE "name" = 'O''Reilly'
```
- Double quotes for identifiers
- Single quotes for strings
- `''` escapes single quote

### Oracle
```sql
SELECT "id", "email"
FROM "Customers"
WHERE "Name" = 'O''Reilly'
```
- Case-sensitive with quotes
- Same string escaping as PostgreSQL

### Generic SQL
```sql
SELECT "id", "email"
FROM "customers"
WHERE "name" = 'O''Reilly'
```
- ANSI SQL-92 standard
- Works with most databases

---

**Ready to build? Launch SQLTrans and try these examples!**

```bash
sqltrans
```
