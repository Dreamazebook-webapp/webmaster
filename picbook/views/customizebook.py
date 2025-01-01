from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import redirect
import time
import json
#pip install Pillow
from PIL import Image
import os
from .pages import getbooks

def pbcontent(request):
	if request.method == 'GET':
		pbid = request.GET.get("pbid")
		bookname = request.GET.get("bookname")
		booklist = getbooks()
		with connection.cursor() as cursor:
			cursor.execute("select id,pagenum,pagepic72,pflag,nameflag,nametype from bookpics where pbid=%s order by pagenum",(pbid,))
			picrs = cursor.fetchall()
			if picrs is not None:
				return render(request, 'manage/pbcontent.html',{"booklist":booklist,"pbid":pbid,'bookname':bookname,'picrs':picrs})
		return render(request, 'manage/pbcontent.html',{"booklist":booklist,"pbid":pbid,'bookname':bookname})

#处理动态文字
def dynamicText(request,picid):
	nametype = request.POST.get("nametype")
	sql2 = None
	param2 = None
	if nametype=='0':	#单行全文字
		sql2 = "insert into setpic0 set picid=%s"
		param2 = [picid]
	elif nametype=='1':	#双行全文字
		sql2 = "insert into setpic1 set picid=%s"
		param2 = [picid]
	elif nametype=='2':	#多行全文字
		sql2 = "insert into setpic2 set picid=%s"
		param2 = [picid]
	elif nametype=='3':	#单弧文字
		sql2 = "insert into setpic3 set picid=%s"
		param2 = [picid]
	elif nametype=='4':	#双弧文字
		sql2 = "insert into setpic4 set picid=%s"
		param2 = [picid]
	return sql2,param2

#上传bookpic
def uploadBookpic(request):
	pbid = request.POST.get("pbid")
	pagenum = request.POST.get("pagenum")
	defflag = request.POST.get("defflag")		#是否默认页
	dflag=0
	if defflag=='1':							#如果不是默认页
		dflag=time.time()

	pagepic300 = request.FILES.get("pagepic300")
	pagepic300Path,pagepic72Path='',''		#300图路径和72图路径
	if pagepic300 is not None:
		pagepic300Path = "media/pic300/%s_%s_%d_%s"%(pbid,pagenum,dflag,pagepic300.name)
		f = open(pagepic300Path,mode='wb')
		for chunk in pagepic300.chunks():
			f.write(chunk)
		f.close()
		# 生成缩略图
		thumbimg = Image.open(pagepic300Path)
		thumb_size = (1151, 584)
		thumbimg.thumbnail(thumb_size)
		#thumb = thumbimg.resize(thumb_size, Image.ANTIALIAS)
		pagepic72Path = "media/pic72/%s_%s_%d_1_%s"%(pbid,pagenum,dflag,pagepic300.name)
		thumbimg.save(pagepic72Path)
	
	blankpic300 = request.FILES.get("blankpic300")
	blankpic300Path,blankpic72Path='',''		#300图路径和72图路径
	if blankpic300 is not None:
		blankpic300Path = "media/blank300/%s_%s_%d_%s"%(pbid,pagenum,dflag,blankpic300.name)
		f = open(blankpic300Path,mode='wb')
		for chunk in blankpic300.chunks():
			f.write(chunk)
		f.close()
		# 生成缩略图
		thumbimg = Image.open(blankpic300Path)
		thumb_size = (1151, 584)
		thumbimg.thumbnail(thumb_size)
		#thumb = thumbimg.resize(thumb_size, Image.ANTIALIAS)
		blankpic72Path = "media/blank72/%s_%s_%d_1_%s"%(pbid,pagenum,dflag,blankpic300.name)
		thumbimg.save(blankpic72Path)
	else:
		blankpic300Path,blankpic72Path=pagepic300Path,pagepic72Path
	print(pagepic300Path,pagepic72Path,blankpic300Path,blankpic72Path)
	return pagepic300Path,pagepic72Path,blankpic300Path,blankpic72Path

#上传blankpic
'''
def uploadBlankpic(request):
	pbid = request.POST.get("pbid")
	blankpic = request.FILES.get("blankpic")
	pagenum = request.POST.get("pagenum")
	dflag=time.time()
	fbpath = ''
	if blankpic is not None:
		fbpath = "media/upload/%s_%s_%d_blank_%s"%(pbid,pagenum,dflag,blankpic.name)
		fb = open(fbpath,mode='wb')
		for chunk in blankpic.chunks():
			fb.write(chunk)
		fb.close()
	return fbpath
'''

