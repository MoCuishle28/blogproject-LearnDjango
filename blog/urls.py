"""
这个文件将用于 blog 应用相关的 URL 配置

把不同的网址对应的处理函数写在一个 urls.py 文件里
当用户访问某个网址时，Django 就去会这个文件里找，如果找到这个网址，就会调用和它绑定在一起的处理函数（叫做视图函数）
"""

from django.conf.urls import url
# 从当前目录下导入了 views 模块
from . import views

app_name = 'blog'

# 网址和处理函数的关系写在了 urlpatterns 列表里
# 绑定关系的写法是把网址和对应的处理函数作为参数传给 url 函数（第一个参数是网址，第二个参数是处理函数）
# 另外我们还传递了另外一个参数 name，这个参数的值将作为处理函数 index 的别名，这在以后会用到
urlpatterns = [
    # # 第一个参数:网址是用正则表达式写的 Django 会用这个正则表达式去匹配用户实际输入的网址
    # # 如果匹配成功，就会调用其后面的视图函数做相应的处理
    # url(r'^$', views.index, name='index'),
    #
    # # 这条正则表达式的含义是: 以 post/ 开头 后跟一个至少一位数的数字 并且以 / 符号结尾
    # # 如 post/1/ , post/255/ 等都是符合规则的
    # # 这里 (?P<pk>[0-9]+) 表示命名捕获组
    # # 其作用是从用户访问的 URL 里把括号内匹配的字符串捕获并作为关键字参数传给其对应的视图函数 detail
    # # 比如当用户访问 post/255/ 时（注意 Django 不关心域名 只关心去掉域名后的相对 URL）
    # # 被括起来的部分 (?P<pk>[0-9]+) 匹配 255 这个 255 会在调用视图函数 detail 时被传递进去
    # # 实际上视图函数的调用是这样: detail(request, pk=255)
    # url(r'^post/(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    #
    # # 例如如果用户想查看 2017 年 3 月下的全部文章
    # # 他访问 /archives/2017/3/，那么 archives 视图函数的实际调用为：archives(request, year=2017, month=3)
    # url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.archives, name='archives'),
    # url(r'^category/(?P<pk>[0-9]+)/$', views.category, name='category'),

    # 配置类视图函数 IndexView
    # 对 url 函数来说，第二个参数传入的值必须是一个函数 IndexView 是一个类 不能直接替代 index 函数
    # 调用类视图的 as_view() 方法即可
    url(r'^$', views.IndexView.as_view(), name='index'),

    # 配置类视图
    url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='detail'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.ArchivesView.as_view(), name='archives'),
    url(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='category'),
    url(r'^tag/(?P<pk>[0-9]+)/$', views.TagView.as_view(), name='tag'),
]