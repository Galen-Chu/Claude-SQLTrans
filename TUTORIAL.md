# SQLTrans Step-by-Step Tutorial

**Welcome to SQLTrans!** This tutorial will guide you through building SQL queries using the interactive interface.

---

## Table of Contents

1. [Installation](#installation)
2. [Your First Query](#your-first-query)
3. [Tutorial 1: Simple Customer Lookup](#tutorial-1-simple-customer-lookup)
4. [Tutorial 2: Finding Recent Orders](#tutorial-2-finding-recent-orders)
5. [Tutorial 3: Pattern Matching](#tutorial-3-pattern-matching)
6. [Tutorial 4: Using Multiple Filters](#tutorial-4-using-multiple-filters)
7. [Tutorial 5: Working with Lists (IN Operator)](#tutorial-5-working-with-lists-in-operator)
8. [Tutorial 6: NULL Checks](#tutorial-6-null-checks)
9. [Switching Between Databases](#switching-between-databases)
10. [Tips and Tricks](#tips-and-tricks)

---

## Installation

### Option 1: Install with pip (Recommended)

```bash
pip install sqltrans
```

### Option 2: Install from source

```bash
git clone https://github.com/Galen-Chu/Claude-SQLTrans.git
cd Claude-SQLTrans
pip install -e .
```

### Verify Installation

```bash
sqltrans --version
```

You should see: `SQLTrans 0.1.0`

---

## Your First Query

Let's launch SQLTrans and build your first SQL query!

### Step 1: Launch the Application

Open your terminal and run:

```bash
sqltrans
```

Or specify a database dialect:

```bash
sqltrans --dialect postgresql
```

You'll see the interactive interface:

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name:      │ Add Filter:      │ SELECT *             │
│ [            ]   │                  │ FROM ...             │
│                  │ Column: [     ]  │                      │
│ Columns:         │ Operator: [=  ]  │ [Copy]  [Save]       │
│                  │ Value: [      ]  │                      │
│ [Add Column]     │ [Add Filter]     │                      │
│                  │                  │                      │
│                  │ Active Filters:  │                      │
│                  │ (none)           │                      │
└──────────────────┴──────────────────┴──────────────────────┘
│ q: Quit  c: Copy  n: New  ?: Help                          │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Understanding the Interface

The interface has **3 main sections**:

**Left Panel** - Table & Columns
- Enter your table name
- Add columns to SELECT (or leave empty for SELECT *)

**Center Panel** - Filters
- Build WHERE clause conditions
- Add multiple filters (they combine with AND)

**Right Panel** - SQL Preview
- See your SQL update in real-time
- Copy or save the generated SQL

---

## Tutorial 1: Simple Customer Lookup

**Goal:** Find a customer by their email address

**Scenario:** A customer calls support and you need to look up their account.

### Step-by-Step

**Step 1: Select Database Dialect**
- Click on "PostgreSQL" at the top (or press Tab to navigate)

**Step 2: Enter Table Name**
1. Press `Tab` to move to the "Table Name" field
2. Type: `customers`
3. Press `Enter` or `Tab` to continue

**Step 3: Leave Columns Empty**
- We want to see all customer data, so skip the columns section
- This will generate `SELECT *`

**Step 4: Add Email Filter**
1. Press `Tab` to move to the "Column" field under Filters
2. Type: `email`
3. Press `Tab` to move to "Operator"
4. The default `=` is already selected (perfect!)
5. Press `Tab` to move to "Value"
6. Type: `john.doe@example.com`
7. Click `[Add Filter]` or press `Enter`

**Step 5: View the Generated SQL**

The SQL Preview panel now shows:

```sql
SELECT *
FROM "customers"
WHERE "email" = 'john.doe@example.com'
```

**Step 6: Copy the SQL**
- Press `c` on your keyboard (or click the Copy button)
- The SQL is now in your clipboard!
- Paste it into your database tool and run it

### What You Learned
- ✅ How to enter a table name
- ✅ How to use SELECT * (leave columns empty)
- ✅ How to add a simple filter with the = operator
- ✅ How to copy the generated SQL

---

## Tutorial 2: Finding Recent Orders

**Goal:** Find all orders created after November 1st, 2024

**Scenario:** You need to review recent orders for a report.

### Step-by-Step

**Step 1: Start Fresh**
- Press `n` to clear the previous query

**Step 2: Enter Table Name**
1. Tab to "Table Name"
2. Type: `orders`

**Step 3: Select Specific Columns**

We want to see specific order details:

1. Tab to "Column" input (in the left panel)
2. Type: `id`
3. Click `[Add]` or press `Enter`
4. Type: `customer_id`
5. Click `[Add]`
6. Type: `total`
7. Click `[Add]`
8. Type: `created_at`
9. Click `[Add]`

Your columns list now shows:
```
Columns:
  - id         [Remove]
  - customer_id [Remove]
  - total      [Remove]
  - created_at [Remove]
```

**Step 4: Add Date Filter**

1. Tab to the Filter section
2. Column: `created_at`
3. Operator: Click and select `>` (greater than)
4. Value: `2024-11-01`
5. Click `[Add Filter]`

**Step 5: View the Generated SQL**

```sql
SELECT "id", "customer_id", "total", "created_at"
FROM "orders"
WHERE "created_at" > '2024-11-01'
```

**Step 6: Copy and Use**
- Press `c` to copy
- Run in your database!

### What You Learned
- ✅ How to select specific columns
- ✅ How to use the `>` (greater than) operator
- ✅ How to filter by dates
- ✅ How to remove columns (click Remove button)

---

## Tutorial 3: Pattern Matching

**Goal:** Find all users with "Smith" in their name

**Scenario:** A customer remembers part of their name but not the exact spelling.

### Step-by-Step

**Step 1: Start Fresh**
- Press `n` for a new query

**Step 2: Setup**
1. Table: `users`
2. Add columns: `id`, `name`, `email`

**Step 3: Add LIKE Filter**

1. Tab to Filter section
2. Column: `name`
3. Operator: Select `LIKE` from dropdown
4. Value: `%Smith%`
   - The `%` means "any characters"
   - `%Smith%` finds Smith anywhere in the name

5. Click `[Add Filter]`

**Step 4: View Result**

```sql
SELECT "id", "name", "email"
FROM "users"
WHERE "name" LIKE '%Smith%'
```

This will find:
- "John Smith"
- "Smith Jones"
- "Alice Smithson"
- "Bob Blacksmith"

### Pattern Matching Examples

| Pattern | Matches | Example |
|---------|---------|---------|
| `%Smith%` | Smith anywhere | "John Smith", "Smithson" |
| `Smith%` | Starts with Smith | "Smith", "Smithson" |
| `%Smith` | Ends with Smith | "Smith", "Blacksmith" |
| `J%n` | Starts J, ends n | "John", "Jason" |
| `___` | Exactly 3 chars | "Bob", "Amy" |

### What You Learned
- ✅ How to use the LIKE operator
- ✅ How to use wildcards (%, _)
- ✅ Pattern matching techniques

---

## Tutorial 4: Using Multiple Filters

**Goal:** Find high-value, non-cancelled orders from November

**Scenario:** You need to find important orders for review.

### Step-by-Step

**Step 1: Setup**
1. Press `n` for new query
2. Table: `orders`
3. Columns: `id`, `customer_id`, `total`, `status`

**Step 2: Add First Filter (Total)**

1. Column: `total`
2. Operator: `>=` (greater than or equal)
3. Value: `1000`
4. Click `[Add Filter]`

You'll see under "Active Filters":
```
Active Filters:
  - total >= 1000 [Remove]
```

**Step 3: Add Second Filter (Status)**

1. Column: `status`
2. Operator: `!=` (not equal)
3. Value: `cancelled`
4. Click `[Add Filter]`

Active Filters now shows:
```
Active Filters:
  - total >= 1000 [Remove]
  - status != 'cancelled' [Remove]
```

**Step 4: Add Third Filter (Date)**

1. Column: `created_at`
2. Operator: `>`
3. Value: `2024-11-01`
4. Click `[Add Filter]`

**Step 5: View Result**

```sql
SELECT "id", "customer_id", "total", "status"
FROM "orders"
WHERE "total" >= 1000
  AND "status" != 'cancelled'
  AND "created_at" > '2024-11-01'
```

### Understanding Multiple Filters

All filters are combined with **AND**:
- The order must have total >= 1000
- **AND** status must not be cancelled
- **AND** it must be created after Nov 1

All conditions must be true for a row to be returned.

### What You Learned
- ✅ How to add multiple filters
- ✅ How filters combine with AND
- ✅ How to use >=, !=, and > operators
- ✅ How to remove individual filters

---

## Tutorial 5: Working with Lists (IN Operator)

**Goal:** Find specific customers by their IDs

**Scenario:** You have a list of customer IDs from a report.

### Step-by-Step

**Step 1: Setup**
1. Press `n`
2. Table: `customers`
3. Columns: `id`, `name`, `email`

**Step 2: Add IN Filter**

1. Column: `id`
2. Operator: Select `IN`
3. Value: Here's the important part!

**For the IN operator, enter a comma-separated list:**

In the UI, you would type: `1001,1002,1003,1004,1005`

But SQLTrans is smart - it will convert this to proper SQL format!

4. Click `[Add Filter]`

**Step 3: View Result**

```sql
SELECT "id", "name", "email"
FROM "customers"
WHERE "id" IN (1001, 1002, 1003, 1004, 1005)
```

Notice how it:
- Added parentheses
- Formatted the list properly
- Added proper spacing

### IN Operator Examples

**Numbers:**
```
Input:  1,2,3,4,5
Output: WHERE "id" IN (1, 2, 3, 4, 5)
```

**Strings:**
```
Input:  pending,active,processing
Output: WHERE "status" IN ('pending', 'active', 'processing')
```

### What You Learned
- ✅ How to use the IN operator
- ✅ How to format lists (comma-separated)
- ✅ Works with both numbers and strings

---

## Tutorial 6: NULL Checks

**Goal:** Find users who haven't verified their email

**Scenario:** You need to send reminder emails to unverified users.

### Step-by-Step

**Step 1: Setup**
1. Press `n`
2. Table: `users`
3. Columns: `id`, `email`, `created_at`

**Step 2: Add IS NULL Filter**

1. Column: `verified_at`
2. Operator: Select `IS NULL`
3. Value: **Leave empty!**
   - For IS NULL and IS NOT NULL, no value is needed
   - The value field will be disabled

4. Click `[Add Filter]`

**Step 3: Add Second NULL Check**

To exclude deleted users:

1. Column: `deleted_at`
2. Operator: `IS NULL`
3. Value: (empty)
4. Click `[Add Filter]`

**Step 4: View Result**

```sql
SELECT "id", "email", "created_at"
FROM "users"
WHERE "verified_at" IS NULL
  AND "deleted_at" IS NULL
```

This finds users who:
- Haven't verified (verified_at is NULL)
- Haven't been deleted (deleted_at is NULL)

### NULL Operators

**IS NULL** - Field has no value
```sql
WHERE "field" IS NULL
```

**IS NOT NULL** - Field has a value
```sql
WHERE "field" IS NOT NULL
```

### Common Use Cases

| Use Case | Operator | Example |
|----------|----------|---------|
| Not verified | IS NULL | `verified_at IS NULL` |
| Has verified | IS NOT NULL | `verified_at IS NOT NULL` |
| Not deleted | IS NULL | `deleted_at IS NULL` |
| Has phone number | IS NOT NULL | `phone IS NOT NULL` |

### What You Learned
- ✅ How to use IS NULL operator
- ✅ How to use IS NOT NULL operator
- ✅ NULL operators don't need values
- ✅ Finding missing or present data

---

## Switching Between Databases

SQLTrans supports multiple database dialects. Here's how they differ:

### PostgreSQL

**When to use:** Working with PostgreSQL databases

**Example:**
```sql
SELECT "id", "email"
FROM "customers"
WHERE "name" = 'O''Reilly'
```

**Features:**
- Double quotes for identifiers
- Single quotes escaped with `''`

### Oracle

**When to use:** Working with Oracle databases

**Example:**
```sql
SELECT "OrderID", "CustomerID"
FROM "Orders"
WHERE "Status" = 'PENDING'
```

**Features:**
- Case-sensitive identifiers
- Preserves your exact capitalization

### Generic SQL

**When to use:** MySQL, SQLite, SQL Server, or any ANSI SQL database

**Example:**
```sql
SELECT "id", "email"
FROM "customers"
WHERE "active" = 1
```

**Features:**
- ANSI SQL-92 standard
- Works with most databases

### How to Switch

**Method 1: In the UI**
1. Click on the dialect radio button at the top
2. The SQL regenerates automatically

**Method 2: Command Line**
```bash
sqltrans --dialect postgresql
sqltrans --dialect oracle
sqltrans --dialect generic
```

---

## Tips and Tricks

### Keyboard Shortcuts (Super Important!)

| Key | Action | When to Use |
|-----|--------|-------------|
| `Tab` | Next field | Navigate without mouse |
| `Shift+Tab` | Previous field | Go back |
| `c` | Copy SQL | Quick copy to clipboard |
| `n` | New query | Start fresh |
| `q` | Quit | Exit application |
| `?` | Help | Show help screen |
| `Enter` | Submit | Add column/filter |

### Pro Tips

**Tip 1: Use Tab Navigation**
```
Tab → Tab → Type → Enter → Tab → Tab → Type → Enter
```
Much faster than using the mouse!

**Tip 2: Start Simple, Add Complexity**
```
1. Add table first
2. Test with SELECT *
3. Add one filter
4. Test the SQL
5. Add more filters
6. Add specific columns
```

**Tip 3: Copy Early and Often**
Press `c` after each change to test in your database.

**Tip 4: Use Descriptive Column Names**
If your database has columns like:
- `usr_eml` → Still type `usr_eml` exactly
- `CustomerEmail` → Match the case for Oracle

**Tip 5: Pattern Matching Power**
```
Starts with: name%
Ends with:   %name
Contains:    %name%
Exact:       name
```

**Tip 6: Remove Wrong Filters**
Each filter has a `[Remove]` button - use it to fix mistakes!

### Common Workflows

**Support Engineer Workflow:**
```
1. Customer email → Table: customers, Filter: email = value
2. Find customer_id from results
3. New query → Table: orders, Filter: customer_id = value
4. Review order history
5. Copy SQL for documentation
```

**Data Analysis Workflow:**
```
1. Start with date range
2. Add status filter
3. Add value filter
4. Export SQL
5. Run in database tool
6. Analyze results
```

---

## Practice Exercises

Try building these queries yourself:

### Exercise 1: Basic
**Task:** Find all active products
- Table: `products`
- Filter: `status = 'active'`

### Exercise 2: Date Range
**Task:** Find orders from the last month
- Table: `orders`
- Filter: `created_at > '2024-10-01'`

### Exercise 3: Multiple Conditions
**Task:** Find premium active users who logged in recently
- Table: `users`
- Filters:
  - `tier = 'premium'`
  - `status = 'active'`
  - `last_login > '2024-11-01'`

### Exercise 4: Pattern Match
**Task:** Find all emails from example.com domain
- Table: `users`
- Filter: `email LIKE '%@example.com'`

### Exercise 5: Complex
**Task:** Find high-value, recent, non-cancelled orders for active customers
- Table: `orders`
- Filters:
  - `total >= 500`
  - `created_at > '2024-11-01'`
  - `status != 'cancelled'`

---

## Troubleshooting

### Problem: "Invalid identifier" error

**Solution:**
- Check that your table/column name starts with a letter
- Only use letters, numbers, and underscores
- No spaces or special characters

### Problem: Filter won't add

**Solution:**
- Make sure you filled in all required fields
- For IS NULL/IS NOT NULL, leave value empty
- For other operators, value is required

### Problem: SQL looks wrong

**Solution:**
- Check your selected dialect (top of screen)
- Verify filter operators
- Remove and re-add problematic filters

### Problem: Copy doesn't work

**Solution:**
```bash
# Linux - install clipboard tool
sudo apt-get install xclip

# Use Save instead
Click [Save] button and save to file
```

### Problem: Can't find my table

**Solution:**
- SQLTrans doesn't connect to databases
- It only generates SQL
- Make sure you type the exact table name from your database

---

## Next Steps

### 1. Read the Full User Guide
```
docs/user-guide.md
```
Comprehensive guide with all features

### 2. Check Example Queries
```
examples/sample_queries.md      - 30+ example queries
examples/support_scenarios.md   - Real-world scenarios
```

### 3. Try Real Scenarios
Start using SQLTrans for your actual work:
- Customer lookups
- Order investigations
- User management
- Data analysis

### 4. Customize Your Config
```
~/.sqltrans/config.toml
```
Set your default dialect, theme, and preferences

---

## Quick Reference Card

### Operators

| Operator | Use For | Example |
|----------|---------|---------|
| = | Exact match | `status = 'active'` |
| != | Not equal | `status != 'deleted'` |
| > | Greater than | `total > 100` |
| >= | Greater or equal | `age >= 18` |
| < | Less than | `price < 50` |
| <= | Less or equal | `score <= 100` |
| LIKE | Pattern match | `name LIKE '%Smith%'` |
| IN | Match list | `id IN (1,2,3)` |
| IS NULL | No value | `deleted_at IS NULL` |
| IS NOT NULL | Has value | `email IS NOT NULL` |

### Keyboard Shortcuts

```
Tab       - Next field
Shift+Tab - Previous field
Enter     - Submit/Add
c         - Copy SQL
n         - New query
q         - Quit
?         - Help
```

### Workflow

```
1. Select dialect
2. Enter table
3. Add columns (or leave empty)
4. Add filters
5. Press 'c' to copy
6. Paste in database tool
7. Run query
```

---

## Getting Help

**In the App:**
- Press `?` for help screen

**Documentation:**
- User Guide: `docs/user-guide.md`
- Development: `docs/development.md`

**Support:**
- GitHub Issues: https://github.com/Galen-Chu/Claude-SQLTrans/issues
- Email: support@sqltrans.com

---

**Congratulations!** You've completed the SQLTrans tutorial. You're now ready to build SQL queries efficiently and safely!

**Happy querying! 🚀**

---

*SQLTrans v0.1.0 - Interactive SQL Query Builder*
*For support engineers who need SQL, fast.*
