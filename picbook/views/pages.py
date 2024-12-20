from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import redirect
import time
import json
#pip install Pillow
from PIL import Image
import os
 
def managelogin(request):
	if request.method == 'GET':
		context = {}
		return render(request, 'manage/login.html')
	elif request.method == 'POST':
		uname = request.POST.get("uname")
		pwd = request.POST.get("pwd")
		with connection.cursor() as cursor:
			cursor.execute("select id,privileges from webmaster where uname=%s and pwd=%s",(uname,pwd))
			result = cursor.fetchone()
			if result is not None:
				request.session['loginbean'] = {'uid':result[0],'uname':uname,'privileges':result[1]}
				return redirect('/manage/index/')
			else:
				return HttpResponse("<script>alert('用户名/密码错误');location.href='/manage/login';</script>")
		#return HttpResponse(uname)

def menu(request):
	sql = "select id,pid,mname,mlink from menu where pid=%s"
	with connection.cursor() as cursor:
		cursor.execute(sql,(0,))
		rs = cursor.fetchall()
		rs_arr = []
		i=0
		for item in rs:
			item = list(item)
			cursor.execute(sql,(item[0],))
			rs1 = cursor.fetchall()
			arr1 = []
			for item1 in rs1:
				item1 = list(item1)
				cursor.execute(sql,(item1[0],))
				rs2 = cursor.fetchall()
				item1.append(rs2)
				arr1.append(item1)
			item.append(arr1)
			rs_arr.append(item)
			i+=1
		print(rs_arr)
		booklist = getbooks()
	return render(request, 'manage/menu.html',{"menu":rs_arr,"booklist":booklist})

def addmenu(request):
	if request.method == 'POST':
		pid = request.POST.get("pid")
		mname = request.POST.get("mname")
		mlink = request.POST.get("mlink")
		with connection.cursor() as cursor:
			cursor.execute("insert into menu set pid=%s,mname=%s,mlink=%s",[pid,mname,mlink])
			connection.commit()
			return redirect('/manage/menu/')

def delmenu(request):
	mid = request.GET.get("mid")
	with connection.cursor() as cursor:
		cursor.execute("delete from menu where id=%s",[mid,])
		connection.commit()
		return redirect('/manage/menu/')

def bindmenu(request):
	sql = "select id,pid,mname,mlink from menu where pid=%s"
	with connection.cursor() as cursor:
		cursor.execute(sql,(0,))
		rs = cursor.fetchall()
		rs_arr = []
		for item in rs:
			item = list(item)
			cursor.execute(sql,(item[0],))
			rs1 = cursor.fetchall()
			item.append(rs1)
			rs_arr.append(item)
	bookid = request.GET.get("bookid")
	bookname = request.GET.get("bookname")
	sql1 = "select menuid from book2menu where pbid=%s"
	with connection.cursor() as cursor:
		cursor.execute(sql1,(bookid,))
		rs1 = cursor.fetchall()
	return render(request, 'manage/bindmenu.html',{'bookid':bookid,'bookname':bookname,'bmenu':rs_arr,'rs1':rs1})

def bindmenuexec(request):
	bookid = request.GET.get("bookid")
	menuidArr = request.GET.getlist("menuid")
	sql0="delete from book2menu where pbid=%s"
	with connection.cursor() as cursor:
		cursor.execute(sql0,(bookid,))
		for menuid in menuidArr:
			sql = "insert into book2menu set pbid=%s,menuid=%s"
			cursor.execute(sql,(bookid,menuid))
	connection.commit()
	bookname = request.GET.get("bookname")
	return HttpResponse("<script>alert('绑定成功');location.href='../bindmenu/?bookid=%s&bookname=%s';</script>"%(bookid,bookname))

#类别管理
def bcategory(request):
	sql = "select id,pid,bcname from bcategory where pid=%s"
	with connection.cursor() as cursor:
		cursor.execute(sql,(0,))
		rs = cursor.fetchall()
		rs_arr = []
		for item in rs:
			item = list(item)
			cursor.execute(sql,(item[0],))
			rs1 = cursor.fetchall()
			if len(rs1)>0:
				arr1 = []
				for item1 in rs1:
					arr1.append(list(item1))
				ii = 0
				for item11 in rs1:
					cursor.execute(sql,(item11[0],))
					rs2 = cursor.fetchall()
					if len(rs2)>0:
						arr2 = []
						for item2 in rs2:
							arr2.append(item2)
						arr1[ii].append(arr2)
					ii += 1
				item.append(arr1)
			rs_arr.append(item)
		booklist = getbooks()
	return render(request, 'manage/bcategory.html',{"bcategory":rs_arr,"booklist":booklist})

