# Tasks: Frontend UI Iteration

## Task List

### `ui-1-cors`
**Goal**: Update FastAPI to support decoupled frontend requests.
- Add `CORSMiddleware` in `src/api/main.py` to allow origins like `http://localhost:5173`.

### `ui-2-vite-setup`
**Goal**: Initialize the decoupled frontend.
- Run `npx create-vite@latest frontend --template react` in the project root.
- Clean up boilerplate code and install `react-markdown`.

### `ui-3-design-system`
**Goal**: Implement the premium aesthetic design system in CSS.
- Define global CSS tokens (`index.css`) for dark mode, glassmorphism, gradients, and micro-animations.

### `ui-4-components`
**Goal**: Build the React UI components.
- Build `QueryPanel` (Ask questions, display markdown results).
- Build `IngestPanel` (Upload PDFs).
- Build the main `App` layout with tab navigation.

### `ui-5-api-integration`
**Goal**: Wire components to the backend.
- Implement `fetch` calls to the FastAPI endpoints.
- Add loading spinners and error handling states.
