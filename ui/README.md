# Market Agent UI (MVP)

- React + Vite + Tailwind + Router + Recharts
- Requiere variable de entorno `VITE_API_BASE` apuntando a tu API FastAPI

## Scripts
- `npm run dev` — local dev (http://localhost:5173)
- `npm run build` — build para producción
- `npm run preview` — sirve el build localmente

## Entorno
En Vercel, seteá en **Project Settings → Environment Variables**:
- `VITE_API_BASE = https://<tu-servicio-en-render>.onrender.com`

Para desarrollo local, copiá `.env.example` a `.env` y ajustá `VITE_API_BASE` si tu API no corre en `http://localhost:8000`.

## API esperada
- `GET /healthz` → `{ status: "ok" }`
- `GET /rules` → `Rule[]`
- `POST /instruments` → `{ ok: true }` con body `{ symbol, instrument_id, type, currency, source }`

## Notas
- El sparkline usa datos mock hasta que exista `GET /prices`.
- Para CORS en la API, habilitá tu dominio de Vercel.
