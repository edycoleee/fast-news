## Database and Transaction Architecture Standards

### Database
- Use PostgreSQL as the primary relational database.
- Use SQLAlchemy 2.x with a consistent asynchronous session strategy.
- Use Alembic for database schema migrations.
- Keep database models organized by feature.
- Use explicit foreign keys, unique constraints, check constraints, and appropriate indexes.
- Never rely solely on application-level validation for data integrity.

### Transaction Management
- Define transaction boundaries at the service/use-case level.
- Use one database transaction for all database changes belonging to one atomic business operation.
- Repositories must never call `commit()` independently.
- Repositories may call `flush()` when generated identifiers or database synchronization are needed.
- Let exceptions propagate so the transaction can roll back.
- Avoid implicit or nested transaction management.
- Do not commit automatically in the database session dependency.
- Ensure a failed operation does not leave partial database changes.

### Concurrency Control
- Use PostgreSQL READ COMMITTED as the default isolation level.
- Prefer optimistic locking for frequently edited records where simultaneous modifications are possible.
- Use SELECT FOR UPDATE for critical operations requiring pessimistic row locking.
- Use conditional UPDATE statements and database constraints for race-sensitive operations.
- Do not apply row locks indiscriminately.
- Use unique constraints to prevent duplicate records.
- Use idempotency keys for operations that must not be processed more than once.
- Handle deadlocks and serialization failures safely when retrying transactions.

### Data Integrity and Audit
- Use foreign keys and appropriate ON DELETE policies.
- Use indexes for frequently queried and filtered columns.
- Preserve important business transaction history.
- Do not silently delete financial or clinical transaction history.
- Record important user actions in audit logs.
- Keep audit records consistent with the business operation when required.

### File Storage
- Do not store uploaded binary files directly in PostgreSQL unless there is a specific reason.
- Store file metadata and storage keys in PostgreSQL.
- Validate file content, MIME type, size, and file access permissions.
- Coordinate database transactions with filesystem or object storage operations.
- Implement cleanup for failed or abandoned uploads.

### Database Testing
- Use a dedicated PostgreSQL testing database.
- Test commit, rollback, constraints, and foreign key behavior.
- Test concurrent requests for race-sensitive operations.
- Test optimistic locking conflicts.
- Test row locking using separate database connections.
- Never run automated tests against production databases.
- Never reset or drop production databases through automated development commands.