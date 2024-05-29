from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError


class MaterialController(http.Controller):

    @http.route('/materials', type='json', auth='user')
    def get_materials(self):
        try:
            materials = request.env['materials.material'].search([])
            return {
                'materials': materials.read(['id', 'code', 'name', 'type', 'buy_price', 'supplier_id'])
            }
        except Exception as e:
            return {
                'error': str(e)
            }

    @http.route('/materials/filter', type='json', auth='user')
    def filter_materials(self, **kwargs):
        try:
            material_type = kwargs.get('type')
            materials = request.env['materials.material'].search([('type', '=', material_type)])
            return {
                'materials': materials.read(['id', 'code', 'name', 'type', 'buy_price', 'supplier_id'])
            }
        except Exception as e:
            return {
                'error': str(e)
            }

    @http.route('/materials/<int:material_id>', type='json', auth='user')
    def get_material(self, material_id):
        try:
            material = request.env['materials.material'].browse(material_id)
            if not material.exists():
                return {
                    'error': 'Material not found'
                }
            return {
                'material': material.read(['id', 'code', 'name', 'type', 'buy_price', 'supplier_id'])[0]
            }
        except Exception as e:
            return {
                'error': str(e)
            }

    @http.route('/materials/create', type='json', auth='user')
    def create_material(self, **kwargs):
        try:
            material = request.env['materials.material'].create(kwargs)
            return {
                'material': material.read(['id', 'code', 'name', 'type', 'buy_price', 'supplier_id'])
            }
        except ValidationError as e:
            return {
                'error': str(e)
            }
        except Exception as e:
            return {
                'error': str(e)
            }

    @http.route('/materials/<int:material_id>/update', type='json', auth='user')
    def update_material(self, material_id, **kwargs):
        try:
            material = request.env['materials.material'].browse(material_id)
            if not material.exists():
                return {
                    'error': 'Material not found'
                }
            material.write(kwargs)
            return {
                'material': material.read(['id', 'code', 'name', 'type', 'buy_price', 'supplier_id'])
            }
        except ValidationError as e:
            return {
                'error': str(e)
            }
        except Exception as e:
            return {
                'error': str(e)
            }

    @http.route('/materials/<int:material_id>/delete', type='json', auth='user')
    def delete_material(self, material_id):
        try:
            material = request.env['materials.material'].browse(material_id)
            if not material.exists():
                return {
                    'error': 'Material not found'
                }
            material.unlink()
            return {
                'message': 'Material deleted successfully'
            }
        except Exception as e:
            return {
                'error': str(e)
            }

    @http.route('/materials/available_types', type='json', auth='user')
    def get_available_types(self):
        return {
            'types': request.env['materials.material']._fields['type'].selection
        }

    @http.route('/materials/suppliers', type='json', auth='user')
    def get_suppliers(self):
        try:
            suppliers = request.env['res.partner'].search([])
            return {
                'suppliers': suppliers.read(['id', 'name'])
            }
        except Exception as e:
            return {
                'error': str(e)
            }
