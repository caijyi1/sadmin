#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from website.common.CommonPaginator import SelfPaginator
from UserManage.views.permission import PermissionVerify

from django.contrib import auth
from UserManage.models import GitMessage,AppMessage
from UserManage.forms import EditGitCommentForm
import sys,os,paramiko,datetime,re,time
from subprocess import *


@login_required
@PermissionVerify()
def ListAppMessage(request):
	mList = AppMessage.objects.order_by("-id").all()
	lst = SelfPaginator(request,mList,20)

	kwvars = {
		'lPage':lst,
		'request':request,
		}
	
	return render_to_response('UserManage/app.list.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def RollbackApp(request,ID):
	appname = AppMessage.objects.filter(id=ID)[0].appname
	version = AppMessage.objects.filter(id=ID)[0].version
	pid = AppMessage.objects.filter(id=ID)[0].pid
	md5sum = AppMessage.objects.filter(id=ID)[0].md5sum
	
	if 'gs_' in appname:
		try:
			check_call('fab  gamerollback:version=%s,app_name=%s'% (version,appname),shell=True)
		except CalledProcessError,e:
			kwvars = {
				'request':request,
				'error_message':str(e),
				}
			return  render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))
	elif 'dispatcher'== appname:
		try:
			check_call('fab disrollback:version=%s'% version,shell=True)

		except CalledProcessError, e:
			kwvars = {
				'request':request,
				'error_message':str(e),
			}
			return  render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))
	

	AppMessage.objects.create(appname=appname,version=version,pid=pid,md5sum=md5sum)

	return HttpResponseRedirect(reverse('listappurl'))
		

@login_required
@PermissionVerify()
def ReleaseApp(request,ID):
	appname = AppMessage.objects.filter(id=ID)[0].appname
	version = time.strftime("%Y%m%d%H%M")
	pid = AppMessage.objects.filter(id=ID)[0].pid
	pattern = re.compile(r'out: (.*)\s/opt/project')
	
	if 'dispatcher' not in appname:
		try:
			result=Popen('fab  gamerelease:app_name=%s,version=%s' % (appname,version),shell=True,stdout=PIPE).stdout.read()
			md5sum=pattern.search(result).group(1).strip()
		except AttributeError, e:
			kwvars = {
				'request':request,
				'error_message':u'游戏程序无法找到...',
				}
			return  render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))
	elif 'dispatcher'== appname:
		try:
			result=Popen('fab disrelease:version=%s' % version,shell=True,stdout=PIPE).stdout.read()
			md5sum=pattern.search(result).group(1).strip()
		except AttributeError, e:
			kwvars = {
				'request':request,
				'error_message':u'游戏程序无法找到...',
			}
			return  render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))
	

	AppMessage.objects.create(appname=appname,version=version,pid=pid,md5sum=md5sum)

	return HttpResponseRedirect(reverse('listappurl'))

@login_required
@PermissionVerify()
def StopApp(request,ID):
	appname = AppMessage.objects.filter(id=ID)[0].appname
	pattern = re.compile(r'out: root\s+(\d{1,6})\s')

	if 'dispatcher' not in appname:
		try:
			result=Popen('fab stopgame:app_name=%s'% (appname),shell=True,stdout=PIPE).stdout.read()
			pid = int(pattern.search(result).group(1))
		except AttributeError, e:
			AppMessage.objects.filter(id=ID).update(pid=0)
			return HttpResponseRedirect(reverse('listappurl'))

	elif 'dispatcher' == appname:
		try:
			result = Popen('fab stopdis',shell=True,stdout=PIPE).stdout.read()
			pid = pattern.search(result).group(1)
			print pid
		except AttributeError, e:
			AppMessage.objects.filter(id=ID).update(pid=0)
			return HttpResponseRedirect(reverse('listappurl'))

	kwvars = {
		'request':request,
		'error_message':u'请稍侯几分钟再重试...游戏服正在关闭',
	}
	return  render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def StartApp(request,ID):
	appname = AppMessage.objects.filter(id=ID)[0].appname
	pattern = re.compile(r'out: root\s+(\d{1,6})\s')

	if 'dispatcher' not in appname:
		try:
			result=Popen('fab startgame:app_name=%s'% (appname),shell=True,stdout=PIPE).stdout.read()
			pid = int(pattern.search(result).group(1))
		except AttributeError, e:
			kwvars = {
				'request':request,
				'error_message':u'启动游戏出现异常...',
				}
			return  render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))
	elif 'dispatcher' == appname:
		try:
			result=Popen('fab startdis',shell=True,stdout=PIPE).stdout.read()
			pid = pattern.search(result).group(1)
		except AttributeError, e:
			kwvars = {
				'request':request,
				'error_message':u'游戏启动出现异常...',
			}
			return  render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))
	
	AppMessage.objects.filter(id=ID).update(pid=pid)
	return HttpResponseRedirect(reverse('listappurl'))
