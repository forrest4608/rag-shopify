# Specification: Frontend UI Iteration

## Overview
We will build a Single Page Application (SPA) using React and Vite as the modern decoupled frontend framework. The frontend will run on its own port (e.g., 5173) and communicate with the FastAPI backend via standard REST calls.

## Requirements

### 1. Aesthetic Design (Mandatory)
- **Theme**: Clean, fresh, and minimalist light mode (inspired by Apple/Google design languages). Use ample whitespace and clear hierarchy.
- **Typography**: Modern, highly legible sans-serif font (e.g., 'Inter', 'SF Pro Display', or 'Roboto').
- **Colors**: Crisp white backgrounds, subtle light-gray cards (`#f8f9fa`), and primary brand colors (like a clear Google Blue or Apple subtle accent). Avoid heavy gradients; prefer solid, soft colors.
- **Styling**: Vanilla CSS utilizing CSS Modules for component isolation. Soft, diffused drop-shadows to provide depth without clutter.
- **Animations**: Silky smooth, understated micro-animations (e.g., subtle scaling on buttons, gentle fade-ins).

### 2. Components
- **Layout**: Header, Sidebar/Tabs, and Main Content area.
- **Chat/Query View**: Form for Company Name and Question. Real-time rendering of markdown responses using `react-markdown`.
- **Ingest View**: Form to upload a PDF with a Company Name.

### 3. Integration
- Frontend calls `http://127.0.0.1:8000/query` and `/ingest`.
- Backend must be updated to enable CORS (Cross-Origin Resource Sharing) to allow requests from the Vite dev server.
