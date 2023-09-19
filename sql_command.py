# whether the table exists
# Parameters: (tableName: str)
TABLE_EXISTS = """
SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?
"""