import logging
from functools import wraps
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


MATERIAL_FIELDS = ['id', 'code', 'name', 'type', 'buy_price', 'supplier_id']
VALID_SORT_FIELDS = {'code', 'name', 'buy_price', 'type'}


def handle_errors(func):
    """Decorator that catches exceptions and returns error dict.
    
    - ValidationError, ValueError, AccessError: returns message to user
    - Other exceptions: logs error, returns generic message
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return {'error': str(e)}
        except ValueError as e:
            return {'error': f'Invalid input: {e}'}
        except AccessError:
            return {'error': 'Permission denied'}
        except Exception as e:
            _logger.exception('Unexpected error in %s', func.__name__)
            return {'error': 'Internal server error'}
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

    @http.route('/materials', type='json', auth='user')
    @handle_errors
    def get_materials(self, **kwargs):
        """List materials with pagination, search, and sorting."""
        page, limit, order = _parse_pagination(kwargs)
        search = kwargs.get('search', '').strip()

        domain = [('active', '=', True)]
        if search:
            domain += ['|', ('name', 'ilike', search), ('code', 'ilike', search)]

        materials, total = _paginate(
            request.env, 'materials.material', domain, page, limit, order
        )
        return {
            'materials': materials.read(MATERIAL_FIELDS),
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit if limit else 1,
        }

    @http.route('/materials/filter', type='json', auth='user')
    @handle_errors
    def filter_materials(self, **kwargs):
        """Filter materials by type (comma-separated for multiple)."""
        material_type = kwargs.get('type')
        if not material_type:
            return {'error': 'Material type is required'}

        valid_types = [t[0] for t in request.env['materials.material'].get_available_types()]
        types = [t.strip() for t in material_type.split(',') if t.strip()]
        invalid = [t for t in types if t not in valid_types]
        if invalid:
            return {'error': f'Invalid material type(s): {invalid}. Must be one of: {valid_types}'}

        page, limit, order = _parse_pagination(kwargs)
        domain = [('active', '=', True), ('type', 'in', types)]

        materials, total = _paginate(
            request.env, 'materials.material', domain, page, limit, order
        )
        return {
            'materials': materials.read(MATERIAL_FIELDS),
            'total': total,
            'page': page,
            'limit': limit,
        }

    @http.route('/materials/<int:material_id>', type='json', auth='user')
    @handle_errors
    def get_material(self, material_id):
        """Get a single material by ID."""
        material = request.env['materials.material'].get_by_id(material_id)
        if not material:
            return {'error': 'Material not found'}
        return {'material': material.read(MATERIAL_FIELDS)[0]}

    @http.route('/materials/create', type='json', auth='user')
    @handle_errors
    def create_material(self, **kwargs):
        """Create a new material. Required: code, name, type, buy_price, supplier_id."""
        required_fields = ['code', 'name', 'type', 'buy_price', 'supplier_id']
        missing = [f for f in required_fields if f not in kwargs or not kwargs[f]]
        if missing:
            return {'error': f'Missing required fields: {missing}'}

        material = request.env['materials.material'].create(kwargs)
        return {'material': material.read(MATERIAL_FIELDS)}

    @http.route('/materials/<int:material_id>/update', type='json', auth='user')
    @handle_errors
    def update_material(self, material_id, **kwargs):
        """Update an existing material (partial update)."""
        material = request.env['materials.material'].get_by_id(material_id)
        if not material:
            return {'error': 'Material not found'}
        material.write(kwargs)
        return {'material': material.read(MATERIAL_FIELDS)}

    @http.route('/materials/<int:material_id>/delete', type='json', auth='user')
    @handle_errors
    def delete_material(self, material_id):
        """Delete a material."""
        material = request.env['materials.material'].get_by_id(material_id)
        if not material:
            return {'error': 'Material not found'}
        material.unlink()
        return {'message': 'Material deleted successfully'}

    @http.route('/materials/available_types', type='json', auth='user')
    @handle_errors
    def get_available_types(self):
        """List available material types."""
        return {'types': request.env['materials.material'].get_available_types()}

    @http.route('/materials/suppliers', type='json', auth='user')
    @handle_errors
    def get_suppliers(self):
        """List all suppliers."""
        suppliers = request.env['res.partner'].search([])
        return {'suppliers': suppliers.read(['id', 'name'])}
