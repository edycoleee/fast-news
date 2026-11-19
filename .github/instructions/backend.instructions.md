---
applyTo: "backend/**/*.py"
---

# Backend Development Rules

- Gunakan FastAPI.
- Gunakan SQLAlchemy 2.x.
- Gunakan Pydantic untuk request dan response schemas.
- Gunakan async SQLAlchemy secara konsisten.
- Pisahkan router, service, repository, models dan schemas.
- Router hanya menangani HTTP request dan response.
- Business logic harus berada di service layer.
- Database access harus melalui repository atau pola data access yang disepakati.
- Gunakan dependency injection.
- Gunakan transaction boundary yang jelas.
- Gunakan rollback ketika transaksi gagal.
- Jangan menyimpan password plaintext.
- Periksa permission di backend.
- Jangan mengembalikan informasi internal atau secret dalam response.
- Tambahkan pytest untuk fitur baru.
- Setiap modul fitur wajib mempunyai `permissions.py` dan permission-nya didaftarkan di RBAC permission registry.
- Endpoint menggunakan `require_permission(...)` atau `require_any_permission(...)` dengan konstanta dari manifest modul.
- Role template/assignment tidak boleh di-hardcode di kode fitur; role dan relasi role tetap data database.
- Permission registry wajib disinkronkan melalui command yang idempotent, bukan dibuat dari input endpoint.
- Permission yang dikelola registry tidak boleh diubah/dihapus melalui RBAC API biasa.
- Gunakan type hints.
- Tangani exception secara konsisten.
- Jangan menggunakan synchronous database operations di async request handlers.
- Gunakan Alembic untuk seluruh perubahan skema database.
- Hindari duplikasi kode di backend.
- Pastikan semua input divalidasi dengan Pydantic schemas.
- Gunakan logging untuk mencatat kejadian penting dan error.
- hybrid design pattern untuk service dan repository layer, fitur mempunyai atomic unit sendiri.

## Backend Architecture Standards

Use a Feature-Based Modular Monolith architecture with Service–Repository Pattern.

### 1. Feature-Based Modules
- Organize backend code by business feature, not only by technical layer.
- Each feature must be an independent module under `app/modules/`.
- Each module owns its routers, schemas, models, services, repositories, dependencies, and tests as appropriate.
- Features must have clear responsibilities and boundaries.
- Do not create microservices unless explicitly requested.

### 2. Layer Responsibilities
- Router: HTTP request handling, dependency injection, input/output schemas, and HTTP status codes only.
- Service: business rules, use-case orchestration, authorization-related business checks, and transaction coordination.
- Repository: database queries and persistence operations only.
- Model: SQLAlchemy database entities and relationships.
- Schema: Pydantic request and response contracts.
- Dependencies: module-specific dependency providers.

### 3. Atomic Feature Design
- Keep each feature cohesive and independently understandable.
- Avoid oversized files and unrelated responsibilities.
- Start with simple `service.py` and `repository.py` files for small modules.
- Split services by use case when complexity grows.
- Split schemas, repositories, and tests when their responsibilities become too large.
- Do not create unnecessary abstractions or excessive one-line files.
- Do not introduce circular dependencies between modules.

### 4. Cross-Module Communication
- Avoid directly accessing another module's internal repository or database implementation.
- Expose clear service interfaces or application-level contracts for cross-module operations.
- Keep shared utilities in `app/shared/` only when genuinely reused.
- Avoid circular imports and hidden dependencies.

### 5. Database and Transactions
- Use SQLAlchemy 2.x with a consistent async database strategy.
- Inject database sessions through FastAPI dependencies.
- Define explicit transaction boundaries.
- Do not commit independently inside individual repositories.
- Support atomic operations across multiple repositories when required.
- Use database constraints to protect data integrity and race-sensitive operations.
- Use Alembic for all schema migrations.

### 6. Testing
- Keep tests close to their owning feature in `modules/<feature>/tests/`.
- Maintain shared testing configuration and fixtures in the central test infrastructure.
- Test service business logic independently.
- Test repositories and database behavior using integration tests.
- Test API endpoints and permissions.
- Never run automated tests against production databases.

### 7. Implementation Workflow
Before implementing a new feature:
1. Identify its module boundary.
2. Define its API contract and use cases.
3. Identify database entities and relationships.
4. Identify dependencies on other modules.
5. Propose the file structure.
6. Explain transaction boundaries.
7. Define unit, integration, and API tests.

Implement only the requested feature. Avoid unrelated refactoring.

Aturan	Rekomendasi
Router	Tidak boleh berisi business logic
Service	Tidak menulis query SQL langsung
Repository	Tidak mengatur HTTP response
Database session	Dikelola melalui dependency dan unit of work
Transaction	Dikendalikan satu batas transaksi yang jelas
Antarfitur	Mengakses melalui service/interface yang disepakati
Shared	Hanya untuk fungsi yang benar-benar lintas fitur
Testing	Setiap fitur memiliki unit dan integration test