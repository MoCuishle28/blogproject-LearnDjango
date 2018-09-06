"""
自定义模板标签代码写在 blog_tags.py 文件中
模板标签本质上就是一个 Python 函数
"""
from django.db.models.aggregates import Count
from django import template
from ..models import Post, Category, Tag

# 导入 template 这个模块，实例化了一个 template.Library 类，并将函数 get_recent_posts 装饰为 register.simple_tag
register = template.Library()

# 为了能够通过 {% get_recent_posts %} 的语法在模板中调用这个函数，要按照 Django 的规定注册这个函数为模板标签
@register.simple_tag
def get_recent_posts(num=5):
    """
    获取数据库中前 num 篇文章，这里 num 默认为 5
    """
    return Post.objects.all().order_by('-created_time')[:num]

@register.simple_tag
def archives():
    """
    归档模板标签
    """
    # dates 方法会返回一个列表，元素为每一篇文章（Post）的创建时间，且是 Python 的 date 对象，精确到月份，降序排列
    return Post.objects.dates('created_time', 'month', order='DESC')

@register.simple_tag
def get_categories():
    # 记得在顶部引入 count 函数
    # Count 计算分类下的文章数，其接受的参数为需要计数的模型的名称
    # 对结果集做了一个过滤，使用 filter 方法把 num_posts 的值小于 1 的分类过滤掉
    # num_posts 的值小于 1 表示该分类下没有文章，没有文章的分类我们不希望它在页面中显示
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

@register.simple_tag
def get_tags():
    # 记得在顶部引入 Tag model
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)