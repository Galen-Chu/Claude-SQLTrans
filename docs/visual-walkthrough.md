# SQLTrans Visual Walkthrough

**See exactly what to do at each step with visual screenshots!**

---

## Walkthrough 1: Simple Customer Lookup

**Goal:** Find customer with email `john.doe@example.com`

---

### Step 1: Launch SQLTrans

**Command:**
```bash
sqltrans --dialect postgresql
```

**What you see:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │  ← Dialect selected
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name:      │ Add Filter:      │                      │
│ ┌──────────────┐ │                  │ (No SQL yet)         │
│ │ █            │ │ Column: ┌─────┐  │                      │
│ └──────────────┘ │         └─────┘  │                      │
│     ▲            │ Operator: ┌───┐  │                      │
│     └─ Cursor    │           │ = │  │                      │
│                  │           └───┘  │                      │
│ Columns:         │ Value: ┌───────┐ │                      │
│ (none yet)       │        └───────┘ │                      │
│                  │                  │                      │
│ ┌──────────────┐ │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│ │  Add Column  │ │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│ └──────────────┘ │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
│ q: Quit  c: Copy  n: New  ?: Help                          │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 2: Enter Table Name

**Action:** Type `customers`

**What you see:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT *             │ ← SQL appears!
│ ┌──────────────┐ │                  │ FROM "customers"     │
│ │ customers    │ │ Column: ┌─────┐  │                      │
│ └──────────────┘ │         └─────┘  │                      │
│   Green border!  │ Operator: ┌───┐  │                      │
│                  │           │ = │  │                      │
│ Columns:         │           └───┘  │                      │
│ (none - SELECT *) │ Value: ┌───────┐ │                      │
│                  │        └───────┘ │                      │
│ ┌──────────────┐ │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│ │  Add Column  │ │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│ └──────────────┘ │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
│ q: Quit  c: Copy  n: New  ?: Help                          │
└─────────────────────────────────────────────────────────────┘
```

**Notice:**
- ✓ Green checkmark next to "Table Name"
- SQL preview shows `SELECT * FROM "customers"`
- Ready to add filters!

---

### Step 3: Add Email Filter - Enter Column

**Action:** Press Tab to move to "Column" field, type `email`

**What you see:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT *             │
│ ┌──────────────┐ │                  │ FROM "customers"     │
│ │ customers    │ │ Column: ┌─────┐  │                      │
│ └──────────────┘ │         │email│  │ ← Typed "email"      │
│                  │         └─────┘  │                      │
│ Columns:         │ Operator: ┌───┐  │                      │
│ (none - SELECT *) │           │ = │  │                      │
│                  │           └───┘  │                      │
│ ┌──────────────┐ │ Value: ┌───────┐ │                      │
│ │  Add Column  │ │        └───────┘ │                      │
│ └──────────────┘ │                  │                      │
│                  │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
│ q: Quit  c: Copy  n: New  ?: Help                          │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 4: Select Operator

**Action:** Press Tab, operator `=` is already selected (perfect!)

**What you see:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT *             │
│ ┌──────────────┐ │                  │ FROM "customers"     │
│ │ customers    │ │ Column: ┌─────┐  │                      │
│ └──────────────┘ │         │email│  │                      │
│                  │         └─────┘  │                      │
│ Columns:         │ Operator: ┌───┐  │                      │
│ (none - SELECT *) │           │ = │◄─── Selected           │
│                  │           └───┘  │                      │
│ ┌──────────────┐ │ Value: ┌───────┐ │                      │
│ │  Add Column  │ │        │ █     │ │ ← Cursor here        │
│ └──────────────┘ │        └───────┘ │                      │
│                  │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
│ q: Quit  c: Copy  n: New  ?: Help                          │
└─────────────────────────────────────────────────────────────┘
```

**If you need a different operator:**
- Click the dropdown
- See options: `=`, `!=`, `<`, `>`, `<=`, `>=`, `LIKE`, `IN`, etc.

---

### Step 5: Enter Value

**Action:** Type `john.doe@example.com`

