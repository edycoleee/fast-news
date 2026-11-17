---
applyTo: "frontend/src/**/*.{js,jsx}"
---

# Frontend Development Rules

- Gunakan React functional components.
- Gunakan JavaScript ES Modules.
- Gunakan React Router untuk routing.
- Gunakan TanStack Query untuk server state.
- Gunakan Context hanya untuk global client state yang benar-benar diperlukan.
- Gunakan Axios melalui satu centralized API client.
- Gunakan React Hook Form untuk form management.
- Gunakan Zod untuk frontend validation.
- Pisahkan API services dari UI components.
- Pisahkan reusable components dari feature components.
- Gunakan Tailwind CSS.
- Hindari komponen yang terlalu besar.
- Hindari duplikasi business rules.
- Jangan menyimpan access secret di frontend.
- Jangan mengandalkan frontend sebagai mekanisme authorization.
- Tangani loading, error dan empty states.
- Tambahkan unit testing untuk komponen penting.


## Frontend Architecture Standards

Use Feature-Based Architecture combined with reusable UI components inspired by Atomic Design.

### 1. Feature-Based Structure
- Organize application code by business feature under `src/features/`.
- Each feature owns its API functions, components, hooks, pages, and tests as appropriate.
- Keep feature-specific business logic inside its owning feature.
- Avoid large centralized component, API, or hooks directories.
- Do not create micro-frontends.

### 2. Component Responsibilities
- Feature components belong inside their respective feature.
- Generic reusable UI components belong in `src/shared/components/ui/`.
- Application layouts belong in `src/shared/components/layout/`.
- Shared components must not contain feature-specific business rules.
- Apply Atomic Design principles when useful, without requiring unnecessary atoms/molecules/organisms folders.

### 3. API and Server State
- Use a centralized Axios client.
- Keep API functions inside their respective feature API directories.
- Use TanStack Query for server state, caching, mutations, and invalidation.
- Avoid duplicating server state in React Context.
- Handle loading, error, empty, and success states consistently.

### 4. Client State and Forms
- Use React Context only for genuinely global client state.
- Use local component state for local UI interactions.
- Use React Hook Form for complex forms.
- Use Zod for frontend schema validation.
- Do not treat frontend validation as a replacement for backend validation.

### 5. Routing and Permissions
- Centralize route configuration in `app/router.jsx`.
- Keep page components inside their respective features.
- Frontend route guards improve UX but do not replace backend authorization.
- Backend remains the authority for authentication and permissions.

### 6. Testing and Maintainability
- Use Vitest and React Testing Library.
- Use Playwright for E2E testing.
- Add stable data-testid attributes to important interactive elements.
- Keep feature-specific tests near their feature.
- Avoid oversized components; split them by responsibility.
- Do not introduce abstractions without a clear reuse or maintainability benefit.


