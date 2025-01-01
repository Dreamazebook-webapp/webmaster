import mysql.connector
#创建数据库连接
db = mysql.connector.connect(
	host="127.0.0.1",
	user="root",
	password="root",
	database="picbook"
)

-- 生成动态文字并换脸表
create table taskcontent(
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  taskid bigint(20) NOT NULL,
  picid bigint(20) NOT NULL,
  pagenum int NOT NULL,			-- 1为首页
  pagepic varchar(300) not null,	-- 生成后的图片或无动态文字的图片
  pflag tinyint not null,		-- 是否需要换头像，0表不需要，1表需要
  finish tinyint not null default 1	-- 是否完成，0表完成，1表未完成
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

def addTask(uid,cid,pbid,rname,uphoto):
	global db
	#创建游标对象
	cursor = db.cursor()
	sql = "insert into task set cid='1',pbid=1,rname='hello',uphoto=''"
	cursor.execute(sql)
	#获取刚刚插入的id
	sql_id = "SELECT LAST_INSERT_ID()"
	cursor.execute(sql_id)
	rs_id = cursor.fetchone()
	taskid = rs_id[0]
	#查询绘本，读取前7页，插入任务内容表
	sql1 = "select id,pagenum,pagepic,pflag,blankpic,nameflag,nametype from bookpics where pbid=%s and defflag=0 order by pagenum limit 0,7"
	cursor.execute(sql)
	rs_pic = cursor.fetchall()
	for item in rs_pic:
		if item.3==0 and item.5==0:	#无需换头且没有动态字
			#直接插入taskcontent, finish=0
			sql2 = "insert into taskcontent (taskid,picid,pagenum,pagepic,finish) values(%d,%d,%d,%s,0)"
		elif 
	connection.commit()
	