#添加类别
def addBcategory(request):
	if request.method == 'POST':
		pid = request.POST.get("pid")
		bcname = request.POST.get("bcname")
		with connection.cursor() as cursor:
			cursor.execute("insert into bcategory set pid=%s,bcname=%s",[pid,bcname])
			connection.commit()
			return redirect('/manage/bcategory/')

def delBcategory(request):
	bcid = request.GET.get("bcid")
	with connection.cursor() as cursor:
		cursor.execute("delete from bcategory where id=%s",[bcid,])
		cursor.execute("delete from bcategory where pid=%s",[bcid,])
		connection.commit()
		return redirect('/manage/bcategory/')

#绘本绑定类别
def bindcategory(request):
	sql = "select id,pid,bcname from bcategory where pid=%s"
	with connection.cursor() as cursor:
		cursor.execute(sql,(0,))
		rs = cursor.fetchall()
		rs_arr = []
		for item in rs:
			item = list(item)
			cursor.execute(sql,(item[0],))
			rs1 = cursor.fetchall()
			if len(rs1)>0:
				arr1 = []
				for item1 in rs1:
					arr1.append(list(item1))
				ii = 0
				for item11 in rs1:
					cursor.execute(sql,(item11[0],))
					rs2 = cursor.fetchall()
					if len(rs2)>0:
						arr2 = []
						for item2 in rs2:
							arr2.append(item2)
						arr1[ii].append(arr2)
					ii += 1
				item.append(arr1)
			rs_arr.append(item)
	bookid = request.GET.get("bookid")
	bookname = request.GET.get("bookname")
	sql1 = "select bcid from book2category where pbid=%s"
	with connection.cursor() as cursor:
		cursor.execute(sql1,(bookid,))
		rs1 = cursor.fetchall()
	
	return render(request, 'manage/bindcategory.html',{'bookid':bookid,'bookname':bookname,'bcategory':rs_arr,'rs1':rs1})

def bindcategoryexec(request):
	bookid = request.GET.get("bookid")
	bcidArr = request.GET.getlist("bcid")
	sql0="delete from book2category where pbid=%s"
	with connection.cursor() as cursor:
		cursor.execute(sql0,(bookid,))
		for bcid in bcidArr:
			sql = "insert into book2category set pbid=%s,bcid=%s"
			cursor.execute(sql,(bookid,bcid))
	connection.commit()
	bookname = request.GET.get("bookname")
	return HttpResponse("<script>alert('绑定成功');location.href='../bindcategory/?bookid=%s&bookname=%s';</script>"%(bookid,bookname))

def getbooks():
	rs = []
	with connection.cursor() as cursor:
		cursor.execute("select id,bookname from picbook where pid=0")
		result = cursor.fetchall()
		rs = [list(item) for item in result]
		for item in rs:
			cursor.execute("select id,bookname,gender,language,skincolor from picbook where pid=%s",[item[0],])
			rs1 = cursor.fetchall()
			item.append(rs1)
	return rs

def manageindex(request):
	#if request.session['loginbean'] is not None:
	if 'loginbean' in request.session:
		booklist = getbooks()
		#print(booklist)
		return render(request, 'manage/index.html',{'booklist':booklist})
		#return HttpResponse('主页')
	else:
		return HttpResponse("<script>alert('登录过期');location.href='../login/';</script>")

def addPage(request):
	bookid = request.GET.get("bookid")
	sql = "select id,pname from picbook where id=%s"
	rs,rs1 = None,[]
	with connection.cursor() as cursor:
		cursor.execute(sql,[bookid,])
		rs = cursor.fetchone()
		if rs is not None:
			sql1 = 'select id,pagenum,thumbnail from bookpage where pbid=%s order by pagenum'
			cursor.execute(sql1,[bookid,])
			rs1 = cursor.fetchall()
	return render(request, 'manage/addpage.html',{'picbookrs':rs,'bookpage':rs1})

