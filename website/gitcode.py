#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys,os
import paramiko
from subprocess import *
serverIP="116.93.96.23"

def gitrollback(request):
	#p=Popen("git log",shell=True,stdout=PIPE)
	#p1=Popen(["sed", "-n", "7p"],stdin=p.stdout,stdout=PIPE)
	#p2=Popen(["awk"],"{print $2}"),stdin=p1.stdout,stdout=PIPE)
	#version = p2.communicate()[0]
	version = request
	try:
		check_output('git reset --hard %s' % version,shell=True)
	except CalledProcessError, e:
		print "Error info:" + str(e)
		sys.exit(0)

	try:
		check_output('git push origin master -f',shell=True)
	except CalledProcessError, e:
		print "Push Failed: " + str(e)

	remotegitpull()

def gitcommit(request):
	
	info = request
	#CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
	GIT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
	os.chdir(GIT_DIR)
	print os.getcwd()

	try:
		check_call("git add .",shell=True)
		check_call('git commit -m %s' % info,shell=True)
		check_call('git push origin master',shell=True)
	except CalledProcessError, e:
		print "Push Faild: " + str(e) 
		sys.exit(0)

	remotegitpull()

def remotegitpull():
	hostname='116.93.96.23'
	username='root'
	paramiko.util.log_to_file='syslogin.log'
	webname='/mnt/sadmin.git'
	
	ssh=paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.load_system_host_keys()
	privatekey = os.path.expanduser('/root/.ssh/id_rsa')
	key = paramiko.RSAKey.from_private_key_file(privatekey,password='cai110110')

	ssh.connect(port=9831,hostname=hostname,username=username,pkey = key)
	stdin,stdout,stderr=ssh.exec_command('cd %s && git pull git://proxy.dapaile.com:9400/sadmin.git' % webname)
	print stdout.read()
	print stderr.read()

	ssh.close()

if __name__ == "__main__":
	if 'gitcommit' in sys.argv[1]:
		gitcommit(sys.argv[2])
	elif 'gitrollback' in sys.argv[1]:
		gitrollback(sys.argv[2])
