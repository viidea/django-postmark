from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from postmark.models import EmailBounce
import json

class PostmarkViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def testBounceTestMessage(self):
        data = {
            'ID': 42,
            'Type': u'HardBounce',
            'Name': u'Hard bounce',
            'Tag': u'Test',
            'BouncedAt': u'2012-05-23T13:49:48.0254-04:00',
            'CanActivate': True,
            'Description': u'Test bounce description',
            'Details': u'Test bounce details',
            'DumpAvailable': True,
            'Email': u'john@example.com',
            'Inactive': True,
            'TypeCode': 1
        }
        data_json = json.dumps(data)

        response = self.client.post(reverse('postmark_bounce_hook'), json.dumps(data), "text/json")
        data = json.loads(response.content)
        self.assertEqual(data.get('status'), 'ok')

    def testBounceMessage(self):
        data = {
            'BouncedAt': u'2012-05-23T19:18:47.756Z',
            'CanActivate': True,
            'Details': u'action: failed\r\n',
            'DumpAvailable': True,
            'Email': u'bounce@exxxample.con',
            'ID': 381077264,
            'Inactive': True,
            'MessageID': u'b00e91cc-2401-47af-be63-346762fcc0ca',
            'Subject': u'Sandbox - access information',
            'Type': u'HardBounce',
            'TypeCode': 1
        }
        data_json = json.dumps(data)

        response = self.client.post(reverse('postmark_bounce_hook'), json.dumps(data), "text/json")
        resp = json.loads(response.content)
        self.assertEqual(resp.get('status'), 'ok')

        msg = EmailBounce.objects.all().latest('id')
        self.assertEqual(data['MessageID'], msg.msg_id)