**What you see:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT *             │
│ ┌──────────────┐ │                  │ FROM "customers"     │
│ │ customers    │ │ Column: ┌─────┐  │                      │
│ └──────────────┘ │         │email│  │                      │
│                  │         └─────┘  │                      │
│ Columns:         │ Operator: ┌───┐  │                      │
│ (none - SELECT *) │           │ = │  │                      │
│                  │           └───┘  │                      │
│ ┌──────────────┐ │ Value: ┌───────────────────────┐        │
│ │  Add Column  │ │        │john.doe@example.com   │        │
│ └──────────────┘ │        └───────────────────────┘        │
│                  │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │◄─ Click this!          │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
│ q: Quit  c: Copy  n: New  ?: Help                          │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 6: Add the Filter

**Action:** Click `[Add Filter]` button

**What you see:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT *             │
│ ┌──────────────┐ │                  │ FROM "customers"     │
│ │ customers    │ │ Column: ┌─────┐  │ WHERE "email" =      │
│ └──────────────┘ │         └─────┘  │  'john.doe@example   │
│                  │         (cleared) │   .com'              │
│ Columns:         │ Operator: ┌───┐  │     ▲                │
│ (none - SELECT *) │           │ = │  │     └─ SQL updated!  │
│                  │           └───┘  │                      │
│ ┌──────────────┐ │ Value: ┌───────┐ │                      │
│ │  Add Column  │ │        └───────┘ │                      │
│ └──────────────┘ │        (cleared) │                      │
│                  │                  │                      │
│                  │ Active Filters:  │                      │
│                  │ ┌──────────────────────────┐            │
│                  │ │ email = 'john.doe@       │            │
│                  │ │   example.com'  [Remove] │◄─ Filter!  │
│                  │ └──────────────────────────┘            │
│                  │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
│ q: Quit  c: Copy  n: New  ?: Help                          │
└─────────────────────────────────────────────────────────────┘
```

**Notice:**
- Filter fields cleared (ready for another filter)
- Filter appears in "Active Filters" list
- SQL updated with WHERE clause
- Can click [Remove] to delete this filter

---

### Step 7: Copy the SQL

**Action:** Press `c` key

**What you see:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT *             │
│ ┌──────────────┐ │                  │ FROM "customers"     │
│ │ customers    │ │ Column: ┌─────┐  │ WHERE "email" =      │
│ └──────────────┘ │         └─────┘  │  'john.doe@example   │
│                  │                  │   .com'              │
│ Columns:         │ Operator: ┌───┐  │                      │
│ (none - SELECT *) │           │ = │  │ ╔════════════════╗   │
│                  │           └───┉┉┉┼─║ SQL copied to  ║   │
│ ┌──────────────┐ │ Value: ┌───────┐ │ ║ clipboard!     ║   │
│ │  Add Column  │ │        └───────┘ │ ╚════════════════╝   │
│ └──────────────┘ │                  │     ▲                │
│                  │ Active Filters:  │     └─ Notification  │
│                  │ ┌──────────────────────────┐            │
│                  │ │ email = 'john.doe@       │            │
│                  │ │   example.com'  [Remove] │            │
│                  │ └──────────────────────────┘            │
│                  │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
│ q: Quit  c: Copy  n: New  ?: Help                          │
└─────────────────────────────────────────────────────────────┘
```

**Success!** SQL is now in your clipboard. Paste it anywhere!

---

## Walkthrough 2: Multiple Filters

**Goal:** Find high-value orders from November

---

### Starting Point

**Action:** Press `n` to start fresh, then enter:
- Table: `orders`
- Columns: `id`, `customer_id`, `total`

