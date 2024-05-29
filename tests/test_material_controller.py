import json

from odoo.tests.common import HttpCase, tagged


@tagged('-at_install', 'post_install', 'material')
class TestMaterialController(HttpCase):
    def setUp(self):
        super(TestMaterialController, self).setUp()
        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'password': 'testuser',
            'email': 'test@mail.com'
        })
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
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertIn('materials', result)
        materials = result['materials']
        self.assertEqual(len(materials), 2)
        self.assertEqual(materials[0]['code'], 'M001')
        self.assertEqual(materials[1]['code'], 'M002')

    def test_filter_materials(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials/filter', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'type': 'fabric'
            },
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertIn('materials', result)
        materials = result['materials']
        self.assertEqual(len(materials), 1)
        self.assertEqual(materials[0]['code'], 'M001')
        self.assertEqual(materials[0]['type'], 'fabric')

    def test_get_material_by_id(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open(f'/materials/{self.material1.id}', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertIn('material', result)
        material = result['material']
        self.assertEqual(material['code'], 'M001')
        self.assertEqual(material['name'], 'Material 1')

    def test_create_material_validation_error(self):
        self.authenticate('testuser', 'testuser')
        new_material = {
            'code': 'M003',
            'name': 'Material 3',
            'type': 'cotton',
            'buy_price': 50,
            'supplier_id': self.supplier.id
        }
        response = self.url_open('/materials/create', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': new_material
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertIn('error', result)
        self.assertIn('Material Buy Price cannot be less than 100', result['error'])

    def test_create_material(self):
        self.authenticate('testuser', 'testuser')
        new_material = {
            'code': 'M003',
            'name': 'Material 3',
            'type': 'cotton',
            'buy_price': 250,
            'supplier_id': self.supplier.id
        }
        response = self.url_open('/materials/create', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': new_material,
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertIn('material', result)
        material = result['material'][0]
        self.assertEqual(material['code'], 'M003')
        self.assertEqual(material['name'], 'Material 3')
        self.assertEqual(material['type'], 'cotton')
        self.assertEqual(material['buy_price'], 250)
        self.assertEqual(material['supplier_id'][0], self.supplier.id)

    def test_update_material_not_found(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open(f'/materials/100/update', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'buy_price': 300},
            'material_id': 100,
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertIn('error', result)
        self.assertIn('Material not found', result['error'])

    def test_update_material(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open(f'/materials/{self.material1.id}/update', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'buy_price': 300},
            'material_id': self.material1.id,
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertIn('material', result)
        self.assertGreater(len(result['material']), 0)
        self.assertEqual(result['material'][0]['buy_price'], 300)

    def test_delete_material_not_found(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open(f'/materials/100/delete', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertIn('error', result)
        self.assertIn('Material not found', result['error'])

    def test_delete_material(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open(f'/materials/{self.material1.id}/delete', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertIn('message', result)
        self.assertIn('Material deleted successfully', result['message'])

    def test_get_available_types(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials/available_types', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertIn('types', result)
        types = result['types']
        self.assertEqual(len(types), 3)
        self.assertIn(['fabric', 'Fabric'], types)
        self.assertIn(['jeans', 'Jeans'], types)
        self.assertIn(['cotton', 'Cotton'], types)

    def test_get_available_suppliers(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials/suppliers', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertIn('suppliers', result)
        suppliers = result['suppliers']
        self.assertGreater(len(suppliers), 0)
        self.assertIn({'id': self.supplier.id, 'name': self.supplier.name}, suppliers)