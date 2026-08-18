# Materials Management - Odoo 14 Module

REST API module for managing materials (fabric, jeans, cotton) with supplier associations.

## Requirements

- Odoo 14

## Installation

```sh
git clone https://github.com/dalhaqq/odoo-materials-addon.git /path/to/odoo/addons/materials
```

Restart Odoo, update module list, install "Materials".

## Model: `materials.material`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `code` | Char | Yes | Unique identifier |
| `name` | Char | Yes | Material name |
| `type` | Selection | Yes | `fabric`, `jeans`, `cotton` |
| `buy_price` | Float | Yes | Minimum 100 |
| `supplier_id` | Many2one | Yes | Links to `res.partner` |
| `active` | Boolean | - | Default `True` (soft delete) |

## API Reference

All endpoints use **JSON-RPC** (`type='json'`). Authenticate via session.

### `POST /materials` - List all materials

**Params:**
```json
{
  "page": 1,
  "limit": 20,
  "search": "keyword",
  "sort": "code",
  "order": "asc"
}
```

**Response:**
```json
{
  "materials": [{"id": 1, "code": "M001", "name": "Fabric A", "type": "fabric", "buy_price": 200, "supplier_id": [1, "Supplier 1"]}],
  "total": 10,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

### `POST /materials/filter` - Filter by type

**Params:**
```json
{ "type": "fabric" }
```

Multiple types (comma-separated):
```json
{ "type": "fabric,jeans" }
```

### `POST /materials/<id>` - Get single material

**Response:**
```json
{
  "material": {"id": 1, "code": "M001", "name": "Fabric A", "type": "fabric", "buy_price": 200, "supplier_id": [1, "Supplier 1"]}
}
```

### `POST /materials/create` - Create material

**Params:**
```json
{
  "code": "M001",
  "name": "Fabric A",
  "type": "fabric",
  "buy_price": 200,
  "supplier_id": 1
}
```

### `POST /materials/<id>/update` - Update material

**Params (partial update):**
```json
{ "buy_price": 300 }
```

### `POST /materials/<id>/delete` - Delete material

**Response:**
```json
{ "message": "Material deleted successfully" }
```

### `POST /materials/available_types` - List type options

### `POST /materials/suppliers` - List all suppliers

## Error Responses

All endpoints return errors in this format:
```json
{ "error": "Error message here" }
```

Common errors:
| Error | Cause |
|-------|-------|
| `Missing required fields: [...]` | Required field not provided |
| `Material Buy Price cannot be less than 100` | Price below minimum |
| `Material Code must be unique` | Duplicate code |
| `Material not found` | Invalid ID |
| `Invalid material type(s): [...]` | Unknown type value |

## Tests

```sh
# Run model tests
odoo-bin -d test_db --test-tags /material -i materials --stop-after-init

# Run controller tests (post-install)
odoo-bin -d test_db --test-tags /material -i materials --stop-after-init
```

## License

MIT License
