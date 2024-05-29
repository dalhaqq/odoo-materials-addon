# Odoo Material Management Module

## Overview
This Odoo 14 module allows users to register materials to be sold with the following attributes:
- Material Code
- Material Name
- Material Type (Fabric, Jeans, Cotton)
- Material Buy Price
- Related Supplier

## Requirements
- Odoo 14
- `contacts` module

## Installation
1. Install `contacts` module (optional since it will be installed automatically if not already installed)
2. Clone the repository into your Odoo addons directory:
 ```sh
 git clone https://github.com/dalhaqq/odoo-materials-addon.git /path/to/odoo/addons/materials
 ```
3. Restart Odoo and update the module list
4. Install the module "Materials" from the Odoo Apps menu

## Usage
API endpoints are available to manage materials and suppliers. The following endpoints are available:

| Endpoint                     |Description|Example|
|------------------------------|-------------------------|-------------------------------------------------------------------------------------------------|
| `/materials`                 | Get all materials ||
| `/materials/<id>`            | Get a material by ID ||
| `/materials/filter`          | Filter materials by type | `{ "type": "fabric" }` |
| `/materials/create`          | Create a new material | `{ "code": "M001", "name": "Material 1", "type": "fabric", "buy_price": 100, "supplier_id": 1 }` |
| `/materials/<id>update`      | Update a material | `{ "type": "jeans", "buy_price": 150, "supplier_id": 1 }` |
| `/materials/<id>/delete`     | Delete a material ||
| `/materials/available_types` | Get all available material types ||
| `/materials/suppliers`       | Get all suppliers ||

## License
This module is licensed under the MIT License. You are free to use, modify, and distribute this software.