#插入绘本页
def addpic(request):
	if request.method == 'GET':
		return HttpResponse("请正确提交")
	#接收原图
	pbid = request.POST.get("pbid")
	pagenum = request.POST.get("pagenum")
	nametype = request.POST.get("nametype")
	defflag = request.POST.get("defflag")		#是否默认页
	
	pagepic300Path,pagepic72Path,blankpic300Path,blankpic72Path = uploadBookpic(request)		#图片上传
	nameflag = request.POST.get("nameflag")		#是否含有动态字
	pflag = request.POST.get("pflag")			#是否需要换脸
	sql,param = None,None
	if pflag=='0' and nameflag=='0':	#无需换脸也无需动态字,mergepic放入原图缩小版
		sql = "insert into bookpics set pbid=%s,pagenum=%s,pagepic300=%s,pagepic72=%s,blankpic300=%s,blankpic72=%s,pflag=0,nameflag=0,defflag=%s,mergepic=%s"
		param = [pbid,pagenum,pagepic300Path,pagepic72Path,blankpic300Path,blankpic72Path,defflag,pagepic72Path]
	else:
		sql = "insert into bookpics set pbid=%s,pagenum=%s,pagepic300=%s,pagepic72=%s,blankpic300=%s,blankpic72=%s,pflag=%s,nameflag=%s,nametype=%s,defflag=%s"
		param = [pbid,pagenum,pagepic300Path,pagepic72Path,blankpic300Path,blankpic72Path,pflag,nameflag,nametype,defflag]
	'''
	elif pflag=='1' and nameflag=='0':	#仅需换脸
		sql = "insert into bookpics set pbid=%s,pagenum=%s,pagepic300=%s,pagepic72=%s,blankpic300=%s,blankpic72=%s,pflag=1,nameflag=0,defflag=%s"
		param = [pbid,pagenum,pagepic300Path,pagepic72Path,blankpic300Path,blankpic72Path,defflag]
	elif nameflag=='1':	#仅需动态字,无论换不换脸(pflag是0还是1都不影响)
		sql = "insert into bookpics set pbid=%s,pagenum=%s,pagepic300=%s,pagepic72=%s,blankpic300=%s,blankpic72=%s,pflag=%s,nameflag=1,nametype=%s,defflag=%s"
		param = [pbid,pagenum,pagepic300Path,pagepic72Path,blankpic300Path,blankpic72Path,pflag,nametype,defflag]	#blankpic
	'''
	sql_id = "SELECT LAST_INSERT_ID()"			#获取插入bookpics后的返回id
	with connection.cursor() as cursor:
		cursor.execute(sql,param)
		cursor.execute(sql_id)
		rs_id = cursor.fetchone()
		picid = rs_id[0]
		#调用动态字方法
		sql2,param2 = dynamicText(request,picid)
		cursor.execute(sql2,param2)
		connection.commit()
	bookname = request.POST.get("bookname")
	return redirect('/manage/pbcontent/?pbid=%s&bookname=%s'%(pbid,bookname))


def delbookpic(request):
	if request.method == 'GET':
		picid = request.GET.get("picid")
		nameflag = request.GET.get("nameflag")
		nametype = request.GET.get("nametype")
		with connection.cursor() as cursor:
			if nameflag=='1':
				if nametype=="0":	#删setpic0
					sql1 = "delete from setpic0 where picid=%s"
					cursor.execute(sql1,(picid,))
				elif nametype=="1":	#删setpic1
					sql1 = "delete from setpic1 where picid=%s"
					rs1 = cursor.execute(sql1,(picid,))
				elif nametype=="2":	#删setpic2
					sql1 = "delete from setpic2 where picid=%s"
					rs1 = cursor.execute(sql1,(picid,))
				elif nametype=="3":	#删setpic3
					sql1 = "delete from setpic3 where picid=%s"
					rs1 = cursor.execute(sql1,(picid,))
				elif nametype=="4":	#删setpic4
					sql1 = "delete from setpic4 where picid=%s"
					rs1 = cursor.execute(sql1,(picid,))
			sql = "delete from bookpics where id=%s"
			rs = cursor.execute(sql,(picid,))
			connection.commit()
		pbid = request.GET.get("pbid")
		bookname = request.GET.get("bookname")
		return redirect('/manage/pbcontent/?pbid=%s&bookname=%s'%(pbid,bookname))

