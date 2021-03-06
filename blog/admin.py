from django.contrib import admin
from .models import Post, Category, Tag

"""
# Register your models here.
在后台注册我们自己创建的模型 Django Admin 才能知道它们的存在
"""

# 在 admin post 列表页面，我们只看到了文章的标题，但是我们希望它显示更加详细的信息
# 这需要我们来定制 Admin  在 admin.py 添加如下代码:
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']


# 把在命令行创建的Post 和 上述代码创建的 PostAdmin 注册进来
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)