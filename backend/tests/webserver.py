from unittest import TestCase

from web import app
import json

class FlaskTest(TestCase):

    def setUp(self):
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['WTF_CSRF_METHODS'] = []
        app.config['TRAP_BAD_REQUEST_ERRORS'] = False
        app.testing = True
        self.tc = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        rv = self.tc.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_capabilities(self):
        rv = self.tc.get('/api/capabilities/')
        self.assertEqual(rv.status_code, 200)

    def test_fail_script_GET(self):
        rv = self.tc.get('/api/script/')
        self.assertEqual(rv.status_code, 405)

    def test_fail_script_no_script(self):
        rv = self.tc.post('/api/script/', content_type='application/json', charset='UTF-8')
        self.assertEqual(rv.status_code, 400)

    def test_fail_script_empty(self):
        rv = self.tc.post('/api/script/', data="", content_type='application/json', charset='UTF-8')
        self.assertEqual(rv.status_code, 400)

        rv = self.tc.post('/api/script/', data="{}", content_type='application/json', charset='UTF-8')
        res = json.loads(rv.data)
        self.assertIn("error", res)
        self.assertEqual(res["error"], "No script sent")
        self.assertEqual(rv.status_code, 200)

    def test_script(self):
        script = open("../data/presets/iceland2013.json").read()
        rv = self.tc.post('/api/script/', data=script, content_type='application/json', charset='UTF-8')
        res = json.loads(rv.data)
        self.assertEqual(rv.status_code, 200)
