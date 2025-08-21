# Market Agent UI (MVP)

- React + Vite + Tailwind + Router + Recharts
- Requiere variable de entorno `VITE_API_URL` apuntando a tu API FastAPI

## Scripts
- `npm run dev` — local dev (http://localhost:5173)
- `npm run build` — build para producción
- `npm run preview` — sirve el build localmente

## Entorno
En Vercel, seteá en **Project Settings → Environment Variables**:
- `VITE_API_URL = https://<tu-servicio-en-render>.onrender.com`

## API esperada
- `GET /healthz` → `{ status: "ok" }`
- `GET /rules` → `Rule[]`
- `POST /instruments` → `{ ok: true }` con body `{ symbol, instrument_id, type, currency, source }`

## Notas
- El sparkline usa datos mock hasta que exista `GET /prices`.
- Para CORS en la API, habilitá tu dominio de Vercel.
