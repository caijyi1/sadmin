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


def RollbackGit(request,comhash):
	#p=Popen("git log",shell=True,stdout=PIPE)
	#p1=Popen(["sed", "-n", "7p"],stdin=p.stdout,stdout=PIPE)
	#p2=Popen(["awk"],"{print $2}"),stdin=p1.stdout,stdout=PIPE)
	#version = p2.communicate()[0]
	#comhash = comhash

	try:
		check_output('git reset --hard %s' % comhash,shell=True)
		check_output('git push origin master',shell=True)
	except CalledProcessError, e:
		print "Push Failed: " + str(e)

@login_required
@PermissionVerify()
def CommitGit(request):
	
	#CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
	GIT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir,os.pardir))
	os.chdir(GIT_DIR)
	
	if request.method=='POST':
		form = EditGitCommentForm(request.POST)
		if form.is_valid():
			comment = form.cleaned_data['comment']
			try:
				check_call("git add .",shell=True)
				check_call('git commit -m %s' % comment,shell=True)
				check_call('git push origin master',shell=True)
			except CalledProcessError, e:
				return  HttpResponse(str(e))
			comhash = Popen('git log -1 --pretty=format:"%H"',shell=True,stdout=PIPE).stdout.read()
			comAuthor = Popen('git log -1 --pretty=format:"%cn"',shell=True,stdout=PIPE).stdout.read()
			Date = Popen('git log -1 --pretty=format:"%ct"',shell=True,stdout=PIPE).stdout.read()
			comDate = datetime.datetime.fromtimestamp(int(Date)).strftime('%Y-%m-%d %H:%M:%S')

			print comment,comhash,comAuthor,comDate

			GitMessage.objects.create(comhash=comhash,comAuthor=comAuthor,comDate=comDate,comment=comment)
			return HttpResponseRedirect(reverse('listweburl'))
	else:
		form = EditGitCommentForm()
	kwvars = {
		'form':form,
		'request':request,
		}
	return render_to_response('UserManage/web.edit.html',kwvars,RequestContext(request))
	
	
	#return HttpResponse

def ReleaseGit(request):

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
		stdin,stdout,stderr=ssh.exec_command('cd %s && git pull git://proxy.dapaile.com:9400/sadmin.git' % webname)
	except:
		return HttpResponse(u'连接远程服务器推送代码出错...')

	#return HttpResponse
	print stdout.read()
	print stderr.read()

	ssh.close()