**What you see:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT "id",         │
│ ┌──────────────┐ │                  │   "customer_id",     │
│ │ orders       │ │ Column: ┌─────┐  │   "total"            │
│ └──────────────┘ │         └─────┘  │ FROM "orders"        │
│                  │                  │                      │
│ Columns:         │ Operator: ┌───┐  │                      │
│ ┌────────────────────────┐           │                      │
│ │ • id         [Remove]  │           │                      │
│ │ • customer_id [Remove] │           │                      │
│ │ • total      [Remove]  │           │                      │
│ └────────────────────────┘           │                      │
│                  │ Value: ┌───────┐ │                      │
│ ┌──────────────┐ │        └───────┘ │                      │
│ │  Add Column  │ │                  │                      │
│ └──────────────┘ │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
```

---

### Add First Filter: total >= 1000

**Action:** Add filter for minimum total

**After clicking [Add Filter]:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT "id",         │
│ ┌──────────────┐ │                  │   "customer_id",     │
│ │ orders       │ │ Column: ┌─────┐  │   "total"            │
│ └──────────────┘ │         └─────┘  │ FROM "orders"        │
│                  │                  │ WHERE "total" >= 1000│
│ Columns:         │ Operator: ┌───┐  │         ▲            │
│ • id             │           │ = │  │         └─ 1st filter│
│ • customer_id    │           └───┘  │                      │
│ • total          │ Value: ┌───────┐ │                      │
│                  │        └───────┘ │                      │
│                  │                  │                      │
│                  │ Active Filters:  │                      │
│                  │ ┌────────────────────┐                  │
│                  │ │ total >= 1000      │ ← Filter 1       │
│                  │ │          [Remove]  │                  │
│                  │ └────────────────────┘                  │
│                  │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
```

---

### Add Second Filter: created_at > 2024-11-01

**Action:** Add another filter for date

**After clicking [Add Filter]:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT "id",         │
│ ┌──────────────┐ │                  │   "customer_id",     │
│ │ orders       │ │ Column: ┌─────┐  │   "total"            │
│ └──────────────┘ │         └─────┘  │ FROM "orders"        │
│                  │                  │ WHERE "total" >= 1000│
│ Columns:         │ Operator: ┌───┐  │   AND "created_at" > │
│ • id             │           │ = │  │   '2024-11-01'       │
│ • customer_id    │           └───┘  │          ▲           │
│ • total          │ Value: ┌───────┐ │          └─ 2 filters│
│                  │        └───────┘ │                      │
│                  │                  │                      │
│                  │ Active Filters:  │                      │
│                  │ ┌────────────────────────┐              │
│                  │ │ total >= 1000          │ ← Filter 1   │
│                  │ │          [Remove]      │              │
│                  │ ├────────────────────────┤              │
│                  │ │ created_at > '2024-    │ ← Filter 2   │
│                  │ │   11-01'    [Remove]   │              │
│                  │ └────────────────────────┘              │
│                  │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
```

**Notice:**
- Both filters shown in list
- SQL automatically includes `AND`
- Each filter can be removed independently

---

## Walkthrough 3: Pattern Matching with LIKE

**Goal:** Find users with "Smith" anywhere in their name

---

### Setup and Add LIKE Filter

**What you see after adding the filter:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT "id", "name"  │
│ ┌──────────────┐ │                  │ FROM "users"         │
│ │ users        │ │ Column: ┌─────┐  │ WHERE "name" LIKE    │
│ └──────────────┘ │         └─────┘  │   '%Smith%'          │
│                  │                  │      ▲               │
│ Columns:         │ Operator: ┌─────┐│      └─ Pattern!     │
│ • id             │           │LIKE ││                      │
│ • name           │           └─────┘│                      │
│                  │              ▲    │                      │
│                  │              │    │ This will match:     │
│                  │         LIKE operator│ • "John Smith"    │
│                  │ Value: ┌───────┐ │ • "Smithson"         │
│                  │        │%Smith%│ │ • "Blacksmith"       │
│                  │        └───────┘ │                      │
│                  │            ▲      │                      │
│                  │            │      │                      │
│                  │      Wildcards!   │                      │
│                  │                  │                      │
│                  │ Active Filters:  │                      │
│                  │ ┌────────────────────────┐              │
│                  │ │ name LIKE '%Smith%'    │              │
│                  │ │          [Remove]      │              │
│                  │ └────────────────────────┘              │
│                  │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
```

---

## Walkthrough 4: IS NULL Check

