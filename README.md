# TicketHub

Middleware REST servis koji dohvaća "support tickete" iz vanjskog izvora (DummyJSON),
sprema ih u lokalnu bazu i izlaže ih kroz vlastiti API. Zadatak za akademiju.

## Tech stack

- Python 3.11, FastAPI, httpx, pydantic 2
- SQLAlchemy 2 (async) + SQLite (aiosqlite)
- Alembic migracije
- pytest + pytest-asyncio, ruff
- Docker + docker compose, GitHub Actions CI

## Pokretanje lokalno

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt -e .

alembic upgrade head             # kreira shemu baze
uvicorn tickethub.main:app --reload
```

Na startup se automatski povuku ticketi s DummyJSON-a u lokalnu bazu (samo oni koji
još ne postoje, pa lokalne izmjene prežive restart). Nakon toga svi endpointi rade
isključivo nad lokalnom bazom. Background task ponavlja sync svakih
`SYNC_INTERVAL_SECONDS` sekundi.

Swagger UI: http://localhost:8000/docs

Umjesto ručnih naredbi može se koristiti i Makefile: `make install`, `make migrate`,
`make run`, `make lint`, `make test`, `make docs`, `make docker-build`, `make docker-up`.

## Konfiguracija (env varijable)

| Varijabla | Default | Opis |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./tickethub.db` | Async SQLAlchemy URL baze |
| `DUMMYJSON_URL` | `https://dummyjson.com` | Bazni URL vanjskog izvora |
| `SECRET_KEY` | dev vrijednost | Tajna za potpisivanje JWT-a (obavezno promijeniti u produkciji) |
| `JWT_ALGORITHM` | `HS256` | Algoritam za JWT |
| `TOKEN_EXPIRE_MINUTES` | `60` | Trajanje tokena |
| `SYNC_INTERVAL_SECONDS` | `300` | Interval pozadinskog synca (0 = isključen) |
| `STATS_CACHE_TTL` | `30` | TTL in-memory cachea za /stats (sekunde) |

## Endpointi

| Metoda | Path | Opis |
|---|---|---|
| GET | `/tickets` | Paginirana lista (id, title, status, priority, opis skraćen na 100 znakova). Filtri: `?status=open\|closed`, `?priority=low\|medium\|high`, paginacija: `?limit=&offset=` |
| GET | `/tickets/search?q=...` | Pretraga po nazivu |
| GET | `/tickets/{id}` | Detalji ticketa + puni JSON iz izvora (`raw_source`) |
| POST | `/tickets` | Kreiranje ticketa (traži JWT) |
| PATCH | `/tickets/{id}` | Izmjena ticketa - status, priority, assignee... (traži JWT) |
| POST | `/auth/login` | Login preko DummyJSON korisnika, vraća JWT |
| GET | `/stats` | Agregirane statistike (cachirano) |
| GET | `/health` | Health check za k8s/Compose |

### Autentifikacija

Write endpointi su zaštićeni JWT-om. Token se dobije loginom s bilo kojim
DummyJSON korisnikom (https://dummyjson.com/users), npr.:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "emilys", "password": "emilyspass"}'

curl -X POST http://localhost:8000/tickets \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Novi ticket", "priority": "high", "assignee": "emilys"}'
```

## Transformacija podataka

DummyJSON todo se mapira u Ticket ovako:

- `title` = polje `todo`
- `status` = `closed` ako je `completed == true`, inače `open`
- `priority` = `id % 3` -> low / medium / high
- `assignee` = username korisnika dohvaćen preko `userId`
- originalni JSON se čuva u koloni `raw_source`

## Testovi i lint

```bash
make test    # pytest (26 testova, in-memory SQLite, bez pravih HTTP poziva)
make lint    # ruff
```

CI (GitHub Actions) na svaki push/PR vrti lint, migracije i testove:
[.github/workflows/ci.yml](.github/workflows/ci.yml)

## Docker

```bash
docker compose up --build
```

Baza se sprema u named volume pa podaci prežive restart kontejnera.

## Statička OpenAPI dokumentacija

`make docs` generira [docs/redoc-static.html](docs/redoc-static.html) i
[docs/openapi.json](docs/openapi.json).

## Struktura projekta

```
src/tickethub/       aplikacija (config, baza, modeli, sheme, sync, auth, routeri)
tests/               pytest testovi
alembic/             migracije
scripts/             pomoćne skripte (export OpenAPI docs)
docs/                generirana statička dokumentacija
.github/workflows/   CI
```

## Napomena o korištenju AI alata

Većinu zadatka radio sam sam, ali za postavljanje Alembica s asinkronim SQLAlchemy
engine-om koristio sam Claude jer mi standardni (sync) `env.py` predložak nije radio.
Prompt koji sam koristio:

> Koristim FastAPI i SQLAlchemy 2.0 s async engine-om (sqlite+aiosqlite). Kako trebam
> napisati alembic env.py da migracije rade s async engine-om? Standardni env.py mi ne
> radi jer create_engine očekuje sync driver. Trebam offline i online mode.

Claude sam iskoristio i za async pytest setup (fixture koja svakom testu daje svježu
in-memory SQLite bazu preko dependency override-a za `get_session`, uz `StaticPool`
da sve konekcije dijele istu in-memory bazu).
