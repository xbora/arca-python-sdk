# Query Filter Fix - Comparison Operators Now Work Correctly

## Summary

Fixed a critical bug where SDK clients couldn't use comparison operators (`>`, `<`, `>=`, `<=`, `!=`, `LIKE`, etc.) in queries because the SDK wasn't properly formatting the request payload to match the server API expectations.

## The Problem

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

## The Solution

### Code Changes

**1. Fixed `query()` method:**
```python
# NEW CODE (FIXED)
if query or filters:
    filter_dict = filters.copy() if filters else {}
    if query:
        filter_dict["customWhere"] = query  # ✓ Correct mapping
    payload["filters"] = filter_dict
```

**2. Fixed `update()` method:**
Same fix applied to the `where` parameter in the `update()` method.

### Files Modified
- `arca/client.py` - Fixed query and update methods
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

### ✓ Update with Conditions
```python
# Update rows matching condition
result = client.update(
    table_name="meals",
    updates={"meal_type": "dinner"},
    where="calories > 1000"
)
```

## Testing

A comprehensive test suite was created and all tests pass:
- ✓ Query parameter correctly maps to filters.customWhere
- ✓ Query and filters merge properly
- ✓ Filters work without query parameter
- ✓ Update where parameter maps correctly

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
