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

    def test_buy_price_boundary_exact_100(self):
        """buy_price == 100 should be allowed (boundary)."""
        material = self.env['materials.material'].create({
            'code': 'M010',
            'name': 'Boundary Material',
            'type': 'cotton',
            'buy_price': 100,
            'supplier_id': self.supplier.id
        })
        self.assertEqual(material.buy_price, 100)

    def test_buy_price_boundary_99_rejected(self):
        """buy_price == 99 should be rejected (just below boundary)."""
        with self.assertRaises(ValidationError):
            self.env['materials.material'].create({
                'code': 'M011',
                'name': 'Below Boundary',
                'type': 'cotton',
                'buy_price': 99,
                'supplier_id': self.supplier.id
            })

    def test_check_code_unique(self):
        """Duplicate code must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.env['materials.material'].create({
                'code': 'M001',
                'name': 'Duplicate Code',
                'type': 'cotton',
                'buy_price': 200,
                'supplier_id': self.supplier.id
            })

    def test_code_unique_on_update(self):
        """Updating code to an existing code must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.material2.write({'code': 'M001'})

    def test_update_material(self):
        self.material1.write({
            'buy_price': 300
        })
        self.assertEqual(self.material1.buy_price, 300)

    def test_delete_material(self):
        self.material1.unlink()
        materials = self.env['materials.material'].search([('code', '=', 'M001')])
        self.assertEqual(len(materials), 0)

    def test_active_field_default_true(self):
        """New materials should be active by default."""
        self.assertTrue(self.material1.active)

    def test_soft_delete_via_active(self):
        """Setting active=False should hide record from default search."""
        self.material1.active = False
        materials = self.env['materials.material'].search([])
        self.assertNotIn(self.material1, materials)
        # Still accessible via explicit search
        mat = self.env['materials.material'].with_context(active_test=False).search([
            ('code', '=', 'M001')
        ])
        self.assertEqual(len(mat), 1)

    def test_copy_material_appends_counter(self):
        """Copying a material should append ' (1)' to the code."""
        copy = self.material1.copy()
        self.assertEqual(copy.code, 'M001 (1)')
        self.assertNotEqual(copy.id, self.material1.id)

    def test_copy_material_increments_counter(self):
        """Copying again should increment the counter."""
        copy1 = self.material1.copy()
        copy2 = self.material1.copy()
        self.assertEqual(copy1.code, 'M001 (1)')
        self.assertEqual(copy2.code, 'M001 (2)')

    def test_copy_material_from_copied_record(self):
        """Copying a copy should strip old counter and use new one."""
        copy1 = self.material1.copy()
        self.assertEqual(copy1.code, 'M001 (1)')
        copy2 = copy1.copy()
        self.assertEqual(copy2.code, 'M001 (2)')
