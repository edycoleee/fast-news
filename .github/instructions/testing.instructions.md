
## Testing Standards

### Frontend Testing
- Use Playwright for End-to-End (E2E) testing.
- Use Vitest and React Testing Library for component and frontend unit tests.
- Add stable `data-testid` attributes to important interactive elements and elements requiring deterministic E2E selection.
- Use semantic selectors such as `getByRole`, `getByLabel`, and `getByText` when appropriate.
- Use `getByTestId` when semantic selectors are insufficient.
- Use consistent kebab-case naming for test IDs.
- Do not use CSS classes or styling selectors as the primary E2E selectors.
- Every major feature should include relevant tests for success, validation errors, loading, empty states, and failure states.

### Backend Testing
- Use pytest for backend testing.
- Use FastAPI TestClient or HTTPX according to the application's async architecture.
- Maintain reusable fixtures in `tests/conftest.py`.
- Use a dedicated PostgreSQL testing database.
- Never run automated tests against production data.
- Test API response status, response schema, validation, authentication, and authorization.
- Test business logic independently from HTTP endpoints.
- Test transaction commit, rollback, and concurrency-sensitive operations where relevant.
- Ensure sensitive fields such as password hashes are never exposed in API responses.

### E2E Testing
- Use Playwright to test complete user workflows.
- Test login, logout, role-based access, user CRUD, news CRUD, file upload, comment moderation, and public news visibility.
- Verify both positive and negative authorization scenarios.
- Keep test data isolated and reproducible.
- Do not rely on execution order between independent tests.

### Development Rules
- Every new feature must include an appropriate testing strategy.
- Run relevant tests before declaring a feature complete.
- Do not claim tests passed unless they were actually executed.
- Fix regressions before moving to the next milestone.


