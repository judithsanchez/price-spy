# Measurement Units 📏

Price Spy uses a standardized list of units to ensure accurate price-per-unit comparisons across different products and stores.

## Database Schema

Located in `app/storage/database.py`.

```sql
CREATE TABLE units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
```

---

## Seeded Units
The system is pre-loaded with common measurement units:

| | | | | |
|---|---|---|---|---|
| `ml` | `cl` | `dl` | `L` | `g` |
| `kg` | `lb` | `oz` | `fl oz` | `piece` |
| `pack` | `pair` | `set` | `tube` | `bottle` |
| `can` | `box` | `bag` | `tub` | `jar` |
| `unit` | | | | |

---

## API Interaction
You can fetch the full list of supported units for your frontend via:

- **`GET /api/units`**: Retrieves all available units in alphabetical order.
- **`POST /api/units`**: Create a new unit.
- **`PUT /api/units/{id}`**: Update a unit's name and **cascade changes** to all products and tracked items using it.
- **`PATCH /api/units/{id}`**: Partial update for units.
- **`DELETE /api/units/{id}`**: Safely delete a unit. Deletion is **blocked** if the unit is currently in use by any product or tracked item.
