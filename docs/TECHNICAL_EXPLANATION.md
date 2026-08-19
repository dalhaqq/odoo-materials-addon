# Materials API — Technical Explanation

## Context

This repository is an evolution of a solution I submitted for the same technical test approximately two years ago.

At that time, the implementation focused on fulfilling the functional requirements with a basic Odoo module. Since then, I have gained professional experience in QA and Backend Development, and I decided to revisit the same problem using the engineering practices and experience I have gained since the original submission.

The current implementation was substantially refactored and extended, with particular attention to API design, validation, error handling, security, testing, and maintainability.

The original implementation is preserved in Git history, allowing the evolution of the solution to be reviewed directly.

## Overview

The current module is an Odoo 14 module that exposes a REST-style API for managing materials and their suppliers.

A material contains:

- Material Code
- Material Name
- Material Type (`fabric`, `jeans`, `cotton`)
- Material Buy Price
- Related Supplier

The implementation uses Odoo's ORM and extends `res.partner` with an `is_supplier` flag to identify partners that can be selected as suppliers.

## What Changed

### Original Implementation

The original implementation primarily provided:

- Odoo JSON-RPC endpoints
- Basic CRUD operations
- Separate filtering endpoint
- Basic validation through Odoo
- Minimal automated tests
- Minimal documentation

### Current Implementation

The current version introduces a more structured REST-style API and additional application-level behavior:

- HTTP methods: `GET`, `POST`, `PATCH`, and `DELETE`
- `/api` namespace
- JSON request body support
- HTTP status codes
- Centralized error handling
- Pagination
- Search
- Sorting
- Single and multiple material-type filtering
- Field allowlisting
- Explicit validation
- Supplier filtering
- Access control
- Archive and unarchive operations
- Expanded automated tests
- API documentation
- ERD
- Postman collection

## REST API Architecture

Odoo 14's standard `type='json'` routes are designed around Odoo's JSON-RPC mechanism. For this implementation, the goal was to expose a conventional HTTP API that accepts regular JSON request bodies.

The module therefore introduces a custom `HttpRestRequest` that parses `application/json` request bodies and makes the resulting data available through Odoo's request parameters.

`Root.get_request` is then extended so that requests under `/api` use this custom request implementation, while other Odoo requests continue to use the original request handling behavior.

This keeps the custom behavior scoped to the API namespace rather than changing request handling globally.

## API Design

