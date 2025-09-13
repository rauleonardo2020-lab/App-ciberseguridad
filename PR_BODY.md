Escudo IA: Fullstack integration (FastAPI + JWT + React/Tailwind)

Summary
- Backend:
  - Auth: /auth/signup (JSON), /auth/login (x-www-form-urlencoded OAuth2). JWT issued and used for protected routes.
  - Network scan: POST /scan/network expects JSON {"ip": "<IPv4/IPv6>"}; uses python-nmap and persists results per user (scan_results).
  - Results: GET /scan/results lists the authenticated user’s scans.
  - CORS: Allows http://localhost:5173 and http://127.0.0.1:5173.
  - Robust handling when nmap is missing: returns 503 with a clear message instead of crashing.
  - Fix: Correct traversal of python-nmap results (use all_protocols() and dict access) to avoid server error.
- Frontend (Vite + React + Tailwind):
  - Routes: /login, /signup, /dashboard (protected).
  - AuthContext: persists token in localStorage and attaches Authorization: Bearer token via axios.
  - Dashboard: input for IP, “Escanear” button calls /scan/network, table renders /scan/results. Trims and validates IP to avoid 422.
  - Build: cleaned up unused React imports; type-check/build passes.

Local test flow (verified)
1) Signup: POST /auth/signup
2) Login: POST /auth/login (form-encoded) → store token
3) Scan: POST /scan/network with {"ip":"127.0.0.1"} → 200 OK; results saved
4) List: GET /scan/results → includes latest result
Note: If nmap is unavailable on the server, /scan/network responds 503 with a clear message; the frontend surfaces it gracefully.

How to run locally
Backend:
- poetry install
- poetry run fastapi dev app/main.py
Frontend:
- cd frontend
- npm ci
- echo 'VITE_API_URL=http://localhost:8000' > .env
- npm run dev (or npm run build)

Deployment
- After approval, deploy backend (FastAPI/Poetry) and then set frontend VITE_API_URL to the public backend URL, rebuild, and deploy frontend.

Requester and Links
- Requested by: Raul Leonardo (@rauleonardo2020-lab)
- Link to Devin run: https://app.devin.ai/sessions/58b96b32bb224c248ecf1c6f0178de33

Screenshots (optional local)
- You can test UI locally at http://localhost:5173
