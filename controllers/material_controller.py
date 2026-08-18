from odoo import http
from odoo.http import request

from ..rest.helpers import (
    _json_response, handle_errors, _filter_fields, _paginate, _parse_pagination,
)

MATERIAL_FIELDS = ['id', 'code', 'name', 'type', 'buy_price', 'supplier_id']
ALLOWED_FIELDS = {'code', 'name', 'type', 'buy_price', 'supplier_id'}
VALID_SORT_FIELDS = {'code', 'name', 'buy_price', 'type'}


class MaterialController(http.Controller):

    @http.route('/api/materials', type='http', auth='user', methods=['GET'], csrf=False)
    @handle_errors
    def list_materials(self, **kwargs):
        """List materials with optional type filter, pagination, search, and sorting."""
        page, limit, order = _parse_pagination(kwargs, VALID_SORT_FIELDS)
        search = kwargs.get('search', '').strip()
        material_type = kwargs.get('type', '').strip()

        domain = [('active', '=', True)]

        # Search filter
        if search:
            domain += ['|', ('name', 'ilike', search), ('code', 'ilike', search)]

        # Type filter (comma-separated for multiple)
        if material_type:
            valid_types = [t[0] for t in request.env['materials.material'].get_available_types()]
            types = [t.strip() for t in material_type.split(',') if t.strip()]
            invalid = [t for t in types if t not in valid_types]
            if invalid:
                return _json_response(
                    {'error': f'Invalid material type(s): {invalid}. Must be one of: {valid_types}'},
                    status=400,
                )
            domain.append(('type', 'in', types))

        materials, total = _paginate(
            request.env, 'materials.material', domain, page, limit, order
        )
        return _json_response({
            'materials': materials.read(MATERIAL_FIELDS),
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit if limit else 1,
        })

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['GET'], csrf=False)
    @handle_errors
    def get_material(self, material_id):
        """Get a single material by ID."""
        material = request.env['materials.material'].get_by_id(material_id)
        if not material:
            return _json_response({'error': 'Material not found'}, status=404)
        return _json_response({'material': material.read(MATERIAL_FIELDS)[0]})

    @http.route('/api/materials', type='http', auth='user', methods=['POST'], csrf=False)
    @handle_errors
    def create_material(self, **kwargs):
        """Create a new material. Required: code, name, type, buy_price, supplier_id."""
        filtered = _filter_fields(kwargs, ALLOWED_FIELDS)

        required_fields = ['code', 'name', 'type', 'buy_price', 'supplier_id']
        missing = [f for f in required_fields if f not in filtered]
        if missing:
            return _json_response({'error': f'Missing required fields: {missing}'}, status=400)

        # Odoo ORM handles type validation and model constraints
        material = request.env['materials.material'].create(filtered)
        return _json_response({'material': material.read(MATERIAL_FIELDS)}, status=201)

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['PATCH'], csrf=False)
    @handle_errors
    def update_material(self, material_id, **kwargs):
        """Update an existing material (partial update)."""
        material = request.env['materials.material'].get_by_id(material_id)
        if not material:
            return _json_response({'error': 'Material not found'}, status=404)

        filtered = _filter_fields(kwargs, ALLOWED_FIELDS)
        if not filtered:
            return _json_response({'error': 'No valid fields to update'}, status=400)

        # Odoo ORM handles type validation and model constraints
        material.write(filtered)
        return _json_response({'material': material.read(MATERIAL_FIELDS)})

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    @handle_errors
    def delete_material(self, material_id):
        """Delete a material."""
        material = request.env['materials.material'].get_by_id(material_id)
        if not material:
            return _json_response({'error': 'Material not found'}, status=404)
        material.unlink()
        return _json_response({'message': 'Material deleted successfully'})

    @http.route('/api/materials/available_types', type='http', auth='user', methods=['GET'], csrf=False)
    @handle_errors
    def get_available_types(self):
        """List available material types."""
        return _json_response({'types': request.env['materials.material'].get_available_types()})

    @http.route('/api/materials/suppliers', type='http', auth='user', methods=['GET'], csrf=False)
    @handle_errors
    def get_suppliers(self):
        """List all partners flagged as suppliers."""
        suppliers = request.env['res.partner'].search([('is_supplier', '=', True)])
        return _json_response({'suppliers': suppliers.read(['id', 'name'])})