The API follows conventional HTTP methods:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/materials` | List materials |
| GET | `/api/materials/<id>` | Get a material |
| POST | `/api/materials` | Create a material |
| PATCH | `/api/materials/<id>` | Partially update a material |
| DELETE | `/api/materials/<id>` | Permanently delete a material |
| POST | `/api/materials/<id>/archive` | Archive a material |
| POST | `/api/materials/<id>/unarchive` | Restore an archived material |
| GET | `/api/materials/available_types` | Get available material types |
| GET | `/api/materials/suppliers` | Get suppliers |

The collection endpoint supports multiple query parameters:

```http
GET /api/materials?type=fabric&page=1&limit=20&search=cotton&sort=buy_price&order=desc
```

Supported functionality includes:

- Type filtering
- Multiple type filtering
- Pagination
- Search by material name or code
- Sorting by allowed fields
- Ascending or descending order

The filtering functionality is intentionally part of the collection endpoint instead of introducing a separate `/filter` resource.

For example:

```http
GET /api/materials?type=fabric
```

is preferred over:

```http
GET /api/materials/filter?type=fabric
```

This keeps the API surface smaller and allows filtering, searching, sorting, and pagination to be composed in a single request.

## Request Validation

The API validates input at multiple levels.

### Required Fields

Creating a material requires:

- `code`
- `name`
- `type`
- `buy_price`
- `supplier_id`

Missing fields are rejected with a `400 Bad Request` response.

### Material Type

Only the defined material types are accepted:

- `fabric`
- `jeans`
- `cotton`

The API also supports filtering by multiple types:

```http
GET /api/materials?type=fabric,jeans
```

Invalid types are rejected instead of silently returning an empty result.

### Buy Price

The minimum material buy price is `100`.

The implementation also tests the boundary explicitly:

- `100` → accepted
- `99` → rejected

### Material Code

Material codes must be unique.

The constraint is implemented at the Odoo model level and is tested for both:

- Creating a material with a duplicate code
- Updating an existing material to use another material's code

## Field Allowlisting

The API does not pass arbitrary request fields directly to the Odoo ORM.

Create and update operations first filter incoming fields against an explicit allowlist:

```text
code
name
type
buy_price
supplier_id
```

This prevents clients from modifying fields that are outside the intended API contract.

For example, attempting to submit fields such as `id` or `create_uid` does not allow the client to control those values.

## Error Handling

API errors are handled through a centralized `@handle_errors` decorator.

The implementation distinguishes between different categories of errors:

- `ValidationError` → `400`
- `ValueError` → `400`
- `AccessError` → `403`
- Unexpected exceptions → `500`

Unexpected exceptions are logged internally and return a generic:

```json
{
  "error": "Internal server error"
}
```

This avoids exposing internal exception details to API consumers.

Expected validation errors, on the other hand, return messages that are useful to the client.

For example:

```json
{
  "error": "Material Buy Price cannot be less than 100"
}
```

## Reusable Helpers

Common API behavior is extracted into reusable helper functions:

- `_json_response`
- `handle_errors`
- `_filter_fields`
- `_paginate`
- `_parse_pagination`

This avoids repeating response construction, exception handling, field filtering, and pagination logic across controllers.

Pagination is implemented by calculating an offset and using Odoo's ORM search with `offset`, `limit`, and `order`.

The API also limits the maximum page size to 100 records.

## Supplier Handling

The module extends Odoo's `res.partner` model with:

```text
is_supplier
```

This allows the API to distinguish suppliers from other partners without requiring the `purchase` module.

The supplier endpoint only returns partners where:

```text
is_supplier = True
```

This behavior is also covered by automated tests to ensure regular contacts are excluded from the supplier list.

## Security Model

The module uses Odoo access control groups.

The current access configuration provides:

| Group | Read | Write | Create | Delete |
|---|---|---|---|---|
| Internal User | Yes | No | No | No |
| Settings Manager | Yes | Yes | Yes | Yes |

The API routes require an authenticated Odoo user.

This separates the ability to consume material data from the ability to modify it.

## Material Lifecycle

The model uses Odoo's standard `active` mechanism to support archiving.

A material is active by default:

```text
active = True
```

Archiving a material sets:

```text
active = False
```

while keeping the record in the database.

Unarchiving restores:

```text
active = True
```

This provides a distinction between archiving a material and permanently deleting it.

The API therefore exposes separate operations:

```http
POST /api/materials/<id>/archive
```

and:

```http
POST /api/materials/<id>/unarchive
```

while:

```http
DELETE /api/materials/<id>
```

permanently removes the record.

This explicit separation avoids giving `DELETE` semantics to an operation that only changes the record's active state.

The archive and unarchive operations also make use of Odoo's standard `active_test` behavior, so archived materials are excluded from normal searches while remaining available when explicitly requested.

## Copy Behavior

The material model overrides Odoo's `copy()` behavior so that copied materials receive a new code.

For example:

```text
M001
M001 (1)
M001 (2)
```

Copying a previously copied material also continues the counter rather than producing nested values such as:

```text
M001 (1) (1)
```

This behavior is covered by dedicated unit tests.

## Testing

The test suite contains both model-level and HTTP-level tests.

### Model Tests

Model tests cover:

- Material creation
- Material retrieval
- Material filtering
- Buy price validation
- Buy price boundary conditions
- Unique material codes
- Unique code validation during updates
- Material updates
- Material deletion
- Active/archive behavior
- Copy behavior
- Supplier flag behavior

### Controller Tests

HTTP tests cover:

- Listing materials
- Getting a material by ID
- Creating materials
- Updating materials
- Deleting materials
- Archiving materials
- Unarchiving materials
- Missing resources
- Required fields
- Duplicate codes
- Invalid buy prices
- Invalid input types
- Pagination
- Pagination boundaries
- Searching by name
- Searching by code
- Sorting
- Single and multiple type filtering
- Invalid material types
- Supplier filtering
- Ignoring disallowed fields
- Invalid update fields
- Available material types
- Available suppliers

The test suite covers both normal application flows and invalid input scenarios.

## Documentation and Supporting Files

The repository includes supporting documentation and tooling.

### API Documentation

`docs/API.md` contains endpoint descriptions, parameters, request examples, response examples, and common error responses.

### ERD

`docs/ERD.md` documents the main database entities and their relationships, including:

- `materials.material`
- `res.partner`
- `res.users`

It also documents validation rules and the security model.

### Postman Collection

`docs/postman_collection.json` provides requests for:

- Authentication
- Material listing
- Searching
- Filtering
- Getting a material
- Creating a material
- Updating a material
- Deleting a material
- Archiving a material
- Unarchiving a material
- Getting material types
- Getting suppliers
- Testing common error scenarios

This allows the API to be manually tested without having to construct every request from scratch.

## Design Decisions

### Why a REST-style API?

The goal was to expose the material functionality through a conventional HTTP interface rather than coupling the API endpoints to Odoo's JSON-RPC request structure.

This makes the API easier to consume from external clients and keeps resource-oriented operations explicit.

### Why use Odoo's ORM?

The module remains an Odoo module, so using the ORM preserves Odoo's model behavior, access control, validation mechanisms, and relationship handling.

The API layer is therefore responsible primarily for HTTP concerns, while the model layer remains responsible for domain-level validation and data access.

### Why use an `is_supplier` flag?

The requirement only needs a way to identify which partners are suppliers.

Adding a simple boolean field avoids introducing the larger `purchase` dependency solely to obtain supplier functionality.

### Why allowlist fields?

The API should expose only fields that are part of its public contract.

Allowlisting prevents clients from attempting to manipulate internal Odoo fields through arbitrary request parameters.

### Why separate archive and delete?

Archiving and deletion have different business implications.

Archiving preserves the record while making it inactive, whereas deletion permanently removes it.

Exposing them as separate operations makes their behavior explicit:

```text
POST /api/materials/<id>/archive
    → active = False