def wordpos(request):
	if request.method == 'GET':
		picid = request.GET.get("picid")
		pbid = request.GET.get("pbid")
		bookname = request.GET.get("bookname")
		vflag = request.GET.get("vflag")
		#mergeImgPath = request.GET.get("mergeImgPath")
		#booklist = getbooks()
		sql1 = "select pagepic300,pagepic72,blankpic300,blankpic72,nameflag,nametype from bookpics where id=%s"
		with connection.cursor() as cursor:
			cursor.execute(sql1,(picid,))
			picrs1 = cursor.fetchone()
			if picrs1 is not None:
				nameflag = picrs1[4]
				nametype = picrs1[5]
				if nameflag==1:
					if nametype==0:	#单行文本
						sql0 = "select leftwords,rightwords,cflag,xpos300,ypos300,xpos72,ypos72,imgfont,fontsize,fontcolor,sname from setpic0 where picid=%s"
						cursor.execute(sql0,(picid,))
						picrs2 = cursor.fetchone()
						return render(request, 'manage/setpic0.html',{'picid':picid,'picrs1':picrs1,'picrs2':picrs2,"pbid":pbid,'bookname':bookname,'vflag':vflag})
					elif nametype==1:	#两行文本
						sql1 = "select leftwords1,rightwords1,cflag1,xpos1,ypos1,imgfont1,fontsize1,fontcolor1,leftwords2,rightwords2,cflag2,xpos2,ypos2,imgfont2,fontsize2,fontcolor2,text1,text2 from setpic1 where picid=%s"
						cursor.execute(sql1,(picid,))
						picrs2 = cursor.fetchone()
						#mergeImgPath = picrs2[9]
						return render(request, 'manage/setpic1.html',{'picid':picid,'picrs1':picrs1,'picrs2':picrs2,"pbid":pbid,'bookname':bookname,'vflag':vflag})
					elif nametype==2:	#多行文本
						sql2 = "select cflag,xpos,ypos,imgfont,fontsize,fontcolor,scontent from setpic2 where picid=%s"
						cursor.execute(sql2,(picid,))
						picrs2 = cursor.fetchone()
						scontent = picrs2[6].split('\r\n')
						return render(request, 'manage/setpic2.html',{'picid':picid,'picrs1':picrs1,'picrs2':picrs2,'scontent':scontent,"pbid":pbid,'bookname':bookname,'vflag':vflag})
					elif nametype==3:	#单弧文字
						sql1 = "select lrflag,sentence,cposx,cposy,rr,startangle,charangle,imgfont,fontsize,fontcolor,mergepic,sname from setpic3 where picid=%s"
						cursor.execute(sql1,(picid,))
						picrs2 = cursor.fetchone()
						if picrs2==None:
							picrs2=[None,None,None,None,None,None,None,None,None,None,None,None]
						return render(request, 'manage/setpic3.html',{'picid':picid,'picrs1':picrs1,'picrs2':picrs2,"pbid":pbid,'bookname':bookname,'vflag':vflag})
					elif nametype==4:	#双弧文字
						sql1 = "select lrflag,leftwords,cposx1,cposy1,r1,rightwords,cposx2,cposy2,r2,charangle,imgfont,fontsize,fontcolor,mergepic,sname from setpic4 where picid=%s"
						cursor.execute(sql1,(picid,))
						picrs2 = cursor.fetchone()
						if picrs2==None:
							picrs2=[None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]
						return render(request, 'manage/setpic4.html',{'picid':picid,'picrs1':picrs1,'picrs2':picrs2,"pbid":pbid,'bookname':bookname,'vflag':vflag})
		return render(request, 'manage/pbcontent.html',{"pbid":pbid,'bookname':bookname})


import cv2
import numpy as np

# 遍历像素法
def overlay_pixel(img, img_over, img_over_x, img_over_y):
	"""
	粘贴图像
	:param img: 背景图像
	:param img_over: 前景图像
	:param img_over_x: 前景图像在背景图像上的横坐标
	:param img_over_y: 前景图像在背景图像上的纵坐标
	:return: 粘贴“前景图像”后的“背景图像”
	"""
	img_h, img_w, img_p = img.shape # 背景图像宽、高、通道数
	img_over_h, img_over_w, img_over_c = img_over.shape # 前景图像高、宽、通道数
	img_over = cv2.cvtColor(img_over, cv2.COLOR_BGR2BGRA) # 转换成4通道图像
	for w in range(0, img_over_w): # 遍历列
		for h in range(0, img_over_h): # 遍历行
			#if img_over[h, w, 3] != 0:	# and img_over[h, w, 3] != 255: # 如果不是全透明的像素
			if img_over[h, w, 0] != 0:
				for c in range(0, 3): # 遍历三个通道
					x = img_over_x + w # 覆盖像素的横坐标
					y = img_over_y + h # 覆盖像素的纵坐标
					if x >= img_w or y >= img_h: # 如果坐标超出最大宽高
						break # 不做操作
					img[y, x, c] = img_over[h, w, c] # 覆盖像素
	return img # 粘贴“前景图像”后的“背景图像”

# 掩模覆盖法
def overlay_mask(background_img, prospect_img, img_over_x, img_over_y):
	back_r, back_c, _ = background_img.shape # 背景图像行数、列数
	if img_over_x > back_c or img_over_x < 0 or img_over_y > back_r or img_over_y < 0:
		print("前景图不在背景图范围内")
		return background_img
	pro_r, pro_c, _ = prospect_img.shape # 前景图像行数、列数
	if img_over_x + pro_c > back_c: # 如果水平方向展示不全
		pro_c = back_c - img_over_x # 截取前景图的列数
		prospect_img = prospect_img[:, 0:pro_c, :] # 截取前景图
	if img_over_y + pro_r > back_r: # 如果垂直方向展示不全
		pro_r = back_r - img_over_y # 截取前景图的行数
		prospect_img = prospect_img[0:pro_r, :, :] # 截取前景图

	prospect_img = cv2.cvtColor(prospect_img, cv2.COLOR_BGR2BGRA) # 前景图转为4通道图像
	prospect_tmp = np.zeros((back_r, back_c, 4), np.uint8) # 与背景图像等大的临时前景图层

	# 前景图像放到前景图层里
	prospect_tmp[img_over_y:img_over_y + pro_r,
	img_over_x: img_over_x + pro_c, :] = prospect_img

	_, binary = cv2.threshold(prospect_img, 254, 255, cv2.THRESH_BINARY) # 前景图阈值处理
	prospect_mask = np.zeros((pro_r, pro_c, 1), np.uint8) # 单通道前景图像掩模
	prospect_mask[:, :, 0] = binary[:, :, 3] # 不透明像素的值作为掩模的值

	mask = np.zeros((back_r, back_c, 1), np.uint8)
	mask[img_over_y:img_over_y + prospect_mask.shape[0],
	img_over_x: img_over_x + prospect_mask.shape[1]] = prospect_mask

	mask_not = cv2.bitwise_not(mask)

	prospect_tmp = cv2.bitwise_and(prospect_tmp, prospect_tmp, mask=mask)
	background_img = cv2.bitwise_and(background_img, background_img, mask=mask_not)
	prospect_tmp = cv2.cvtColor(prospect_tmp, cv2.COLOR_BGRA2BGR) # 前景图层转为三通道图像
	return prospect_tmp + background_img # 前景图层与背景图像相加合并

