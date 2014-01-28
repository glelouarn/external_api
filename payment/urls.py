from django.conf.urls import include
from django.conf.urls import patterns, url
from payment import views


urlpatterns = patterns('payment.views',

                       url(r'^pos/(?P<pos_key>[0-9]+)/charges$', views.ChargeCreate.as_view(), name='charge-create'),
                       url(r'^charges/(?P<pk>[0-9]+)$', views.ChargeDetail.as_view(), name='charge-detail'),

                       url(r'^users/$', views.UserList.as_view(), name='user-list'),
                       url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),

                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

                       url(r'^docs/', include('rest_framework_swagger.urls')),
)

