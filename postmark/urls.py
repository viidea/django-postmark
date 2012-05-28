from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns("",
    url(r"^bounce/$", "postmark.views.bounce", name="postmark_bounce_hook"),
)