#----单行纯文本------------------------
def mergepic0(request):
	if request.method == 'POST':
		pbid = request.POST.get("pbid")
		picid = request.POST.get("picid")
		blankpic = request.POST.get("blankpic")
		vflag = request.POST.get("vflag")
		leftwords = request.POST.get("leftwords")
		rightwords = request.POST.get("rightwords")
		cflag = request.POST.get("cflag")
		vflag = request.POST.get("vflag")		#0表300，1表72
		xpos300 = request.POST.get("xpos300")
		ypos300 = request.POST.get("ypos300")
		xpos72 = request.POST.get("xpos72")
		ypos72 = request.POST.get("ypos72")
		#letterwidth = int(request.POST.get("letterwidth"))
		imgfont = request.POST.get("imgfont")
		fontsize = request.POST.get("fontsize")
		fontcolor = request.POST.get("fontcolor")
		sname = request.POST.get("sname")
		bookname = request.POST.get("bookname")
		#入库
		if vflag=='0':
			sql = "update setpic0 set leftwords=%s,rightwords=%s,cflag=%s,xpos300=%s,ypos300=%s,imgfont=%s,fontsize=%s,fontcolor=%s,sname=%s where picid=%s"
			param = (leftwords,rightwords,cflag,xpos300,ypos300,imgfont,fontsize,fontcolor,sname,picid)
		else:
			sql = "update setpic0 set leftwords=%s,rightwords=%s,cflag=%s,xpos72=%s,ypos72=%s,imgfont=%s,fontsize=%s,fontcolor=%s,sname=%s where picid=%s"
			param = (leftwords,rightwords,cflag,xpos72,ypos72,imgfont,fontsize,fontcolor,sname,picid)
		with connection.cursor() as cursor:
			cursor.execute(sql,param)
			connection.commit()

		return redirect('/manage/wordpos/?picid=%s&id=%s&bookname=%s&vflag=%s'%(picid,pbid,bookname,vflag))

'''
def mergepic0(request):
	if request.method == 'POST':
		pbid = request.POST.get("pbid")
		picid = request.POST.get("picid")
		leftwords = request.POST.get("leftwords")
		rightwords = request.POST.get("rightwords")
		cflag = request.POST.get("cflag")
		xpos = request.POST.get("xpos")
		ypos = int(request.POST.get("ypos"))	#纵向位置
		letterwidth = int(request.POST.get("letterwidth"))
		imgfont = request.POST.get("imgfont")
		fontsize = int(request.POST.get("fontsize"))
		fontcolor = request.POST.get("fontcolor")
		blankpic = request.POST.get("blankpic")
		sname = request.POST.get("sname")
		bookname = request.POST.get("bookname")
		#----------绘制文字-----------
		fcolorList = fontcolor.split(',')
		fcolorList = [int(elem) for elem in fcolorList]
		font_color = tuple(fcolorList)
		img0 = cv2.imread(blankpic)
		sentence = leftwords+" "+sname+" "+rightwords
		c_flag = int(cflag)
		x_pos = int(xpos)
		if c_flag==1:			#如果居中
			s_len = len(sentence)*int(letterwidth)
			x_pos = int(xpos)-s_len/2
		ypos = int(ypos)
		pos = (x_pos, ypos)
		fontsize = int(fontsize)
		imgPIL = Image.fromarray(cv2.cvtColor(img0, cv2.COLOR_BGR2RGB))
		drawPIL = ImageDraw.Draw(imgPIL)
		fontText = ImageFont.truetype("media/font/%s"%(imgfont), fontsize, encoding="utf-8")
		#print(sentence)
		drawPIL.text(pos, sentence, font_color, font=fontText)
		imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
		mergeImgPath = 'media/newimg/%s_%s.png'%(pbid,picid)
		imgsrc=cv2.imwrite(mergeImgPath,imgPutText)
		mergeImgPath = "/%s"%(mergeImgPath)
		sql = "update setpic0 set leftwords=%s,rightwords=%s,cflag=%s,xpos=%s,ypos=%s,letterwidth=%s,imgfont=%s,fontsize=%s,fontcolor=%s,mergepic=%s,sname=%s where picid=%s"
		param = (leftwords,rightwords,cflag,xpos,ypos,letterwidth,imgfont,fontsize,fontcolor,mergeImgPath,sname,picid)
		with connection.cursor() as cursor:
			cursor.execute(sql,param)
			connection.commit()
	return redirect('/manage/wordpos/?picid=%s&id=%s&bookname=%s'%(picid,pbid,bookname))
'''

