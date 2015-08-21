#!/usr/bin/env python
#-*- encoding:utf8 -*-

import time
from fabric.api import *
#from fabric.colors import *
#from fabric.context_managers import *
#from fabric.contrib.console import confirm

env.roledefs = {
		'gameserver' : ['116.93.71.68'],
		'dispatcher' : ['116.93.71.68','116.93.96.23'],
		#'robotclient' : ['116.93.96.23'],
		}

env.port = "9831"
env.user = "root"
env.password = 'cai110110'
env.apath = "/opt/project/p2p/code/game/cpp/bin/"
env.release_dir = 'releases'
#env.version = time.strftime("%Y%m%d%H%M")

@parallel
@roles('dispatcher')
def disrelease(version=''):
	#创建目录，并上传文件
	with settings(warn_only=True):
		with cd(env.apath + env.release_dir):
			run("mkdir %s" % version)
	env.full_path = env.apath + env.release_dir + "/" + version
	with settings(warn_only=True):
		result = put(env.apath + 'dispatch/dispatcher', env.full_path)
	if result.failed and not("put file failed, Continue[Y/N]?"):
		abort("Aborting file put task!")
	#发布，利用软链接
	with settings(warn_only=True):
		run("rm -f %s" % (env.apath + 'dispatch/dispatcher'))
		run("ln -s %s %s" % (env.apath+env.release_dir+"/"+version+'/dispatcher',env.apath+'dispatch/dispatcher'))
	with settings(hide('running','stderr'),warn_only=True):
		return run('md5sum %s'% (env.apath+'dispatch/dispatch'))

@parallel
@roles('gameserver')
def gamerelease(app_name='zjh',version=''):
	with settings(warn_only=True):
		with cd(env.apath + env.release_dir):
			run("mkdir %s" % version)
	env.full_path = env.apath + env.release_dir + "/" + version
	with settings(warn_only=True):
		result = put(env.apath + 'gameserver/' + app_name, env.full_path)
	if result.failed and not("put file failed, Continue[Y/N]?"):
		abort("Aborting file put task!")

	with settings(warn_only=True):
		run("rm -f %s" % (env.apath + 'gameserver/' + app_name + '/gs_' + app_name))
		#run("rm -f '/opt/project/p2p/code/game/cpp/bin/gameserver/zjh/gs_zjh'")
		run("ln -s %s %s" % (env.apath+env.release_dir+"/"+version+"/"app_name,env.apath+'gameserver/'+app_name +'/gs_'+app_name))
		#run("ln -s /opt/project/p2p/code/game/cpp/bin/releases/201508091541/gs_zjh,/opt/project/p2p/code/game/cpp/bin/gameserver/zjh/gs_zjh")
	with settings(hide('running','stderr'),warn_only=True):
		return run('md5sum %s'% (env.apath+'gameserver/'+app_name+'/gs_'+app_name))

#@parallel
#@roles('robotclient')
#def robrelease():
	#创建目录，并上传文件
#	with settings(warn_only=True):
#		with cd(env.apath + env.release_dir):
#			run("mkdir %s" % (env.version))
#	env.full_path = env.apath + env.release_dir + "/" + env.version
#	with settings(warn_only=True):
#		result = put(env.apath + 'robotclient/robotclient', env.full_path)
#	if result.failed and not("put file failed, Continue[Y/N]?"):
#		abort("Aborting file put task!")
	#发布，利用软链接
#	with settings(warn_only=True):
#		run("rm -f %s" % (env.apath + 'robot/robotclient'))
#		run("ln -s %s %s" % (env.apath+env.release_dir+"/"+env.version+'robotclient',env.apath+'robot/robotclient'))

@parallel
@roles('dispatcher')
def disrollback(version=''):
	env.pro_path = env.apath+'dispatch/dispatcher'
	with settings(warn_only=True):
		run("rm -f %s" %(env.pro_path))
		run("ln -s %s %s" % (env.apath+env.release_dir+"/"+version+'/dispatcher',env.pro_path))

@parallel
@roles('robotclient')
def robotrollback(version=''):
	env.pro_path = env.apath+'robot/robotclient'
	with settings(warn_only=True):
		run("rm -f %s" %(env.pro_path))
		run("ln -s %s %s" % (env.apath+env.release_dir+"/"+version+'/robotclient',env.pro_path))

@parallel
@roles('gameserver')
def gamerollback(version='',app_name='zjh'):
	env.pro_path = env.apath+'gameserver/'+app_name+'/gs_'+app_name
	with settings(warn_only=True):
		run("rm -f %s" %(env.pro_path))
		run("ln -s %s %s" % (env.apath+env.release_dir+"/"+version+"/"+app_name,env.pro_path))

@parallel
@roles('dispatcher')
def startdis():
	with settings(warn_only=True):
		with cd(env.apath+'dispatch'):
			run("nohup ./dispatcher --Ice.Config=/opt/project/p2p/code/game/cpp/config/dispatch/config.dispatch &")
	with settings(hide('running','stderr'),warn_only=True):
		run('ps aux |grep dispatcher |grep -v grep |awk "{print $2}"')

@parallel
@roles('dispatcher')
def stopdis():
	with settings(warn_only=True):
		run("kill `ps aux |grep dispatcher|grep -v grep |awk '{print $2}'`")
	with settings(hide('running','stderr'),warn_only=True):
		return run('ps aux |grep dispatcher|grep -v grep |awk "{print $2}"')

@parallel
@roles('gameserver')
def startgame(app_name='zjh'):
	with settings(warn_only=True):
		with cd(env.apath+'gameserver/'+app_name):
			run("nohup %s --Ice.Config=%s" % ("./gs_"+app_name,"/opt/project/p2p/code/game/cpp/config/gameserver/"+app_name+"/config."+app_name))
	with settings(hide('running','stderr'),warn_only=True):
		 run("ps aux|grep %s |grep -v grep |awk '{print $2}'"% (app_name))

@parallel
@roles('gameserver')
def stopgame(app_name='zjh'):
	with settings(warn_only=True):
		run("kill `ps aux |grep %s|grep -v grep |awk '{print $2}'`" % (app_name))
	with settings(hide('running','stderr'),warn_only=True):
		return run("ps aux |grep %s |grep -v grep |awk '{print $2}'"% (app_name))

#@parallel
#@roles('robotclient')
#def runtest(version='',name=''):
#	with settings(hide('running','stderr'),warn_only=True):
	#	with cd('/tmp/'+name+version):
	#		run("ls -l")
#		return run("ps aux |grep robot|grep 'conf.dz.client'|awk '{print $2}'")

