import json
import logging
from functools import wraps

from werkzeug.wrappers import Response

from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)

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


def _filter_fields(kwargs, allowed_fields):
    """Filter kwargs to only allowed fields.

    Args:
        kwargs: Input fields from request
        allowed_fields: Set of allowed field names

    Returns:
        dict: Filtered fields
    """
    return {k: v for k, v in kwargs.items() if k in allowed_fields}


def _paginate(env, model_name, domain, page, limit, order):
    """Search with pagination, return (records, total_count)."""
    Model = env[model_name]
    total = Model.search_count(domain)
    offset = (page - 1) * limit
    records = Model.search(domain, offset=offset, limit=limit, order=order)
    return records, total


def _parse_pagination(kwargs, valid_sort_fields=None, default_sort='code'):
    """Extract and validate pagination, sort params from kwargs.

    Args:
        kwargs: Request params
        valid_sort_fields: Set of allowed sort fields (domain-specific)
        default_sort: Default sort field if invalid

    Returns:
        tuple: (page, limit, order_string)
    """
    page = max(int(kwargs.get('page', 1)), 1)
    limit = min(max(int(kwargs.get('limit', 20)), 1), 100)

    sort_field = kwargs.get('sort', default_sort)
    sort_order = kwargs.get('order', 'asc')

    if valid_sort_fields and sort_field not in valid_sort_fields:
        sort_field = default_sort
    if sort_order not in ('asc', 'desc'):
        sort_order = 'asc'

    return page, limit, f'{sort_field} {sort_order}'
