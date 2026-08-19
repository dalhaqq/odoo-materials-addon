# Materials API Reference

REST API using proper HTTP methods. Authenticate via Odoo session cookie.

Base URL: `http://<odoo-host>`

---

## GET /api/materials

List all active materials with optional type filter, pagination, search, and sorting.

**Query Params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | string | `""` | Filter by type(s), comma-separated. Valid: `fabric`, `jeans`, `cotton` |
| `page` | int | 1 | Page number (min 1) |
| `limit` | int | 20 | Results per page (max 100) |
| `search` | string | `""` | Search keyword (matches name or code, case-insensitive) |
| `sort` | string | `"code"` | Sort field: `code`, `name`, `buy_price`, `type` |
| `order` | string | `"asc"` | Sort direction: `asc` or `desc` |

**Examples:**

```
GET /api/materials                                   # all materials
GET /api/materials?type=fabric                       # filter by type
GET /api/materials?type=fabric,jeans                 # filter by multiple types
GET /api/materials?page=1&limit=10&search=fabric&sort=buy_price&order=desc  # combined
```

**Response (200):**

```json
{
  "materials": [
    {
      "id": 1,
      "code": "M001",
      "name": "Premium Fabric",
      "type": "fabric",
      "buy_price": 250.0,
      "supplier_id": [1, "Supplier ABC"]
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 10,
  "pages": 2
}
```

**Errors:**

| Status | Error | Cause |
|--------|-------|-------|
| 400 | `Invalid material type(s): [...]` | Unknown type value |

---

## GET /api/materials/<id>

Get a single material by ID.

**Example Request:**

```
GET /api/materials/1
```

**Response (200):**

```json
{
  "material": {
    "id": 1,
    "code": "M001",
    "name": "Premium Fabric",
    "type": "fabric",
    "buy_price": 250.0,
    "supplier_id": [1, "Supplier ABC"]
  }
}
```

**Errors:**

| Status | Error | Cause |
|--------|-------|-------|
| 404 | `Material not found` | Invalid material ID |

---

## POST /api/materials

Create a new material.

**Required Fields (JSON body):**

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Unique material code |
| `name` | string | Material name |
| `type` | string | `fabric`, `jeans`, or `cotton` |
| `buy_price` | float | Must be >= 100 |
| `supplier_id` | int | Supplier partner ID |

**Example Request:**

```
POST /api/materials
Content-Type: application/json

{
  "code": "M001",
  "name": "Premium Fabric",
  "type": "fabric",
  "buy_price": 250,
  "supplier_id": 1
}
```

**Response (201):**

```json
{
  "material": [
    {
      "id": 1,
      "code": "M001",
      "name": "Premium Fabric",
      "type": "fabric",
      "buy_price": 250.0,
      "supplier_id": [1, "Supplier ABC"]
    }
  ]
}
```

**Errors:**

| Status | Error | Cause |
|--------|-------|-------|
| 400 | `Missing required fields: [...]` | Required field not provided |
| 400 | `Material Buy Price cannot be less than 100` | Price below minimum |
| 400 | `Material Code must be unique` | Duplicate code |

---

## PATCH /api/materials/<id>

Update an existing material (partial update).

**Body:** Send only fields to change.

**Example Request:**

```
PATCH /api/materials/1
Content-Type: application/json

{
  "buy_price": 300,
  "name": "Updated Name"
}
```

**Response (200):**

```json
{
  "material": [
    {
      "id": 1,
      "code": "M001",
      "name": "Updated Name",
      "type": "fabric",
      "buy_price": 300.0,
      "supplier_id": [1, "Supplier ABC"]
    }
  ]
}
```

**Errors:**

| Status | Error | Cause |
|--------|-------|-------|
| 404 | `Material not found` | Invalid material ID |
| 400 | `Material Buy Price cannot be less than 100` | Price below minimum |

---

## DELETE /api/materials/<id>

Delete a material.

**Example Request:**

```
DELETE /api/materials/1
```

**Response (200):**

```json
{
  "message": "Material deleted successfully"
}
```

**Errors:**

| Status | Error | Cause |
|--------|-------|-------|
| 404 | `Material not found` | Invalid material ID |

---

## POST /api/materials/<id>/archive

Archive a material (soft delete). Sets `active=False`.

**Example Request:**

```
POST /api/materials/1/archive
```

**Response (200):**

```json
{
  "message": "Material archived successfully"
}
```

**Errors:**

| Status | Error | Cause |
|--------|-------|-------|
| 404 | `Material not found` | Invalid material ID |
| 400 | `Material is already archived` | Material already inactive |

---

## POST /api/materials/<id>/unarchive

Unarchive a material (restore). Sets `active=True`.

**Example Request:**

```
POST /api/materials/1/unarchive
```

**Response (200):**

```json
{
  "message": "Material unarchived successfully"
}
```

**Errors:**

| Status | Error | Cause |
|--------|-------|-------|
| 404 | `Material not found` | Invalid material ID |
| 400 | `Material is not archived` | Material already active |

---

## GET /api/materials/available_types

Get all available material type options.

**Response (200):**

```json
{
  "types": [
    ["fabric", "Fabric"],
    ["jeans", "Jeans"],
    ["cotton", "Cotton"]
  ]
}
```

---

## GET /api/materials/suppliers

Get all available suppliers.

**Response (200):**

```json
{
  "suppliers": [
    {"id": 1, "name": "Supplier ABC"},
    {"id": 2, "name": "Supplier XYZ"}
  ]
}
```