from PIL import Image, ImageDraw, ImageFont
#---双行纯文本---------------
def mergepic1(request):
	if request.method == 'POST':
		pbid = request.POST.get("pbid")
		picid = request.POST.get("picid")
		bookname = request.POST.get("bookname")
		blankpic = request.POST.get("blankpic")
		vflag = request.POST.get("vflag")
		#------------------------------------------
		leftwords1 = request.POST.get("leftwords1")
		rightwords1 = request.POST.get("rightwords1")
		cflag1 = request.POST.get("cflag1")
		xpos1 = request.POST.get("xpos1")
		ypos1 = request.POST.get("ypos1")	#纵向位置
		imgfont1 = request.POST.get("imgfont1")
		fontsize1 = request.POST.get("fontsize1")
		fontcolor1 = request.POST.get("fontcolor1")
		text1 = request.POST.get("text1")
		#----------------------------------------
		leftwords2 = request.POST.get("leftwords2")
		rightwords2 = request.POST.get("rightwords2")
		cflag2 = request.POST.get("cflag2")
		xpos2 = request.POST.get("xpos2")
		ypos2 = request.POST.get("ypos2")	#纵向位置
		imgfont2 = request.POST.get("imgfont2")
		fontsize2 = int(request.POST.get("fontsize2"))
		fontcolor2 = request.POST.get("fontcolor2")
		text2 = request.POST.get("text2")
		sql = "update setpic1 set leftwords1=%s,rightwords1=%s,cflag1=%s,xpos1=%s,ypos1=%s,imgfont1=%s,fontsize1=%s,fontcolor1=%s,leftwords2=%s,rightwords2=%s,cflag2=%s,xpos2=%s,ypos2=%s,imgfont2=%s,fontsize2=%s,fontcolor2=%s,text1=%s,text2=%s where picid=%s"
		param = (leftwords1,rightwords1,cflag1,xpos1,ypos1,imgfont1,fontsize1,fontcolor1,leftwords2,rightwords2,cflag2,xpos2,ypos2,imgfont2,fontsize2,fontcolor2,text1,text2,picid)
		with connection.cursor() as cursor:
			cursor.execute(sql,param)
			connection.commit()
	return redirect('/manage/wordpos/?picid=%s&id=%s&bookname=%s&vflag=%s'%(picid,pbid,bookname,vflag))
'''
def mergepic1(request):
	if request.method == 'POST':
		pbid = request.POST.get("pbid")
		picid = request.POST.get("picid")
		bookname = request.POST.get("bookname")
		blankpic = request.POST.get("blankpic")
		#------------------------------------------
		leftwords1 = request.POST.get("leftwords1")
		rightwords1 = request.POST.get("rightwords1")
		cflag1 = request.POST.get("cflag1")
		xpos1 = request.POST.get("xpos1")
		ypos1 = int(request.POST.get("ypos1"))	#纵向位置
		letterwidth1 = int(request.POST.get("letterwidth1"))
		imgfont1 = request.POST.get("imgfont1")
		fontsize1 = int(request.POST.get("fontsize1"))
		fontcolor1 = request.POST.get("fontcolor1")
		blankpic1 = request.POST.get("blankpic1")
		text1 = request.POST.get("text1")
		#----------------------------------------
		leftwords2 = request.POST.get("leftwords2")
		rightwords2 = request.POST.get("rightwords2")
		cflag2 = request.POST.get("cflag2")
		xpos2 = request.POST.get("xpos2")
		ypos2 = int(request.POST.get("ypos2"))	#纵向位置
		letterwidth2 = int(request.POST.get("letterwidth2"))
		imgfont2 = request.POST.get("imgfont2")
		fontsize2 = int(request.POST.get("fontsize2"))
		fontcolor2 = request.POST.get("fontcolor2")
		blankpic2 = request.POST.get("blankpic2")
		text2 = request.POST.get("text2")
		#----------绘制文字1-----------
		fcolorList1 = fontcolor1.split(',')
		fcolorList1 = [int(elem) for elem in fcolorList1]
		font_color1 = tuple(fcolorList1)
		sentence1 = leftwords1+" "+text1+" "+rightwords1
		c_flag1 = int(cflag1)
		x_pos1 = int(xpos1)
		if c_flag1==1:			#如果居中
			s_len1 = len(sentence1)*int(letterwidth1)
			x_pos1 = int(xpos1)-s_len1/2
		ypos1 = int(ypos1)
		pos1 = (x_pos1, ypos1)
		fontsize1 = int(fontsize1)
		fontText1 = ImageFont.truetype("media/font/%s"%(imgfont1), fontsize1, encoding="utf-8")
		#-----------------------------------
		fcolorList2 = fontcolor1.split(',')
		fcolorList2 = [int(elem) for elem in fcolorList2]
		font_color2 = tuple(fcolorList2)
		sentence2 = leftwords2+" "+text2+" "+rightwords2
		c_flag2 = int(cflag2)
		x_pos2 = int(xpos2)
		if c_flag2==1:			#如果居中
			s_len2 = len(sentence2)*int(letterwidth2)
			x_pos2 = int(xpos2)-s_len2/2
		ypos2 = int(ypos2)
		pos2 = (x_pos2, ypos2)
		fontsize2 = int(fontsize2)
		fontText2 = ImageFont.truetype("media/font/%s"%(imgfont2), fontsize2, encoding="utf-8")
		#-----------------------------------
		img0 = cv2.imread(blankpic)
		imgPIL = Image.fromarray(cv2.cvtColor(img0, cv2.COLOR_BGR2RGB))
		drawPIL = ImageDraw.Draw(imgPIL)
		drawPIL.text(pos1, sentence1, font_color1, font=fontText1)
		drawPIL.text(pos2, sentence2, font_color2, font=fontText2)
		imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
		mergeImgPath = 'media/newimg/%s_%s.png'%(pbid,picid)
		imgsrc=cv2.imwrite(mergeImgPath,imgPutText)
		mergeImgPath = "/%s"%(mergeImgPath)
		sql = "update setpic1 set leftwords1=%s,rightwords1=%s,cflag1=%s,xpos1=%s,ypos1=%s,letterwidth1=%s,imgfont1=%s,fontsize1=%s,fontcolor1=%s,leftwords2=%s,rightwords2=%s,cflag2=%s,xpos2=%s,ypos2=%s,letterwidth2=%s,imgfont2=%s,fontsize2=%s,fontcolor2=%s,mergepic=%s,text1=%s,text2=%s where picid=%s"
		param = (leftwords1,rightwords1,cflag1,xpos1,ypos1,letterwidth1,imgfont1,fontsize1,fontcolor1,leftwords2,rightwords2,cflag2,xpos2,ypos2,letterwidth2,imgfont2,fontsize2,fontcolor2,mergeImgPath,text1,text2,picid)
		with connection.cursor() as cursor:
			cursor.execute(sql,param)
			connection.commit()
	return redirect('/manage/wordpos/?picid=%s&id=%s&bookname=%s'%(picid,pbid,bookname))
'''



