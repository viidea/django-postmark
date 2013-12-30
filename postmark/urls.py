from django.conf.urls import url, patterns
from django.core.urlresolvers import reverse

urlpatterns = patterns("",
    url(r"^bounce/$", "postmark.views.bounce", name="postmark_bounce_hook"),
)
