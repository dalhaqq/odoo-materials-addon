# Materials API — Odoo 14

A custom Odoo 14 module for registering and managing materials through a REST-style API.

The module implements material CRUD operations, supplier management, validation, pagination, search, sorting, filtering, archive/unarchive, access control, and automated tests.

## Requirements

- Odoo 14

## Installation

```sh
git clone https://github.com/dalhaqq/odoo-materials-addon.git /path/to/odoo/addons/materials
```

Restart Odoo, update module list, install "Materials".
## Features

- REST-style API under the `/api` namespace
- Material CRUD operations
- Material type validation:
  - `fabric`
  - `jeans`
  - `cotton`
- Supplier management through `res.partner`
- Minimum buy price validation
- Unique material code validation
- Pagination
- Search by material code and name
- Sorting
- Single and multiple material-type filtering
- Request field allowlisting
- Centralized API error handling
- HTTP status codes
- Archive and unarchive operations
- Permanent deletion
- Odoo access control
- Automated model and controller tests
- Postman collection for manual testing

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/materials` | List materials |
| GET | `/api/materials/<id>` | Get a material |
| POST | `/api/materials` | Create a material |
| PATCH | `/api/materials/<id>` | Update a material |
| DELETE | `/api/materials/<id>` | Permanently delete a material |
| POST | `/api/materials/<id>/archive` | Archive a material |
| POST | `/api/materials/<id>/unarchive` | Unarchive a material |
| GET | `/api/materials/available_types` | Get available material types |
| GET | `/api/materials/suppliers` | Get suppliers |

## Documentation

- [API Documentation](docs/API.md) — API endpoints, parameters, request/response examples, and error responses
- [Technical Explanation](docs/TECHNICAL_EXPLANATION.md) — architecture, design decisions, validation, security, testing, and implementation notes
- [ERD](docs/ERD.md) — database schema and relationships
- [Postman Collection](docs/postman_collection.json) — collection for manual API testing

## Testing

The repository contains both model-level and HTTP-level automated tests.

The test suite covers:

- Material CRUD
- Validation
- Buy price boundary conditions
- Duplicate material codes
- Pagination
- Search
- Sorting
- Filtering
- Supplier filtering
- Field allowlisting
- Archive/unarchive
- Error responses
- Access-related behavior
- Copy behavior

Run the module tests using the provided Odoo development/test setup.

```sh
odoo-bin -d test_db --test-tags /material -i materials --stop-after-init
```

## Technical Context

This repository is an evolution of a solution submitted for the same technical test approximately two years ago.

The current implementation was substantially refactored and extended based on experience gained since the original submission, particularly in backend development, API design, testing, validation, security, and maintainability.

The original implementation is preserved in Git history for comparison.

For the detailed rationale behind the implementation, see [Technical Explanation](docs/TECHNICAL_EXPLANATION.md).

## License

LGPL-3