def insertPage(request):
	if request.method == 'POST':
		pbid = request.POST.get("pbid")
		pagenum = request.POST.get("pagenum")
		pagepic = request.FILES.get("pagepic")
		if pagepic is not None:
			fpath = "media/bookpage/%s_%s_%s"%(pbid,pagenum,pagepic.name)
			f = open(fpath,mode='wb')
			for chunk in pagepic.chunks():
				f.write(chunk)
			f.close()
			# 生成缩略图
			thumbimg = Image.open(fpath)
			thumb_size = (128, 128)
			thumbimg.thumbnail(thumb_size)
			#thumb = thumbimg.resize(thumb_size, Image.ANTIALIAS)
			thumbimgPath = "media/bookpage/%s_%s_1_%s"%(pbid,pagenum,pagepic.name)
			thumbimg.save(thumbimgPath)
		sql = "insert into bookpage set pbid=%s,pagenum=%s,pagepic=%s,thumbnail=%s"
		param = [pbid,pagenum,fpath,thumbimgPath]
		with connection.cursor() as cursor:
			cursor.execute(sql,param)
			connection.commit()
		return redirect('/manage/addpage/?bookid=%s'%(pbid))

def delbookpage(request):
	if request.method == 'GET':
		pageid = request.GET.get("pageid")
		sql = "delete from bookpage where id=%s"
		with connection.cursor() as cursor:
			cursor.execute(sql,[pageid,])
			connection.commit()
		bookid = request.GET.get("bookid")
		return redirect('/manage/addpage/?bookid=%s'%(bookid))

def addbook(request):
	if request.method == 'POST':
		bookname = request.POST.get("bookname")
		pid = request.POST.get("pid")
		language = request.POST.get("language")
		gender = request.POST.get("gender")
		skincolor = request.POST.get("skincolor")
		showpic = request.FILES.get("showpic")
		fpath=''
		if showpic is not None:
			fpath = "media/showpic/%s_%s"%(bookname,showpic.name)
			f = open(fpath,mode='wb')
			for chunk in showpic.chunks():
				f.write(chunk)
			f.close()
		with connection.cursor() as cursor:
			sql = "insert into picbook (bookname,pid,gender,language,skincolor,showpic) values(%s,%s,%s,%s,%s,%s)"
			cursor.execute(sql,[bookname,pid,gender,language,skincolor,fpath])
			connection.commit()
			return redirect('/manage/index/')
			#return HttpResponse("创建绘本成功")


