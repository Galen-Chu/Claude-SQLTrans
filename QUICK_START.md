# SQLTrans Quick Start Guide

**Get up and running in 5 minutes!**

---

## Installation (1 minute)

```bash
pip install sqltrans
```

Verify:
```bash
sqltrans --version
```

---

## Launch (30 seconds)

```bash
sqltrans
```

Or with a specific database:
```bash
sqltrans --dialect postgresql
sqltrans --dialect oracle
sqltrans --dialect generic
```

---

## Your First Query (2 minutes)

### Example: Find Customer by Email

**What you want:** Find customer with email `john.doe@example.com`

**Steps:**
```
1. Tab to Table Name → Type: customers
2. Tab to Column (Filter section) → Type: email
3. Tab to Operator → Select: =
4. Tab to Value → Type: john.doe@example.com
5. Click [Add Filter]
6. Press 'c' to copy
```

**Result:**
```sql
SELECT *
FROM "customers"
WHERE "email" = 'john.doe@example.com'
```

**Done!** Paste into your database tool and run.

---

## Keyboard Shortcuts

```
c  = Copy SQL to clipboard
n  = New query (clear all)
q  = Quit
?  = Help
Tab = Navigate fields
```

---

## Common Queries Cheat Sheet

### 1. Find by ID
```
Table: users
Filter: id = 12345
```
→ `SELECT * FROM "users" WHERE "id" = 12345`

### 2. Find Active Records
```
Table: customers
Filter: status = active
```
→ `SELECT * FROM "customers" WHERE "status" = 'active'`

### 3. Recent Records
```
Table: orders
Filter: created_at > 2024-11-01
```
→ `SELECT * FROM "orders" WHERE "created_at" > '2024-11-01'`

### 4. Search by Pattern
```
Table: users
Filter: name LIKE %Smith%
```
→ `SELECT * FROM "users" WHERE "name" LIKE '%Smith%'`

### 5. Multiple IDs
```
Table: products
Filter: id IN 1,2,3,4,5
```
→ `SELECT * FROM "products" WHERE "id" IN (1, 2, 3, 4, 5)`

### 6. Not Null
```
Table: users
Filter: verified_at IS NOT NULL
```
→ `SELECT * FROM "users" WHERE "verified_at" IS NOT NULL`

---

## Operators Quick Reference

| Operator | Example | Meaning |
|----------|---------|---------|
| `=` | `status = active` | Equals |
| `!=` | `status != deleted` | Not equals |
| `>` | `total > 100` | Greater than |
| `>=` | `age >= 18` | Greater or equal |
| `<` | `price < 50` | Less than |
| `<=` | `score <= 100` | Less or equal |
| `LIKE` | `name LIKE %Smith%` | Pattern match |
| `IN` | `id IN 1,2,3` | In list |
| `IS NULL` | `deleted_at IS NULL` | Is null |
| `IS NOT NULL` | `email IS NOT NULL` | Not null |

---

## LIKE Pattern Examples

| Pattern | Matches |
|---------|---------|
| `%Smith%` | Contains "Smith" anywhere |
| `Smith%` | Starts with "Smith" |
| `%Smith` | Ends with "Smith" |
| `%@example.com` | Email at example.com |

---

## 3-Panel Layout

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                                │
├─────────────────────────────────────────────────────────────┤
│ LEFT              │ CENTER             │ RIGHT              │
│                   │                    │                    │
│ Table & Columns   │ Filters (WHERE)    │ SQL Preview        │
│                   │                    │                    │
│ • Table name      │ • Column name      │ Live SQL output    │
│ • Column list     │ • Operator         │ [Copy] [Save]      │
│                   │ • Value            │                    │
│                   │ • Active filters   │                    │
└───────────────────┴────────────────────┴────────────────────┘
```

---

## Typical Workflow

```
┌─────────────────────┐
│ 1. Enter table name │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 2. Add columns      │
│    (or skip for *)  │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 3. Add filters      │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 4. Press 'c' to     │
│    copy SQL         │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 5. Paste & run in   │
│    database tool    │
└─────────────────────┘
```

---

## Support Engineer Workflow

**Customer calls: "I can't find my order"**

```
Step 1: Find customer
  Table: customers
  Filter: email = customer@email.com
  Copy & run → Get customer_id

Step 2: Find their orders
  Table: orders
  Filter: customer_id = [from step 1]
  Filter: created_at > 2024-10-01
  Copy & run → Show customer their orders
```

---

## Tips

### 💡 Tip 1: Use Tab to navigate
Don't use mouse - just Tab → Type → Enter

### 💡 Tip 2: Start simple
- Add table
- Add one filter
- Test it
- Add more filters

### 💡 Tip 3: SELECT * first
Leave columns empty to see all data first

### 💡 Tip 4: Copy often
Press 'c' after each change to test

### 💡 Tip 5: Multiple filters = AND
All filters must match:
```
Filter 1: status = active
Filter 2: total > 100
→ Status must be active AND total must be > 100
```

---

## Need More Help?

**Full Tutorial:**
- `TUTORIAL.md` - Detailed step-by-step guide

**Documentation:**
- `docs/user-guide.md` - Complete user manual
- `examples/sample_queries.md` - 30+ examples

**In the app:**
- Press `?` for help screen

**Online:**
- GitHub: https://github.com/Galen-Chu/Claude-SQLTrans
- Issues: Report bugs or ask questions

---

## Summary Card (Print This!)

```
┌──────────────────────────────────────────────────┐
│              SQLTRANS QUICK CARD                 │
├──────────────────────────────────────────────────┤
│                                                  │
│ LAUNCH:  sqltrans                                │
│          sqltrans --dialect postgresql           │
│                                                  │
│ SHORTCUTS:                                       │
│   c = Copy    n = New    q = Quit    ? = Help   │
│                                                  │
│ WORKFLOW:                                        │
│   1. Table name                                  │
│   2. Columns (or empty for *)                    │
│   3. Filters                                     │
│   4. Press 'c' to copy                           │
│                                                  │
│ OPERATORS:                                       │
│   =  !=  >  >=  <  <=                           │
│   LIKE  IN  IS NULL  IS NOT NULL                │
│                                                  │
│ LIKE PATTERNS:                                   │
│   %word%  = contains "word"                      │
│   word%   = starts with "word"                   │
│   %word   = ends with "word"                     │
│                                                  │
│ IN FORMAT:                                       │
│   Numbers: 1,2,3,4,5                             │
│   Strings: active,pending,completed              │
│                                                  │
│ TIP: All filters combine with AND               │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

**You're ready to go! Launch SQLTrans and start building queries.**

```bash
sqltrans
```

**Happy querying! 🚀**