#---多行文本------------------
def mergepic2(request):
	if request.method == 'POST':
		pbid = request.POST.get("pbid")
		picid = request.POST.get("picid")
		bookname = request.POST.get("bookname")
		blankpic = request.POST.get("blankpic")
		vflag = request.POST.get("vflag")
		cflag = request.POST.get("cflag")
		xpos = request.POST.get("xpos")
		ypos = int(request.POST.get("ypos"))	#纵向位置
		letterwidth = 2	#int(request.POST.get("letterwidth"))
		imgfont = request.POST.get("imgfont")
		fontsize = int(request.POST.get("fontsize"))
		fontcolor = request.POST.get("fontcolor")
		scontent = request.POST.get("scontent")
		
		sql = "update setpic2 set cflag=%s,xpos=%s,ypos=%s,imgfont=%s,fontsize=%s,fontcolor=%s,scontent=%s where picid=%s"
		param = (cflag,xpos,ypos,imgfont,fontsize,fontcolor,scontent,picid)
		with connection.cursor() as cursor:
			cursor.execute(sql,param)
			connection.commit()
	return redirect('/manage/wordpos/?picid=%s&id=%s&bookname=%s&vflag=%s'%(picid,pbid,bookname,vflag))
'''
def mergepic2(request):
	if request.method == 'POST':
		pbid = request.POST.get("pbid")
		picid = request.POST.get("picid")
		bookname = request.POST.get("bookname")
		blankpic = request.POST.get("blankpic")
		
		cflag = request.POST.get("cflag")
		xpos = request.POST.get("xpos")
		ypos = int(request.POST.get("ypos"))	#纵向位置
		letterwidth = int(request.POST.get("letterwidth"))
		imgfont = request.POST.get("imgfont")
		fontsize = int(request.POST.get("fontsize"))
		fontcolor = request.POST.get("fontcolor")
		scontent = request.POST.get("scontent")
		ncontent = scontent
		contentArr = scontent.split('\r\n')
		firstLine = contentArr[0]
		for i in range(1,6):
			if len(contentArr[i].strip())>0:
				secondLine = contentArr[i]
				break
		c_flag = int(cflag)
		x_pos = int(xpos)
		if c_flag==1:			#如果居中
			lw = int(letterwidth)
			s_len1 = len(firstLine)
			s_len2 = len(secondLine)
			spnum = int(s_len2-s_len1)
			sp = []
			for i in range(spnum):
				sp.append('\s')
			spStr = ''.join(sp)
			contentArr[0]="%s%s"%(spStr,firstLine)
			ncontent = '\n'.join(contentArr)
		ypos = int(ypos)
		pos = (x_pos, ypos)
		#----------绘制文字-----------
		fcolorList = fontcolor.split(',')
		fcolorList = [int(elem) for elem in fcolorList]
		font_color = tuple(fcolorList)
		img0 = cv2.imread(blankpic)
		fontsize = int(fontsize)
		imgPIL = Image.fromarray(cv2.cvtColor(img0, cv2.COLOR_BGR2RGB))
		drawPIL = ImageDraw.Draw(imgPIL)
		fontText = ImageFont.truetype("media/font/%s"%(imgfont), fontsize, encoding="utf-8")
		#print(sentence)
		drawPIL.text(pos, ncontent, font_color, font=fontText)
		imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
		mergeImgPath = 'media/newimg/%s_%s.png'%(pbid,picid)
		imgsrc=cv2.imwrite(mergeImgPath,imgPutText)
		mergeImgPath = "/%s"%(mergeImgPath)
		sql = "update setpic2 set cflag=%s,xpos=%s,ypos=%s,letterwidth=%s,imgfont=%s,fontsize=%s,fontcolor=%s,mergepic=%s,scontent=%s where picid=%s"
		param = (cflag,xpos,ypos,letterwidth,imgfont,fontsize,fontcolor,mergeImgPath,scontent,picid)
		with connection.cursor() as cursor:
			cursor.execute(sql,param)
			connection.commit()
	return redirect('/manage/wordpos/?picid=%s&id=%s&bookname=%s'%(picid,pbid,bookname))
'''

