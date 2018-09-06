from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):

    # 指定一些和表单相关的东西
    class Meta:
        # 表单对应的数据库模型是 Comment 类
        model = Comment
        # 表单需要显示的字段
        fields = ['name', 'email', 'url', 'text']