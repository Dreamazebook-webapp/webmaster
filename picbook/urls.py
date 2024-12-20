"""
URL configuration for picbook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import pages
from .views import customizebook
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
	path('manage/login/', pages.managelogin),
	path('manage/index/', pages.manageindex),
	path('manage/addpage/', pages.addPage),
	path('manage/insertpage/', pages.insertPage),
	path('manage/delpage/', pages.delbookpage),
	path('manage/menu/', pages.menu),
	path('manage/addmenu/', pages.addmenu),
	path('manage/delmenu/', pages.delmenu),
	path('manage/bcategory/', pages.bcategory),
	path('manage/addbcategory/', pages.addBcategory),
	path('manage/delbcategory/', pages.delBcategory),
	path('manage/addbook/', pages.addbook),
	path('manage/bindmenu/', pages.bindmenu),
	path('manage/bindmenuexec/', pages.bindmenuexec),
	path('manage/bindcategory/', pages.bindcategory),
	path('manage/bindcategoryexec/', pages.bindcategoryexec),
	path('manage/pbcontent/', customizebook.pbcontent),
	path('manage/addpic/', customizebook.addpic),
	path('manage/delbookpic/', customizebook.delbookpic),
	path('manage/wordpos/', customizebook.wordpos),
	path('manage/mergepic0/', customizebook.mergepic0),
	path('manage/mergepic1/', customizebook.mergepic1),
	path('manage/mergepic2/', customizebook.mergepic2),
	path('manage/mergepic3/', customizebook.mergepic3),
	path('manage/mergepic4/', customizebook.mergepic4),
	path('manage/previewImage/', customizebook.previewImage),	#http方式返回生成的绘本
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
