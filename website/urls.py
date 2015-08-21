from django.conf.urls import patterns, include, url

from django.conf import settings
from website.views import Home,About
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'website.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$',Home),
    url(r'^about/$',About),

    url(r'^accounts/',include('UserManage.urls' )),

    url(r'^captcha/','UserManage.views.captcha.index',name='captchaurl'),

	#web
	url(r'^web/list/$', 'UserManage.views.git.ListGitMessage', name='listweburl'),
    url(r'^web/commit/$', 'UserManage.views.git.CommitGit', name='commitweburl'),
    url(r'^web/rollback/(?P<ID>\d+)/$', 'UserManage.views.git.RollbackGit', name='rollbackweburl'),
    url(r'^web/release/(?P<ID>\d+)$', 'UserManage.views.git.ReleaseGit', name='releaseweburl'),
	
	#app
	url(r'^app/list/$', 'UserManage.views.app.ListAppMessage', name='listappurl'),
    url(r'^app/stopapp/(?P<ID>\d+)$', 'UserManage.views.app.StopApp', name='stopappurl'),
    url(r'^app/startapp/(?P<ID>\d+)$', 'UserManage.views.app.StartApp', name='startappurl'),
    url(r'^app/rollback/(?P<ID>\d+)/$', 'UserManage.views.app.RollbackApp', name='rollbackappurl'),
    url(r'^app/release/(?P<ID>\d+)$', 'UserManage.views.app.ReleaseApp', name='releaseappurl'),

    #static
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT,}),
)
