from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('material')
class TestMaterial(TransactionCase):
    def setUp(self):
        super(TestMaterial, self).setUp()
        self.supplier = self.env['res.partner'].create({
            'name': 'Supplier 1',
            'email': 'supplier1@mail.com',
            'phone': '1234567890',
            'street': 'Supplier Street',
            'city': 'Supplier City',
            'zip': '123456'
        })
        self.material1 = self.env['materials.material'].create({
            'code': 'M001',
            'name': 'Material 1',
            'type': 'fabric',
            'buy_price': 200,
            'supplier_id': self.supplier.id
        })
        self.material2 = self.env['materials.material'].create({
            'code': 'M002',
            'name': 'Material 2',
            'type': 'jeans',
            'buy_price': 150,
            'supplier_id': self.supplier.id
        })

    def test_get_materials(self):
        materials = self.env['materials.material'].search([])
        self.assertEqual(len(materials), 2)
        self.assertEqual(materials[0].code, 'M001')
        self.assertEqual(materials[1].code, 'M002')

    def test_filter_materials(self):
        materials = self.env['materials.material'].search([('type', '=', 'fabric')])
        self.assertEqual(len(materials), 1)
        self.assertEqual(materials.code, 'M001')

    def test_create_material(self):
        material = self.env['materials.material'].create({
            'code': 'M003',
            'name': 'Material 3',
            'type': 'cotton',
            'buy_price': 250,
            'supplier_id': self.supplier.id
        })
        self.assertEqual(material.code, 'M003')
        self.assertEqual(material.name, 'Material 3')
        self.assertEqual(material.type, 'cotton')
        self.assertEqual(material.buy_price, 250)
        self.assertEqual(material.supplier_id, self.supplier)

    def test_check_buy_price(self):
        with self.assertRaises(ValidationError):
            self.env['materials.material'].create({
                'code': 'M005',
                'name': 'Material 5',
                'type': 'jeans',
                'buy_price': 50,
                'supplier_id': self.supplier.id
            })

    def test_update_material(self):
        self.material1.write({
            'buy_price': 300
        })
        self.assertEqual(self.material1.buy_price, 300)

    def test_delete_material(self):
        self.material1.unlink()
        materials = self.env['materials.material'].search([('code', '=', 'M001')])
        self.assertEqual(len(materials), 0)