#单弧文本
def mergepic3(request):
	if request.method == 'POST':
		pbid = request.POST.get("pbid")
		picid = request.POST.get("picid")
		bookname = request.POST.get("bookname")
		blankpic = request.POST.get("blankpic")

		lrflag = int(request.POST.get("lrflag"))	#0在句前,1在句后
		sentence = request.POST.get("sentence")
		cposx = int(request.POST.get("cposx"))
		cposy = int(request.POST.get("cposy"))
		rr = int(request.POST.get("rr"))
		startangle = int(request.POST.get("startangle"))
		charangle = int(request.POST.get("charangle"))
		
		imgfont = request.POST.get("imgfont")
		fontsize = request.POST.get("fontsize")
		fontcolor = request.POST.get("fontcolor")
		sname = request.POST.get("sname")
		if lrflag==0:
			sentence_sname = sname+' '+sentence
		else:
			sentence_sname = sentence+' '+sname
		
		fcolorList = fontcolor.split(',')
		fcolorList = [int(elem) for elem in fcolorList]
		font_color = tuple(fcolorList)
		
		img0 = cv2.imread(blankpic)
		drawPIL = ImageDraw.Draw(img0)
		font_size = int(fontsize)
		font = ImageFont.truetype("media/font/%s"%(imgfont), font_size)
		#imgPIL = Image.fromarray(cv2.cvtColor(img0, cv2.COLOR_BGR2RGB))
		
		# 绘制前半段文字（圆心在下方）
		for i, char in enumerate(sentence_sname):
			# 计算每个字符的位置
			angle = startangle + i * charangle  # 每个字符间隔约2度
			x = cposx + rr * math.cos(math.radians(angle))
			y = cposy + rr * math.sin(math.radians(angle))
			'''
			# 计算字符旋转角度，使字符沿路径对齐
			next_angle = angle + 1  # 下一个字符的位置
			next_x = cposx + radius1 * math.cos(math.radians(next_angle))
			next_y = cposy + radius1 * math.sin(math.radians(next_angle))
			char_angle = math.degrees(math.atan2(next_y - y, next_x - x))
			'''
			

			# 创建一个临时图层来绘制旋转的字符
			char_img = Image.new('RGBA', img0.size, (255, 255, 255, 0))
			char_draw = ImageDraw.Draw(char_img)
			char_draw.text((x, y), char, font=font, fill="black")
			rotated_char_img = char_img.rotate(-char_angle, center=(x, y))
			img0 = Image.alpha_composite(img0.convert('RGBA'), rotated_char_img)
		#----------绘制名字文字----------------------------------------
		imgPIL = Image.fromarray(cv2.cvtColor(img0, cv2.COLOR_BGR2RGB))
		fontText2 = ImageFont.truetype("media/font/%s"%(imgfont2), msgwordsize, encoding="utf-8")
		#---------左上角位置-----------------
		pos = (msgx, msgy)
		drawPIL = ImageDraw.Draw(imgPIL)
		
		content = scontent.replace(' ','   ')
		drawPIL.text(pos, content, fontColor, font=fontText2)
		imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
		
		#current_timestamp = time.time()
		#temptime = int(current_timestamp)
		rootPath = os.getcwd()
		mergeImgPath = '/media/newimg/%s_%s.png'%(pbid,picid)
		mergePath = '%s%s'%(rootPath,mergeImgPath)

		rs_write = cv2.imwrite(mergePath,imgPutText)
		
		sql = "update setpic4 set msgx=%s,msgy=%s,imgfont2=%s,msgwordsize=%s,fontcolor=%s,mergepic=%s,scontent=%s where picid=%s"
		param = (msgx,msgy,imgfont2,msgwordsize,fontcolor,mergeImgPath,scontent,picid)
		with connection.cursor() as cursor:
			rs=cursor.execute(sql,param)
			connection.commit()
		bookname = request.POST.get("bookname")
	return redirect('/manage/wordpos/?picid=%s&id=%s&bookname=%s'%(picid,pbid,bookname))

