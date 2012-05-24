from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import pytz
import base64
import dateutil.parser
from django.conf import settings

from postmark.models import EmailMessage, EmailBounce
from pprint import pprint
try:
    import json                     
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise Exception('Cannot use django-postmark without Python 2.6 or greater, or Python 2.4 or 2.5 and the "simplejson" library')

POSTMARK_DATETIME_STRING = "%Y-%m-%dT%H:%M:%S.%f"
POSTMARK_USE_TZ = getattr(settings, "POSTMARK_USE_TZ", True)

# Settings
POSTMARK_API_USER = getattr(settings, "POSTMARK_API_USER", None)
POSTMARK_API_PASSWORD = getattr(settings, "POSTMARK_API_PASSWORD", None)

if ((POSTMARK_API_USER is not None and POSTMARK_API_PASSWORD is None) or
    (POSTMARK_API_PASSWORD is not None and POSTMARK_API_USER is None)):
    raise ImproperlyConfigured("POSTMARK_API_USER and POSTMARK_API_PASSWORD must both either be set, or unset.")

@csrf_exempt
def bounce(request):
    """
    Accepts Incoming Bounces from Postmark. Example JSON Message:
    
        {
            "ID": 42,
            "Type": "HardBounce",
            "Name": "Hard bounce",
            "Tag": "Test",
            "MessageID": null,
            "Description": "Test bounce description",
            "TypeCode": 1,
            "Details": "Test bounce details",
            "Email": "john@example.com",
            "BouncedAt": "2011-05-23T11:16:00.3018994+01:00",
            "DumpAvailable": true,
            "Inactive": true,
            "CanActivate": true,
            "Content": null,
            "Subject": null
        }

        Example message when Postmark sends test message:
        {
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

        and actual error message:
        {
            u'BouncedAt': u'2012-05-23T19:18:47.756Z',
            u'CanActivate': True,
            u'Details': u'action: failed\r\n',
            u'DumpAvailable': True,
            u'Email': u'bounce@viiiiiiidea.com',
            u'ID': 381077264,
            u'Inactive': True,
            u'MessageID': u'b00e91cc-2401-47af-be63-346762fcc0ca',
            u'Subject': u'Sandbox - access information',
            u'Type': u'HardBounce',
            u'TypeCode': 1
        }

    """
    if request.method in ["POST"]:
        if POSTMARK_API_USER is not None:
            if not request.META.has_key("HTTP_AUTHORIZATION"):
                return HttpResponseForbidden()
                
            type, base64encoded = request.META["HTTP_AUTHORIZATION"].split(" ", 1)
            print type, base64encoded
            
            if type.lower() == "basic":
                username_password = base64.decodestring(base64encoded)
                print username_password
            else:
                return HttpResponseForbidden()
                
            if not username_password == "%s:%s" % (POSTMARK_API_USER, POSTMARK_API_PASSWORD):
                print "lol"
                return HttpResponseForbidden()
        
        bounce_dict = json.loads(request.read())            
        bounced_at = dateutil.parser.parse(bounce_dict["BouncedAt"]).astimezone(pytz.utc)
            
        if POSTMARK_USE_TZ == False:
            bounced_at = bounced_at.replace(tzinfo=None)

        pprint(bounce_dict)
        # for test message, we don't get MessageID
        if not bounce_dict.get('MessageID'):
            return HttpResponse(json.dumps({"status": "ok"}))

        em = get_object_or_404(EmailMessage, message_id=bounce_dict["MessageID"], to=bounce_dict["Email"])
        eb, created = EmailBounce.objects.get_or_create(
            id=bounce_dict["ID"],
            defaults={
                "message": em,
                "type": bounce_dict["Type"],
                "description": bounce_dict.get("Description", ''),
                "details": bounce_dict["Details"],
                "inactive": bounce_dict["Inactive"],
                "can_activate": bounce_dict["CanActivate"],
                "bounced_at": bounced_at,
            }
        )
        
        return HttpResponse(json.dumps({"status": "ok"}))
    else:
        return HttpResponseNotAllowed(['POST'])
