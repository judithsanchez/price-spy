# Labels 🏷️

Labels provide a flexible, optional way to tag tracked items. Unlike Categories (which are mandatory and hierarchical), labels are flat and user-defined.

## Schema

Located in `app/storage/database.py`.

```sql
CREATE TABLE labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

-- Junction Table
CREATE TABLE tracked_item_labels (
    tracked_item_id INTEGER NOT NULL,
    label_id INTEGER NOT NULL,
    PRIMARY KEY (tracked_item_id, label_id),
    FOREIGN KEY(tracked_item_id) REFERENCES tracked_items(id) ON DELETE CASCADE,
    FOREIGN KEY(label_id) REFERENCES labels(id) ON DELETE CASCADE
);
```

---

## API Interaction

Modularized in `app/api/routers/labels.py`.

- **`GET /api/labels`**: List all labels.
- **`GET /api/labels/search?q=...`**: Search labels by name.
- **`POST /api/labels`**: Create a new label.
- **`PUT /api/labels/{id}`**: Rename a label.
- **`DELETE /api/labels/{id}`**: Delete a label. This **automatically** removes the label from all associated tracked items (cascade delete).

### Usage
- **Optional**: Labels are never required.
- **User-Driven**: Labels are not seeded; you create them as needed.
- **Many-to-Many**: A tracked item can have multiple labels, and a label can apply to multiple items.