#双弧文字
def mergepic4(request):
	if request.method == 'POST':
		pbid = request.POST.get("pbid")
		picid = request.POST.get("picid")
		bookname = request.POST.get("bookname")
		blankpic = request.POST.get("blankpic")

		lrflag = int(request.POST.get("lrflag"))	
		leftwords = request.POST.get("leftwords")			
		cposx1 = int(request.POST.get("cposx1"))
		cposy1 = int(request.POST.get("cposy1"))
		r1 = int(request.POST.get("r1"))
		rightwords = request.POST.get("rightwords")
		cposx2 = request.POST.get("cposx2")
		cposy2 = request.POST.get("cposy2")
		r2 = request.POST.get("r2")
		charangle = request.POST.get("charangle")
		imgfont = request.POST.get("imgfont")
		fontsize = request.POST.get("fontsize")
		fontcolor = request.POST.get("fontcolor")
		sname = request.POST.get("sname")
		
		fcolorList = fontcolor.split(',')
		fcolorList = [int(elem) for elem in fcolorList]
		font_color = tuple(fcolorList)
		
		img0 = cv2.imread(blankpic)
		
		#----------绘制名字文字-----------
		imgPIL = Image.fromarray(cv2.cvtColor(img0, cv2.COLOR_BGR2RGB))
		fontText2 = ImageFont.truetype("media/font/%s"%(imgfont2), msgwordsize, encoding="utf-8")
		#---------左上角位置-----------------

		pos = (msgx, msgy)
		drawPIL = ImageDraw.Draw(imgPIL)
		
		content = scontent.replace(' ','   ')
		drawPIL.text(pos, content, font_color, font=fontText2)
		imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
		
		#current_timestamp = time.time()
		#temptime = int(current_timestamp)
		rootPath = os.getcwd()
		mergeImgPath = '/media/newimg/%s_%s.png'%(pbid,picid)
		mergePath = '%s%s'%(rootPath,mergeImgPath)

		rs_write = cv2.imwrite(mergePath,imgPutText)
		
		sql = "update setpic4 set msgx=%s,msgy=%s,imgfont2=%s,msgwordsize=%s,fontcolor=%s,mergepic=%s,scontent=%s where picid=%s"
		param = (msgx,msgy,imgfont2,msgwordsize,fontcolor,mergeImgPath,scontent,picid)
		with connection.cursor() as cursor:
			rs=cursor.execute(sql,param)
			connection.commit()
		
	return redirect('/manage/wordpos/?picid=%s&id=%s&bookname=%s'%(picid,pbid,bookname))

#----------------生成预览图片------------------------------
#两边是文字
def generateImg0(uid,cname,blankpic,rs):
	picid,leftwords,rightwords,centerpos,letterwidth,nameposy,imgfont,wordsize,fontcolor = rs[0],rs[1],rs[2],rs[3],rs[4],rs[5],rs[6],rs[7],rs[8]
	fontcolorArr = fontcolor.split(',')
	fcolorList = [int(elem) for elem in fontcolorArr]
	fontColor = tuple(fcolorList)
	img0 = cv2.imread(blankpic)
	len_left = len(leftwords)
	left_width = len_left*letterwidth  # 左词宽度
	cnameLen = len(cname)*letterwidth	#名字长度
	#左图起始位置=中间点位置-半个名字的长度-空格-左图宽度
	leftpos = centerpos-int(cnameLen/2)-letterwidth-left_width
	sentence = leftwords+" "+cname+" "+rightwords
	#----------绘制文字-----------
	imgPIL = Image.fromarray(cv2.cvtColor(img0, cv2.COLOR_BGR2RGB))
	drawPIL = ImageDraw.Draw(imgPIL)
	textSize = wordsize
	fontText = ImageFont.truetype("media/font/%s"%(imgfont), textSize, encoding="utf-8")
	pos = (leftpos, nameposy)
	color = fontColor
	drawPIL.text(pos, sentence, color, font=fontText)
	imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
	cv2.imwrite('media/preimg/%s_%s.png'%(uid,picid),imgPutText)
	mergeImgPath = 'media/preimg/%s_%s.png'%(uid,picid)
	return mergeImgPath

#生成换名图片
def previewImage(request):
	mergeImgPathArr=[]
	if request.method == 'GET':
		uid = request.GET.get("uid")
		bookid = request.GET.get("bookid")
		uname = request.GET.get("uname")
		uphoto = request.GET.get("uphoto")
		sql = "select id,pagenum,pflag,blankpic,nameflag,nametype from bookpics where pbid=%s and defflag=0 order by pagenum"
		param = (bookid,)
		with connection.cursor() as cursor:
			cursor.execute(sql,param)
			rs = cursor.fetchall()
			for item in rs:
				picid = item[0]
				blankpic = item[3]
				pflag = item[2]
				nameflag = item[4]
				if nameflag==1:
					nametype = item[5]
					if nametype==0:		#纯文字
						sql1 = "select picid,leftwords,rightwords,centerpos,letterwidth,nameposy,imgfont,wordsize,fontcolor from setpic1 where picid=%s"
						cursor.execute(sql1,(picid,))
						rs1 = cursor.fetchone()
						if rs1 is not None:
							mergeImgPath = generateImg0(uid,uname,blankpic,rs1)
							mergeImgPathArr.append(mergeImgPath)
					elif nametype==1:	#两图加文字
						pass
			#connection.commit()
	json_str = json.dumps(mergeImgPathArr, ensure_ascii=False, indent=2)
	#ensure_ascii=False 参数确保输出的 JSON 字符串中的非 ASCII 字符不会被转义。indent=2 参数则是为了让输出的 JSON 字符串具有更好的可读性，通过添加缩进。
	return HttpResponse(json_str)
	'''
Dear Kelly,
You have broughts such joy and wonder
to our lives.We hope that you find the same joy
and happiness,wherever your life takes you.
	'''