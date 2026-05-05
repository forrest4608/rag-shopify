# Technical Plan: Frontend UI Iteration

## Architecture Impact
- **Backend (`src/api/main.py`)**: Must add `CORSMiddleware` to allow requests from `http://localhost:5173`.
- **Frontend (`/frontend`)**: An entirely new directory containing a React+Vite project.

## Files Affected
- `src/api/main.py`
- `frontend/*` (New Vite Project)

## Test Strategy
- **CORS Verification**: Ensure browser does not block OPTIONS preflight requests.
- **Integration Test**: Run backend and frontend concurrently, submit queries and uploads via the UI.

## Rollback Plan
- Delete the `frontend/` directory.
- Remove `CORSMiddleware` from `src/api/main.py`.

## Risks
- **CORS Configuration**: Misconfigured CORS may block development.
- **State Management**: Managing loading/error states cleanly in React without over-complicating dependencies. We will use standard React hooks (`useState`, `useEffect`).