POST /api/materials/<id>/unarchive
    → active = True

DELETE /api/materials/<id>
    → permanent deletion
```

This also aligns the archive behavior with Odoo's existing `active` convention.

## What This Demonstrates

The main purpose of this repository is to demonstrate how my approach to the same problem has evolved since the original implementation.

In particular, it demonstrates:

1. **Backend engineering growth** — moving from a basic CRUD implementation toward a more structured API.
2. **Odoo-specific problem solving** — implementing JSON request handling for a REST-style API while remaining compatible with Odoo 14.
3. **API design** — using HTTP methods, status codes, query parameters, pagination, filtering, searching, and sorting.
4. **Validation and data integrity** — enforcing business rules at the model and API layers.
5. **Security awareness** — separating read access from modification privileges and preventing arbitrary field updates.
6. **Error handling** — distinguishing expected client errors from unexpected server errors.
7. **Resource lifecycle management** — explicitly separating archiving from permanent deletion.
8. **Testing** — covering both model behavior and HTTP-level behavior, including boundary and invalid-input cases.
9. **Maintainability** — extracting reusable helpers and keeping responsibilities separated between the API and model layers.
10. **Documentation** — providing API documentation, ERD, Postman collection, and implementation notes.

The original implementation is preserved in Git history, making the progression between the two implementations directly reviewable.
