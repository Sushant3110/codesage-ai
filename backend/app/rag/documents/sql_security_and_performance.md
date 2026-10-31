# SQL Security, Query Optimization, and Transaction Standards

Source URL: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
Document Title: SQL Security, Query Optimization, and Transaction Standards
Language: sql

## SQL Injection Prevention

### Parameterized Queries and Prepared Statements
The primary defense against SQL injection is the mandatory use of parameterized queries (prepared statements) or stored procedures with bound parameters.
When a database driver executes a parameterized query, the database treats user input strictly as literal data, never as executable SQL code.
Never format or concatenate user input directly into SQL strings, clauses, or stored procedures.

### Dynamic Identifiers and Whitelisting
If table names, column names, or sort orders (`ASC` / `DESC`) must be dynamic and cannot be parameterized with placeholders, validate them against a strict whitelist of known-safe identifiers.
Reject any identifier that contains unexpected characters or does not match the whitelist.

## Query Performance and Optimization

### Index Utilization
Ensure queries have supporting indexes on columns used in `WHERE`, `JOIN`, and `ORDER BY` clauses.
Avoid leading wildcards in `LIKE` queries (e.g. `LIKE '%term'`) because they prevent the database engine from using B-tree indexes, forcing full table scans.
Avoid calling functions on indexed columns in `WHERE` clauses (e.g. `WHERE YEAR(created_at) = 2026`) unless a matching functional index exists.

### Preventing N+1 Query Problems
Avoid running individual database queries inside application loops.
Use SQL `JOIN`s, subqueries, or bulk retrieval (`WHERE id IN (...)`) to fetch associated records in a single query.
Limit result sets using `LIMIT` / `OFFSET` or keyset pagination to avoid pulling millions of unneeded rows into application memory.

## Transaction Management and Data Integrity

### ACID Transactions
Wrap multi-step database mutations (such as money transfers or order creation with inventory deduction) inside explicit `BEGIN TRANSACTION` and `COMMIT` blocks.
Ensure error handlers issue a `ROLLBACK` to prevent partial updates from leaving the database in an inconsistent state.

### Normalization and Constraints
Enforce referential integrity using foreign key constraints (`FOREIGN KEY REFERENCES ... ON DELETE RESTRICT`).
Use database-level `NOT NULL` and `CHECK` constraints to ensure data invariants are enforced regardless of application bugs.
