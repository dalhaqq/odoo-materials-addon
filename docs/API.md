# Materials API Reference

All endpoints use **JSON-RPC** over HTTP POST. Authenticate via Odoo session cookie.

Base URL: `http://<odoo-host>/materials`

---

## POST /materials

List all active materials with pagination, search, and sorting.

**Params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number (min 1) |
| `limit` | int | 20 | Results per page (max 100) |
| `search` | string | `""` | Search keyword (matches name or code, case-insensitive) |
| `sort` | string | `"code"` | Sort field: `code`, `name`, `buy_price`, `type` |
| `order` | string | `"asc"` | Sort direction: `asc` or `desc` |

**Example Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "page": 1,
    "limit": 10,
    "search": "fabric",
    "sort": "buy_price",
    "order": "desc"
  }
}
```

**Response:**

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

---

## POST /materials/filter

Filter materials by type (single or multiple).

**Params:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Material type(s), comma-separated for multiple |
| `page` | int | - | Page number, default 1 |
| `limit` | int | - | Results per page, default 20, max 100 |
| `sort` | string | - | Sort field, default `code` |
| `order` | string | - | Sort direction, default `asc` |

Valid types: `fabric`, `jeans`, `cotton`

**Example Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "type": "fabric,jeans"
  }
}
```

**Response:**

```json
{
  "materials": [...],
  "total": 8,
  "page": 1,
  "limit": 20
}
```

**Errors:**

| Error | Cause |
|-------|-------|
| `Material type is required` | `type` param missing |
| `Invalid material type(s): [...]` | Unknown type value |

---

## POST /materials/<id>

Get a single material by ID.

**Example Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "call"
}
```

**Response:**

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

| Error | Cause |
|-------|-------|
| `Material not found` | Invalid material ID |

---

## POST /materials/create

Create a new material.

**Required Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Unique material code |
| `name` | string | Material name |
| `type` | string | `fabric`, `jeans`, or `cotton` |
| `buy_price` | float | Must be >= 100 |
| `supplier_id` | int | Supplier partner ID |

**Example Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "code": "M001",
    "name": "Premium Fabric",
    "type": "fabric",
    "buy_price": 250,
    "supplier_id": 1
  }
}
```

**Response:**

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

| Error | Cause |
|-------|-------|
| `Missing required fields: [...]` | Required field not provided |
| `Material Buy Price cannot be less than 100` | Price below minimum |
| `Material Code must be unique` | Duplicate code |

---

## POST /materials/<id>/update

Update an existing material (partial update).

**Params:** Send only fields to change.

**Example Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "buy_price": 300,
    "name": "Updated Name"
  }
}
```

**Response:**

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

| Error | Cause |
|-------|-------|
| `Material not found` | Invalid material ID |
| `Material Buy Price cannot be less than 100` | Price below minimum |

---

## POST /materials/<id>/delete

Delete a material.

**Example Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "call"
}
```

**Response:**

```json
{
  "message": "Material deleted successfully"
}
```

**Errors:**

| Error | Cause |
|-------|-------|
| `Material not found` | Invalid material ID |

---

## POST /materials/available_types

Get all available material type options.

**Response:**

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

## POST /materials/suppliers

Get all available suppliers.

**Response:**

```json
{
  "suppliers": [
    {"id": 1, "name": "Supplier ABC"},
    {"id": 2, "name": "Supplier XYZ"}
  ]
}
```
