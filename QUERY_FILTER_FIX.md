# Query and Update API Fixes - Now Matching Server API

## Summary

Fixed critical bugs in both `query()` and `update()` methods where the SDK wasn't properly formatting request payloads to match the server API expectations.

## Problem 1: Query Filter Comparisons

### What Users Experienced
When SDK users tried to filter data using comparison operators:

```python
# This didn't work before the fix
results = client.query(
    table_name="meals",
    query="calories > 500"
)
```

The server wouldn't apply the filter correctly because the SDK was sending:
```json
{
  "tableName": "meals",
  "query": "calories > 500"
}
```

But the server expected:
```json
{
  "tableName": "meals",
  "filters": {
    "customWhere": "calories > 500"
  }
}
```

### Root Cause
In `arca/client.py`, the `query()` method was mapping the `query` parameter to a top-level `"query"` field instead of `filters.customWhere`:

```python
# OLD CODE (BROKEN)
if query:
    payload["query"] = query  # ❌ Wrong field
if filters:
    payload["filters"] = filters
```

### The Solution

#### Code Changes

**Fixed `query()` method:**
```python
# NEW CODE (FIXED)
if query or filters:
    filter_dict = filters.copy() if filters else {}
    if query:
        filter_dict["customWhere"] = query  # ✓ Correct mapping
    payload["filters"] = filter_dict
```

## Problem 2: Update Method Parameter Mismatch

### What Was Wrong

The SDK's `update()` method was using incorrect field names:

**Server API expects:**
```json
{
  "tableName": "meals",
  "where": {"id": 5},
  "data": {"calories": 910, "meal_type": "dinner"}
}
```

**SDK was sending:**
```json
{
  "tableName": "meals",
  "updates": {...},              // ❌ Wrong - should be "data"
  "filters": {"customWhere": ...} // ❌ Wrong - should be "where" as dict
}
```

### The Solution

#### Code Changes

**Fixed `update()` method:**
```python
# OLD SIGNATURE (BROKEN)
def update(table_name, updates, where=None, filters=None):
    payload = {
        "tableName": table_name,
        "updates": updates  # ❌ Wrong field
    }
    if where:
        payload["filters"] = {"customWhere": where}  # ❌ Wrong structure

# NEW SIGNATURE (FIXED)
def update(table_name, data, where=None):
    payload = {
        "tableName": table_name,
        "data": data  # ✓ Correct field name
    }
    if where:
        payload["where"] = where  # ✓ Correct - dict for exact matches
```

**Breaking Change**: The `where` parameter changed from a string (SQL WHERE clause) to a dict (exact match conditions).

### Files Modified
- `arca/client.py` - Fixed query method (filters.customWhere) and update method (data/where params)
- `README.md` - Updated documentation with comparison operator examples
- `replit.md` - Documented the fix in project history

## What Now Works

### ✓ Comparison Operators
```python
# Greater than
results = client.query(table_name="meals", query="calories > 500")

# Less than or equal
results = client.query(table_name="meals", query="protein <= 20")

# Not equal
results = client.query(table_name="meals", query="meal_type != 'snack'")

# LIKE pattern matching
results = client.query(table_name="meals", query="food LIKE '%chicken%'")
```

### ✓ Complex Conditions
```python
# Multiple conditions with AND/OR
results = client.query(
    table_name="meals",
    query="calories > 500 AND protein > 30"
)

results = client.query(
    table_name="meals",
    query="meal_type = 'breakfast' OR meal_type = 'brunch'"
)
```

### ✓ Combining with Other Filters
```python
# Custom WHERE clause + time filter
results = client.query(
    table_name="meals",
    query="protein > 20",
    filters={"daysAgo": 30},
    limit=5
)
```

### ✓ Update with Exact Match Conditions
```python
# Update specific row by ID
result = client.update(
    table_name="meals",
    data={"calories": 910, "meal_type": "dinner"},
    where={"id": 5}
)

# Update by exact column match
result = client.update(
    table_name="meals",
    data={"calories": 170},
    where={"food": "Grilled Chicken Breast"}
)
```

## Testing

Comprehensive test suites were created and all tests pass:

**Query Method Tests:**
- ✓ Query parameter correctly maps to filters.customWhere
- ✓ Query and filters merge properly
- ✓ Filters work without query parameter

**Update Method Tests:**
- ✓ Update uses "data" field (not "updates")
- ✓ Update uses "where" as dict (not "filters")
- ✓ Payload matches server API exactly

## Server API Verification

The fix was verified against the actual server response. Example working request:

**Request:**
```json
POST https://arca.build/api/v1/tables/query
{
  "tableName": "meals",
  "filters": {
    "customWhere": "calories > 500"
  },
  "orderBy": "created_at DESC",
  "limit": 10
}
```

**Response:** ✓ Success - Returns 10 meals with calories > 500

## Impact

This fix enables SDK users to:
1. Use all SQL comparison operators in queries
2. Filter data with complex conditions
3. Combine custom WHERE clauses with other filter types
4. Update specific rows based on conditions

The SDK now properly aligns with the server API contract and matches the functionality shown in the server documentation.
