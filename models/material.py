from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class Material(models.Model):
    _name = 'materials.material'
    _description = 'Material'
    _order = 'code asc'

    code = fields.Char(string='Material Code', required=True)
    name = fields.Char(string='Material Name', required=True)
    type = fields.Selection([
        ('fabric', 'Fabric'),
        ('jeans', 'Jeans'),
        ('cotton', 'Cotton'),
    ], string='Material Type', required=True)
    buy_price = fields.Float(string='Material Buy Price', required=True)
    supplier_id = fields.Many2one('res.partner', string='Supplier', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]):
                raise ValidationError('Material Code must be unique')

    @api.constrains('buy_price')
    def _check_buy_price(self):
        for record in self:
            if record.buy_price < 100:
                raise ValidationError('Material Buy Price cannot be less than 100')

    @api.model
    def get_available_types(self):
        """Return list of available material types."""
        return self._fields['type'].selection

    def copy(self, default=None):
        if default is None:
            default = {}
        # Generate code with counter: M001 -> M001 (1) -> M001 (2)
        base_code = self.code
        match = re.match(r'^(.+) \((\d+)\)$', base_code)
        if match:
            base_code = match.group(1)

        # Find max existing counter for this base code
        existing = self.search([('code', 'like', f'{base_code} (%')])
        max_counter = 0
        for rec in existing:
            m = re.match(r'.+\((\d+)\)$', rec.code)
            if m:
                max_counter = max(max_counter, int(m.group(1)))

        default['code'] = f'{base_code} ({max_counter + 1})'
        return super(Material, self).copy(default)