import json
import logging

import odoo
from odoo.http import HttpRequest, Root, request

_logger = logging.getLogger(__name__)


class HttpRestRequest(HttpRequest):
    """HTTP request that supports application/json content-type.

    Extends HttpRequest so routes declared with type='http' can accept JSON bodies.
    Parses application/json body into self.params automatically.
    """

    def __init__(self, httprequest):
        super(HttpRestRequest, self).__init__(httprequest)
        if self.httprequest.mimetype == 'application/json':
            data = self.httprequest.get_data().decode(self.httprequest.charset)
            try:
                body = json.loads(data) if data else {}
                # Support both plain JSON and JSON-RPC wrapper
                if 'params' in body and isinstance(body['params'], dict):
                    self.params = body['params']
                else:
                    self.params = body
            except ValueError as e:
                _logger.info('Invalid JSON data: %s: %s', self.httprequest.path, e)
                from werkzeug.exceptions import BadRequest
                raise BadRequest('Invalid JSON data: %s' % str(e))
        elif self.httprequest.mimetype == 'multipart/form-data':
            pass
        else:
            # Parse query string params from URL
            from werkzeug.urls import url_decode
            self.params = url_decode(self.httprequest.query_string.decode('utf-8'))


# Store original get_request method
_original_get_request = Root.get_request


def _get_request(self, httprequest):
    """Monkey-patch Root.get_request to use HttpRestRequest for /api routes."""
    db = httprequest.session.db
    if db and odoo.service.db.exp_db_exist(db):
        # Ensure registry is loaded
        odoo.registry(db)

        # Check if this request matches our REST API routes
        if httprequest.path.startswith('/api'):
            return HttpRestRequest(httprequest)

    return _original_get_request(self, httprequest)


# Apply monkey-patch
Root.get_request = _get_request
