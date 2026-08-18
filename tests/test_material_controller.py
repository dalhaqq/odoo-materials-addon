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
        self.assertIn('total', result)
        self.assertEqual(result['total'], 2)
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
        self.assertEqual(result['total'], 1)
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

    # --- Pagination tests ---

    def test_get_materials_pagination(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'page': 1, 'limit': 1},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertEqual(len(result['materials']), 1)
        self.assertEqual(result['total'], 2)
        self.assertEqual(result['page'], 1)
        self.assertEqual(result['limit'], 1)
        self.assertEqual(result['pages'], 2)

    def test_get_materials_pagination_page2(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'page': 2, 'limit': 1},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertEqual(len(result['materials']), 1)
        # Ordered by code asc, page 2 = M002
        self.assertEqual(result['materials'][0]['code'], 'M002')

    # --- Search tests ---

    def test_search_materials_by_name(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'search': 'Material 1'},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['materials'][0]['code'], 'M001')

    def test_search_materials_by_code(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'search': 'M002'},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['materials'][0]['code'], 'M002')

    # --- Sorting tests ---

    def test_sort_materials_by_price_desc(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'sort': 'buy_price', 'order': 'desc'},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        # material1 buy_price=200, material2 buy_price=150 => desc = [200, 150]
        self.assertEqual(result['materials'][0]['buy_price'], 200)
        self.assertEqual(result['materials'][1]['buy_price'], 150)

    # --- Multiple type filter tests ---

    def test_filter_materials_multiple_types(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials/filter', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'type': 'fabric,jeans'},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertNotIn('error', result)
        self.assertEqual(result['total'], 2)
        codes = [m['code'] for m in result['materials']]
        self.assertIn('M001', codes)
        self.assertIn('M002', codes)

    def test_filter_materials_invalid_type(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials/filter', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'type': 'silk'},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertIn('error', result)
        self.assertIn('Invalid material type', result['error'])

    def test_filter_materials_missing_type(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials/filter', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertIn('error', result)
        self.assertIn('Material type is required', result['error'])

    # --- Create missing fields tests ---

    def test_create_material_missing_fields(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials/create', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'code': 'M099'},
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertIn('error', result)
        self.assertIn('Missing required fields', result['error'])

    def test_create_material_duplicate_code(self):
        self.authenticate('testuser', 'testuser')
        response = self.url_open('/materials/create', data=json.dumps({
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'code': 'M001',
                'name': 'Dupe',
                'type': 'cotton',
                'buy_price': 200,
                'supplier_id': self.supplier.id,
            },
        }), headers={'Content-Type': 'application/json'})
        result = response.json()['result']
        self.assertIn('error', result)
        self.assertIn('unique', result['error'].lower())