**Goal:** Find users without email verification

---

### Add IS NULL Filter

**Important:** When you select IS NULL operator, the Value field is disabled!

**What you see:**

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                      v0.1.0    │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ Table & Columns  │ Filters (WHERE)  │ SQL Preview          │
│                  │                  │                      │
│ Table Name: ✓    │ Add Filter:      │ SELECT *             │
│ ┌──────────────┐ │                  │ FROM "users"         │
│ │ users        │ │ Column: ┌────────┐│ WHERE "verified_at" │
│ └──────────────┘ │         │verified││   IS NULL            │
│                  │         │  _at   ││                      │
│ Columns:         │         └────────┘│                      │
│ (SELECT *)       │ Operator: ┌──────┐│                      │
│                  │           │IS NUL││                      │
│                  │           │  L   ││                      │
│                  │           └──────┘│                      │
│                  │                ▲  │                      │
│                  │                │  │                      │
│                  │         IS NULL selected                 │
│                  │                  │                      │
│                  │ Value: ┌───────┐ │                      │
│                  │        │(disabled)│ ← No value needed!   │
│                  │        └───────┘ │                      │
│                  │                  │                      │
│                  │ Active Filters:  │                      │
│                  │ ┌────────────────────────┐              │
│                  │ │ verified_at IS NULL    │              │
│                  │ │          [Remove]      │              │
│                  │ └────────────────────────┘              │
│                  │ ┌──────────────┐ │ ┌─────┐ ┌────────┐  │
│                  │ │  Add Filter  │ │ │Copy │ │  Save  │  │
│                  │ └──────────────┘ │ └─────┘ └────────┘  │
└──────────────────┴──────────────────┴──────────────────────┘
```

**Key Point:** IS NULL and IS NOT NULL don't need values - just column and operator!

---

## Interface Elements Guide

### Visual Indicators

```
✓  Green checkmark    = Valid input
❌  Red X             = Invalid input
━  Green border      = Valid field
━  Red border        = Invalid field
█  Cursor            = Active field
⦿  Selected radio    = Active choice
○  Unselected radio  = Inactive choice
```

### Button States

```
┌──────────────┐
│  Add Filter  │  ← Enabled (dark)
└──────────────┘

┌──────────────┐
│  Add Filter  │  ← Disabled (grayed out)
└──────────────┘

┌──────────────┐
│█ Add Filter █│  ← Focused (highlighted)
└──────────────┘
```

### Progress Flow

```
Empty State → Table Added → Filters Added → SQL Ready
    ↓             ↓              ↓              ↓
No SQL yet    SELECT *     WHERE clause    Press 'c'
                                           to copy!
```

---

## Common Patterns

### Pattern 1: Quick Customer Lookup

```
Table: customers
Filter: email = [value]
⬇
Press 'c' to copy
⬇
Done in 10 seconds!
```

### Pattern 2: Build Complex Query

```
Step 1: Table + basic filter
⬇
Test SQL (press 'c', run in DB)
⬇
Step 2: Add another filter
⬇
Test SQL again
⬇
Step 3: Add more filters
⬇
Final SQL ready!
```

### Pattern 3: Refine Results

```
Start: SELECT *
⬇
See all data
⬇
Add specific columns
⬇
More focused query
⬇
Add filters to narrow results
```

---

## Tips from Visual Walkthrough

### Tip 1: Watch the SQL Preview
The right panel updates **immediately** - watch it change as you type!

### Tip 2: Green = Good
Look for green borders and checkmarks ✓

### Tip 3: Use Active Filters List
See all your conditions at a glance in the center panel

### Tip 4: Remove and Retry
Made a mistake? Click [Remove] next to any filter

### Tip 5: Press 'n' to Reset
Don't manually clear everything - just press `n` for new query

---

## Ready to Try?

Launch SQLTrans and follow along with these walkthroughs!

```bash
sqltrans
```

You now know exactly what to see and do at each step. Happy querying! 🚀

---

*SQLTrans v0.1.0 - See it, do it, build SQL queries!*
