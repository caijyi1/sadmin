#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from website.common.CommonPaginator import SelfPaginator
from UserManage.views.permission import PermissionVerify

from django.contrib import auth
from UserManage.models import GitMessage 
from UserManage.forms import EditGitCommentForm
import sys,os,paramiko,datetime
from subprocess import *

@login_required
@PermissionVerify()
def ListGitMessage(request):
	mList = GitMessage.objects.order_by("-id").all()
	lst = SelfPaginator(request,mList,20)

	kwvars = {
		'lPage':lst,
		'request':request,
		}
	
	return render_to_response('UserManage/web.list.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def RollbackGit(request,ID):
	comhash = GitMessage.objects.filter(id=ID)[0].comhash

	try:
		check_output('git reset --hard %s' % comhash,shell=True)
		check_output('git push origin master',shell=True)
	except CalledProcessError, e:
		kwvars = {
			'request':request,
			'error_message':str(e),
			}
		return  render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))

	comhash = Popen('git log -1 --pretty=format:"%H"',shell=True,stdout=PIPE).stdout.read()
	comAuthor = Popen('git log -1 --pretty=format:"%cn"',shell=True,stdout=PIPE).stdout.read()
	comment = Popen('git log -1 --pretty=format:"%s"',shell=True,stdout=PIPE).stdout.read()
	Date = Popen('git log -1 --pretty=format:"%ct"',shell=True,stdout=PIPE).stdout.read()
	comDate = datetime.datetime.fromtimestamp(int(Date)).strftime('%Y-%m-%d %H:%M:%S')
	GitMessage.objects.create(comhash=comhash,comAuthor=comAuthor,comDate=comDate,comment=comment)

	return HttpResponseRedirect(reverse('listweburl'))
		

@login_required
@PermissionVerify()
def CommitGit(request):
	
	GIT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir,os.pardir))
	os.chdir(GIT_DIR)
	
	if request.method=='POST':
		form = EditGitCommentForm(request.POST)
		if form.is_valid():
			comment = form.cleaned_data['comment']
			try:
				check_call("git checkout master",shell=True)
				check_call("git add .",shell=True)
				check_call('git commit -m %s' % comment,shell=True)
				check_call('git push origin master',shell=True)
			except CalledProcessError, e:
				kwvars = {
					'request':request,
					'error_message':str(e),
					}
				return  render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))

			comhash = Popen('git log -1 --pretty=format:"%H"',shell=True,stdout=PIPE).stdout.read()
			comAuthor = Popen('git log -1 --pretty=format:"%cn"',shell=True,stdout=PIPE).stdout.read()
			Date = Popen('git log -1 --pretty=format:"%ct"',shell=True,stdout=PIPE).stdout.read()
			comDate = datetime.datetime.fromtimestamp(int(Date)).strftime('%Y-%m-%d %H:%M:%S')
			GitMessage.objects.create(comhash=comhash,comAuthor=comAuthor,comDate=comDate,comment=comment)
			return HttpResponseRedirect(reverse('listweburl'))
	else:
		form = EditGitCommentForm()
	kwvars = {
		'form':form,
		'request':request,
		}
	return render_to_response('UserManage/web.edit.html',kwvars,RequestContext(request))

def ReleaseGit(request,ID):

	comhash = GitMessage.objects.filter(id=ID)[0].comhash
	hostname='116.93.96.23'
	username='root'
	paramiko.util.log_to_file='syslogin.log'
	webname='/mnt/sadmin.git'
	
	try:
		ssh=paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.load_system_host_keys()
		privatekey = os.path.expanduser('/root/.ssh/id_rsa')
		key = paramiko.RSAKey.from_private_key_file(privatekey,password='cai110110')
		ssh.connect(port=9831,hostname=hostname,username=username,pkey = key)
		stdin,stdout,stderr=ssh.exec_command('cd %s && git pull git://proxy.dapaile.com:9400/sadmin.git && git reset --hard %s' %  (webname, comhash))
	except:
		ssh.close()
		return HttpResponse(u'连接远程服务器推送代码出错...')

	kwvars = {
		'error_message':stderr.read(),
		'success_message':stdout.read(),
		'requset':request,
		}
	print stdout.read()
	print stderr.read()
	ssh.close()
	return render_to_response('UserManage/release.message.html',kwvars,RequestContext(request))