'''
def addpic(request):
	if request.method == 'GET':
		return HttpResponse("请正确提交")
	#print(request.POST)   # 请求体中的数据
	#print(request.FILES)  # 请求发过来的文件 {}
	pbid = request.POST.get("pbid")
	defflag = request.POST.get("defflag")		#是否默认页
	pagenum = request.POST.get("pagenum")
	ii = int(pagenum)				#0
	current_timestamp = pbid		#time.time()
	pagepic = request.FILES.get("pagepic")
	fpath,fbpath,thumbimgPath,leftpicpath,rightpicpath='','','','',''
	if pagepic is not None:
		fpath = "media/upload/%s_%d_%s"%(current_timestamp,ii,pagepic.name)
		f = open(fpath,mode='wb')
		for chunk in pagepic.chunks():
			f.write(chunk)
		f.close()
		# 生成缩略图
		thumbimg = Image.open(fpath)
		thumb_size = (128, 128)
		thumbimg.thumbnail(thumb_size)
		#thumb = thumbimg.resize(thumb_size, Image.ANTIALIAS)
		thumbimgPath = "media/upload/%s_%d_1_%s"%(current_timestamp,ii,pagepic.name)
		thumbimg.save(thumbimgPath)
	pflag = request.POST.get("pflag")		#0表无需换脸，1表需要换脸
	blankpic = request.FILES.get("blankpic")
	fbpath = ''
	if blankpic is not None:
		fbpath = "media/upload/%s_%d_blank_%s"%(current_timestamp,ii,pagepic.name)
		fb = open(fbpath,mode='wb')
		for chunk in blankpic.chunks():
			fb.write(chunk)
		f.close()
	nameflag = request.POST.get("nameflag")
	if nameflag=='1':		#含有动态名字
		sql_id = "SELECT LAST_INSERT_ID()"			#获取插入bookpics后的返回id
		nametype = request.POST.get("nametype")
		if nametype=='0':	#纯文字
			leftwords = request.POST.get("leftwords")
			rightwords = request.POST.get("rightwords")
			sql1 = "insert into bookpics set pbid=%s,pagenum=%s,pagepic=%s,pflag=%s,blankpic=%s,thumbnail=%s,nameflag=1,nametype=0,defflag=%s"
			param1 = [pbid,pagenum,fpath,pflag,fbpath,thumbimgPath,defflag]
			sql2 = "insert into setpic1 set picid=%s,leftwords=%s,rightwords=%s"
			with connection.cursor() as cursor:
				cursor.execute(sql1,param1)
				cursor.execute(sql_id)
				rs_id = cursor.fetchone()
				picid = rs_id[0]
				param2 = [picid,leftwords,rightwords]
				cursor.execute(sql2,param2)
				connection.commit()
		elif nametype=='1':		#左右图夹中间名字
			leftpic = request.FILES.get("leftpic")
			if leftpic is not None:
				ii += 1
				leftpicpath = "media/upload/%s_%d_%s"%(current_timestamp,ii,leftpic.name)
				f = open(leftpicpath,mode='wb')
				for chunk in leftpic.chunks():
					f.write(chunk)
				f.close()
			rightpic = request.FILES.get("rightpic")
			if rightpic is not None:
				ii += 1
				rightpicpath = "media/upload/%s_%d_%s"%(current_timestamp,ii,rightpic.name)
				f = open(rightpicpath,mode='wb')
				for chunk in rightpic.chunks():
					f.write(chunk)
				f.close()
			sql1 = "insert into bookpics set pbid=%s,pagenum=%s,pagepic=%s,pflag=%s,blankpic=%s,thumbnail=%s,nameflag=1,nametype=1"
			param1 = [pbid,pagenum,fpath,pflag,fbpath,thumbimgPath]
			sql2 = "insert into setpic2 set picid=%s,leftpic=%s,rightpic=%s"
			with connection.cursor() as cursor:
				cursor.execute(sql1,param1)
				cursor.execute(sql_id)
				rs_id = cursor.fetchone()
				picid = rs_id[0]
				param2 = [picid,leftpicpath,rightpicpath]
				cursor.execute(sql2,param2)
				connection.commit()
		elif nametype=='2':		#寄语
			leftpic = request.FILES.get("leftpic")
			if leftpic is not None:
				ii += 1
				leftpicpath = "media/upload/%s_%d_%s"%(current_timestamp,ii,leftpic.name)
				f = open(leftpicpath,mode='wb')
				for chunk in leftpic.chunks():
					f.write(chunk)
				f.close()
			rightpic = request.FILES.get("rightpic")
			if rightpic is not None:
				ii += 1
				rightpicpath = "media/upload/%s_%d_%s"%(current_timestamp,ii,rightpic.name)
				f = open(rightpicpath,mode='wb')
				for chunk in rightpic.chunks():
					f.write(chunk)
				f.close()
			sql1 = "insert into bookpics set pbid=%s,pagenum=%s,pagepic=%s,pflag=%s,blankpic=%s,thumbnail=%s,nameflag=1,nametype=2"
			param1 = [pbid,pagenum,fpath,pflag,fbpath,thumbimgPath]
			sql2 = "insert into setpic3 set picid=%s,leftpic=%s,rightpic=%s"
			with connection.cursor() as cursor:
				cursor.execute(sql1,param1)
				cursor.execute(sql_id)
				rs_id = cursor.fetchone()
				picid = rs_id[0]
				param2 = [picid,leftpicpath,rightpicpath]
				cursor.execute(sql2,param2)
				connection.commit()
		elif nametype=='3':		#多行文本
			sql1 = "insert into bookpics set pbid=%s,pagenum=%s,pagepic=%s,pflag=%s,blankpic=%s,thumbnail=%s,nameflag=1,nametype=3,defflag=%s"
			param1 = [pbid,pagenum,fpath,pflag,fbpath,thumbimgPath,defflag]
			sql2 = "insert into setpic4 set picid=%s"
			with connection.cursor() as cursor:
				cursor.execute(sql1,param1)
				cursor.execute(sql_id)
				rs_id = cursor.fetchone()
				picid = rs_id[0]
				param2 = [picid,]
				cursor.execute(sql2,param2)
				connection.commit()

	else:
		sql = "insert into bookpics set pbid=%s,pagenum=%s,pagepic=%s,pflag=%s,blankpic=%s,thumbnail=%s,nameflag=0"
		param = [pbid,pagenum,fpath,pflag,fbpath,thumbimgPath]
		with connection.cursor() as cursor:
			cursor.execute(sql,param)
			connection.commit()
	bookname = request.POST.get("bookname")
	return redirect('/manage/pbcontent/?id=%s&bookname=%s'%(pbid,bookname))
'''