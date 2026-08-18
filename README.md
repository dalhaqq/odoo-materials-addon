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

REST API using proper HTTP methods. Authenticate via session.

### GET /api/materials - List all materials

**Query Params:**
```
?page=1&limit=20&search=keyword&sort=code&order=asc
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

### GET /api/materials/filter - Filter by type

```
GET /api/materials/filter?type=fabric
GET /api/materials/filter?type=fabric,jeans
```

### GET /api/materials/<id> - Get single material

```json
{
  "material": {"id": 1, "code": "M001", "name": "Fabric A", "type": "fabric", "buy_price": 200, "supplier_id": [1, "Supplier 1"]}
}
```

### POST /api/materials - Create material

**Body:**
```json
{
  "code": "M001",
  "name": "Fabric A",
  "type": "fabric",
  "buy_price": 200,
  "supplier_id": 1
}
```

### PATCH /api/materials/<id> - Update material

**Body (partial update):**
```json
{"buy_price": 300}
```

### DELETE /api/materials/<id> - Delete material

**Response:**
```json
{"message": "Material deleted successfully"}
```

### GET /api/materials/available_types - List type options

### GET /api/materials/suppliers - List suppliers

Returns partners with `is_supplier=True`.

## Error Responses

All endpoints return errors in this format:
```json
{"error": "Error message here"}
```

Common errors:
| Status | Error | Cause |
|--------|-------|-------|
| 400 | `Missing required fields: [...]` | Required field not provided |
| 400 | `Material Buy Price cannot be less than 100` | Price below minimum |
| 400 | `Material Code must be unique` | Duplicate code |
| 404 | `Material not found` | Invalid ID |
| 400 | `Invalid material type(s): [...]` | Unknown type value |

## Tests

```sh
odoo-bin -d test_db --test-tags /material -i materials --stop-after-init
```

## License

LGPL-3
