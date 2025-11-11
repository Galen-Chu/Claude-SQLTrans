# Support Engineer Scenarios

Real-world troubleshooting scenarios showing how to use SQLTrans for customer support.

---

## Table of Contents

1. [Account Issues](#account-issues)
2. [Order Problems](#order-problems)
3. [Payment Investigations](#payment-investigations)
4. [Data Integrity](#data-integrity)
5. [Performance Issues](#performance-issues)
6. [Security Audits](#security-audits)

---

## Account Issues

### Scenario 1: Can't Login - Account Lookup

**Ticket:** "Customer reports they can't log in with email john@example.com"

**Goal:** Verify account exists and check status

**SQLTrans Steps:**
1. Launch: `sqltrans --dialect postgresql`
2. Table: `users`
3. Columns: (leave empty for SELECT *)
4. Filter: `email` = `john@example.com`
5. Press `c` to copy

**Generated SQL:**
```sql
SELECT *
FROM "users"
WHERE "email" = 'john@example.com'
```

**Next Steps:**
- Run in database
- Check `status` field
- Check `password_reset_required` field
- Check `locked_at` field
- Provide findings to customer

---

### Scenario 2: Email Not Verified

**Ticket:** "Customer needs verification email resent"

**Goal:** Confirm email not verified and get user details

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `users`
3. Columns: `id`, `email`, `created_at`
4. Filter: `email` = `jane.smith@example.com`
5. Filter: `verified_at` IS NULL

**Generated SQL:**
```sql
SELECT "id", "email", "created_at"
FROM "users"
WHERE "email" = 'jane.smith@example.com'
  AND "verified_at" IS NULL
```

**Action:** Trigger verification email resend

---

### Scenario 3: Duplicate Account Check

**Ticket:** "Customer says they have multiple accounts"

**Goal:** Find all accounts with similar email

**SQLTrans Steps:**
1. Dialect: `Generic SQL`
2. Table: `users`
3. Columns: `id`, `email`, `username`, `created_at`
4. Filter: `email` LIKE `%john.doe%`

**Generated SQL:**
```sql
SELECT "id", "email", "username", "created_at"
FROM "users"
WHERE "email" LIKE '%john.doe%'
```

**Alternative:** Search by name pattern
- Filter: `name` LIKE `%John Doe%`

---

## Order Problems

### Scenario 4: Missing Order

**Ticket:** "Customer can't find order #45678"

**Goal:** Verify order exists and check status

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `orders`
3. Columns: `id`, `customer_id`, `status`, `total`, `created_at`
4. Filter: `id` = `45678`

**Generated SQL:**
```sql
SELECT "id", "customer_id", "status", "total", "created_at"
FROM "orders"
WHERE "id" = 45678
```

**If Not Found:** Check customer's other orders
- Change filter: `customer_id` = `[id from account lookup]`
- Filter: `created_at` > `2024-11-01`

---

### Scenario 5: Order Status Investigation

**Ticket:** "Order placed 3 days ago still shows 'processing'"

**Goal:** Find stuck orders for customer

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `orders`
3. Columns: `id`, `status`, `created_at`, `updated_at`
4. Filter: `customer_id` = `12345`
5. Filter: `status` = `processing`
6. Filter: `created_at` < `2024-11-08` (3 days ago)

**Generated SQL:**
```sql
SELECT "id", "status", "created_at", "updated_at"
FROM "orders"
WHERE "customer_id" = 12345
  AND "status" = 'processing'
  AND "created_at" < '2024-11-08'
```

**Action:** Escalate to fulfillment team

---

### Scenario 6: Refund Eligibility Check

**Ticket:** "Customer requesting refund for order"

**Goal:** Verify order and check if already refunded

**SQLTrans Steps:**
1. Dialect: `Generic SQL`
2. Table: `orders`
3. Columns: `id`, `customer_id`, `total`, `status`, `created_at`
4. Filter: `id` = `45678`
5. Filter: `status` != `refunded`

**Generated SQL:**
```sql
SELECT "id", "customer_id", "total", "status", "created_at"
FROM "orders"
WHERE "id" = 45678
  AND "status" != 'refunded'
```

**Next:** Check refund policy (within 30 days, etc.)

---

## Payment Investigations

### Scenario 7: Failed Payment Investigation

**Ticket:** "Payment failed, but customer says card should work"

**Goal:** Find payment attempts for order

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `payment_attempts`
3. Columns: `id`, `order_id`, `status`, `error_message`, `created_at`
4. Filter: `order_id` = `45678`

**Generated SQL:**
```sql
SELECT "id", "order_id", "status", "error_message", "created_at"
FROM "payment_attempts"
WHERE "order_id" = 45678
```

**Analysis:** Review error_message for details

---

### Scenario 8: Multiple Failed Payments

**Ticket:** "Customer's card keeps declining"

**Goal:** Find all failed payments for customer

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `payment_attempts`
3. Columns: `id`, `order_id`, `status`, `error_message`, `created_at`
4. Filter: `customer_id` = `12345`
5. Filter: `status` = `failed`
6. Filter: `created_at` > `2024-11-01`

**Generated SQL:**
```sql
SELECT "id", "order_id", "status", "error_message", "created_at"
FROM "payment_attempts"
WHERE "customer_id" = 12345
  AND "status" = 'failed'
  AND "created_at" > '2024-11-01'
```

**Action:** Check for pattern in error messages

---

### Scenario 9: Subscription Payment Status

**Ticket:** "Is my subscription payment current?"

**Goal:** Check subscription payment status

**SQLTrans Steps:**
1. Dialect: `Generic SQL`
2. Table: `subscriptions`
3. Columns: `id`, `user_id`, `plan`, `status`, `current_period_end`
4. Filter: `user_id` = `12345`
5. Filter: `status` = `active`

**Generated SQL:**
```sql
SELECT "id", "user_id", "plan", "status", "current_period_end"
FROM "subscriptions"
WHERE "user_id" = 12345
  AND "status" = 'active'
```

---

## Data Integrity

### Scenario 10: Orphaned Records

**Ticket:** Internal - Data cleanup needed

**Goal:** Find orders without valid customer

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `orders`
3. Columns: `id`, `customer_id`, `total`, `created_at`
4. Filter: `customer_id` IS NULL

**Generated SQL:**
```sql
SELECT "id", "customer_id", "total", "created_at"
FROM "orders"
WHERE "customer_id" IS NULL
```

**Action:** Review and clean up

---

### Scenario 11: Missing Required Data

**Ticket:** Internal - Find incomplete user profiles

**Goal:** Users without phone numbers

**SQLTrans Steps:**
1. Dialect: `Generic SQL`
2. Table: `users`
3. Columns: `id`, `email`, `phone`, `created_at`
4. Filter: `phone` IS NULL
5. Filter: `status` = `active`

**Generated SQL:**
```sql
SELECT "id", "email", "phone", "created_at"
FROM "users"
WHERE "phone" IS NULL
  AND "status" = 'active'
```

**Action:** Send reminder to complete profile

---

## Performance Issues

### Scenario 12: High-Value Transaction Review

**Ticket:** Internal - Review large transactions

**Goal:** Find orders over $5000 this month

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `orders`
3. Columns: `id`, `customer_id`, `total`, `created_at`
4. Filter: `total` >= `5000`
5. Filter: `created_at` > `2024-11-01`

**Generated SQL:**
```sql
SELECT "id", "customer_id", "total", "created_at"
FROM "orders"
WHERE "total" >= 5000
  AND "created_at" > '2024-11-01'
```

**Use:** Fraud detection, VIP customer service

---

### Scenario 13: API Rate Limiting Check

**Ticket:** "Customer says API key not working"

**Goal:** Check API usage for customer

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `api_requests`
3. Columns: `id`, `api_key`, `endpoint`, `status`, `created_at`
4. Filter: `api_key` = `abc123...`
5. Filter: `created_at` > `2024-11-11 00:00:00` (today)

**Generated SQL:**
```sql
SELECT "id", "api_key", "endpoint", "status", "created_at"
FROM "api_requests"
WHERE "api_key" = 'abc123...'
  AND "created_at" > '2024-11-11 00:00:00'
```

**Analysis:** Count requests, check for rate limit errors

---

## Security Audits

### Scenario 14: Admin Account Review

**Ticket:** Internal - Security audit

**Goal:** Find all active admin accounts

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `users`
3. Columns: `id`, `username`, `email`, `role`, `last_login`
4. Filter: `role` = `admin`
5. Filter: `status` = `active`

**Generated SQL:**
```sql
SELECT "id", "username", "email", "role", "last_login"
FROM "users"
WHERE "role" = 'admin'
  AND "status" = 'active'
```

**Review:** Verify all admins are authorized

---

### Scenario 15: Inactive Admin Accounts

**Ticket:** Internal - Security compliance

**Goal:** Find admins who haven't logged in recently

**SQLTrans Steps:**
1. Dialect: `PostgreSQL`
2. Table: `users`
3. Columns: `id`, `username`, `email`, `role`, `last_login`
4. Filter: `role` = `admin`
5. Filter: `last_login` < `2024-10-01`

**Generated SQL:**
```sql
SELECT "id", "username", "email", "role", "last_login"
FROM "users"
WHERE "role" = 'admin'
  AND "last_login" < '2024-10-01'
```

**Action:** Disable inactive admin accounts

---

### Scenario 16: Failed Login Attempts

**Ticket:** "Account locked after multiple login attempts"

**Goal:** Check failed login history

**SQLTrans Steps:**
1. Dialect: `Generic SQL`
2. Table: `login_attempts`
3. Columns: `id`, `user_id`, `email`, `success`, `ip_address`, `created_at`
4. Filter: `email` = `customer@example.com`
5. Filter: `success` = `false`
6. Filter: `created_at` > `2024-11-11`

**Generated SQL:**
```sql
SELECT "id", "user_id", "email", "success", "ip_address", "created_at"
FROM "login_attempts"
WHERE "email" = 'customer@example.com'
  AND "success" = 'false'
  AND "created_at" > '2024-11-11'
```

**Analysis:** Check for brute force attempts, verify IP addresses

---

## Tips for Support Engineers

### Query Building Strategy

**1. Start with the Account**
- Always begin with user/customer lookup
- Get the customer_id for subsequent queries

**2. Narrow the Time Window**
- Use date filters to limit results
- Recent issues: last 7-30 days
- Historical: specific date range

**3. Check Related Tables**
- Orders → Payments
- Users → Subscriptions
- Customers → Orders

**4. Verify Before Action**
- Always verify data before making changes
- Check current state first
- Document findings in ticket

### Common Workflows

**Account Issue Workflow:**
1. Look up user by email
2. Check account status
3. Review recent activity
4. Check related orders/subscriptions

**Order Issue Workflow:**
1. Look up order by ID
2. Verify customer ownership
3. Check order status/history
4. Review payment attempts

**Payment Issue Workflow:**
1. Find order
2. Check payment attempts
3. Review error messages
4. Check customer payment methods

### Safety Tips

**Always:**
- Use read-only queries
- Verify customer identity first
- Document queries and findings
- Test on staging when possible

**Never:**
- Run UPDATE or DELETE queries from SQLTrans
- Share customer data externally
- Modify production without approval
- Skip verification steps

### Efficiency Tips

**Use Keyboard Shortcuts:**
- `Tab` to navigate fields
- `c` to copy SQL instantly
- `n` to start fresh query
- `?` for help anytime

**Save Common Queries:**
- Keep a file of frequent patterns
- Document customer-specific queries
- Share useful queries with team

**Multi-Database Support:**
- Switch dialects for different customers
- Test query in correct dialect
- Save per-customer dialect preferences

---

## Quick Reference

### Most Common Queries

```
1. User Lookup
   Table: users
   Filter: email = '[value]'

2. Order Status
   Table: orders
   Filter: id = [value]

3. Recent Activity
   Table: [any]
   Filter: created_at > '[date]'

4. Status Check
   Table: [any]
   Filter: status = '[value]'

5. Customer Orders
   Table: orders
   Filter: customer_id = [value]
   Filter: created_at > '[date]'
```

### Field Names to Know

**Users Table:**
- id, email, username
- status, role
- created_at, last_login
- verified_at, deleted_at

**Orders Table:**
- id, customer_id
- status, total
- created_at, updated_at
- payment_status

**Common Status Values:**
- active, inactive
- pending, processing, completed
- failed, cancelled, refunded
- verified, unverified

---

**Ready to help customers? Launch SQLTrans!**

```bash
sqltrans --dialect postgresql
```
