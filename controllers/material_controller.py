import json
import logging
from functools import wraps

from werkzeug.wrappers import Response

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


MATERIAL_FIELDS = ['id', 'code', 'name', 'type', 'buy_price', 'supplier_id']
VALID_SORT_FIELDS = {'code', 'name', 'buy_price', 'type'}


def _json_response(data, status=200):
    """Create a JSON response with proper status code."""
    return Response(
        status=status,
        content_type='application/json; charset=utf-8',
        response=json.dumps(data, default=str),
    )


def handle_errors(func):
    """Decorator that catches exceptions and returns JSON error responses.

    - ValidationError, ValueError: shows message to user (client error)
    - AccessError: shows permission denied (403)
    - Other exceptions: logs error, returns generic message (500)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return _json_response({'error': str(e)}, status=400)
        except ValueError as e:
            return _json_response({'error': f'Invalid input: {e}'}, status=400)
        except AccessError:
            return _json_response({'error': 'Permission denied'}, status=403)
        except Exception as e:
            _logger.exception('Unexpected error in %s', func.__name__)
            return _json_response({'error': 'Internal server error'}, status=500)
    return wrapper


def _paginate(env, model_name, domain, page, limit, order):
    """Search with pagination, return (records, total_count)."""
    Model = env[model_name]
    total = Model.search_count(domain)
    offset = (page - 1) * limit
    records = Model.search(domain, offset=offset, limit=limit, order=order)
    return records, total


def _parse_pagination(kwargs):
    """Extract and validate pagination, sort params from kwargs.

    Returns:
        tuple: (page, limit, order_string)
    """
    page = max(int(kwargs.get('page', 1)), 1)
    limit = min(max(int(kwargs.get('limit', 20)), 1), 100)

    sort_field = kwargs.get('sort', 'code')
    sort_order = kwargs.get('order', 'asc')

    if sort_field not in VALID_SORT_FIELDS:
        sort_field = 'code'
    if sort_order not in ('asc', 'desc'):
        sort_order = 'asc'

    return page, limit, f'{sort_field} {sort_order}'


class MaterialController(http.Controller):

    @http.route('/api/materials', type='http', auth='user', methods=['GET'], csrf=False)
    @handle_errors
    def list_materials(self, **kwargs):
        """List materials with pagination, search, and sorting."""
        page, limit, order = _parse_pagination(kwargs)
        search = kwargs.get('search', '').strip()

        domain = [('active', '=', True)]
        if search:
            domain += ['|', ('name', 'ilike', search), ('code', 'ilike', search)]

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

    @http.route('/api/materials/filter', type='http', auth='user', methods=['GET'], csrf=False)
    @handle_errors
    def filter_materials(self, **kwargs):
        """Filter materials by type (comma-separated for multiple)."""
        material_type = kwargs.get('type')
        if not material_type:
            return _json_response({'error': 'Material type is required'}, status=400)

        valid_types = [t[0] for t in request.env['materials.material'].get_available_types()]
        types = [t.strip() for t in material_type.split(',') if t.strip()]
        invalid = [t for t in types if t not in valid_types]
        if invalid:
            return _json_response(
                {'error': f'Invalid material type(s): {invalid}. Must be one of: {valid_types}'},
                status=400,
            )

        page, limit, order = _parse_pagination(kwargs)
        domain = [('active', '=', True), ('type', 'in', types)]

        materials, total = _paginate(
            request.env, 'materials.material', domain, page, limit, order
        )
        return _json_response({
            'materials': materials.read(MATERIAL_FIELDS),
            'total': total,
            'page': page,
            'limit': limit,
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
        required_fields = ['code', 'name', 'type', 'buy_price', 'supplier_id']
        missing = [f for f in required_fields if f not in kwargs or not kwargs[f]]
        if missing:
            return _json_response({'error': f'Missing required fields: {missing}'}, status=400)

        material = request.env['materials.material'].create(kwargs)
        return _json_response({'material': material.read(MATERIAL_FIELDS)}, status=201)

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['PATCH'], csrf=False)
    @handle_errors
    def update_material(self, material_id, **kwargs):
        """Update an existing material (partial update)."""
        material = request.env['materials.material'].get_by_id(material_id)
        if not material:
            return _json_response({'error': 'Material not found'}, status=404)
        material.write(kwargs)
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
