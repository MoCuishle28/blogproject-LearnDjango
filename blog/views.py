from django.shortcuts import render, get_object_or_404
from comments.forms import CommentForm
from .models import Post, Category, Tag
import markdown
from django.http import HttpResponse
from django.views.generic import ListView, DetailView

# Create your views here.
# 编写视图函数，让它实现我们想要的功能

def index(request):
    """
    :param request:     是Django为我们封装好的 HTTP 请求，是类 HttpRequest 的一个实例
    :return:            返回了一个 HTTP 响应给用户
                        这个 HTTP 响应也是 Django 帮我们封装好的，是类 HttpResponse 的一个实例
                        我们给它传了一个自定义的字符串参数。
    """
    # return HttpResponse("欢迎访问我的博客首页！")

    """
    改为调用 render 函数 这个函数根据我们传入的参数来构造 HttpResponse
    render函数 这个函数根据我们传入的参数来构造 HttpResponse
    首先把 HTTP 请求传了进去 然后 render 根据第二个参数的值 blog/index.html 找到这个模板文件并读取模板中的内容
    之后 render 根据我们传入的 context 参数的值把模板中的变量替换为我们传递的变量的值
    {{ title }} 被替换成了 context 字典中 title 对应的值，同理 {{ welcome }} 也被替换成相应的值。
    """
    # return render(request, 'blog/index.html', context={
    #     'title': '我的博客首页',
    #     'welcome': '欢迎访问我的博客首页'
    # })

    # all() 函数从数据库里获取了全部的文章 存在了 post_list 变量里
    # 返回的是一个 QuerySet（可以理解成一个类似于列表的数据结构）(以created_time字段为顺序排序(- 号表示逆序))
    post_list = Post.objects.all().order_by('-created_time')
    # 如之前所说,render 函数渲染了 blog\index.html 模板文件 并把包含文章列表数据的 post_list 变量传给了模板
    return render(request, 'blog/index.html', context={'post_list': post_list})
    # 我们的 HTML 模板中的内容字符串被传递给 HttpResponse 对象并返回给浏览器
    # （Django 在 render 函数里隐式地帮我们完成了这个过程），这样用户的浏览器上便显示出了我们写的 HTML 模板的内容

def detail(request, pk):
    """
    根据我们从 URL 捕获的文章 id（也就是 pk，这里 pk 和 id 是等价的）获取数据库中文章 id 为该值的记录 然后传递给模板
    """
    # 用到了从 django.shortcuts 模块导入的 get_object_or_404 方法
    # 作用是当传入的 pk 对应的 Post 在数据库存在 就返回对应的 post，若不存在就返回一个 404 表明用户请求的文章不存在
    post = get_object_or_404(Post, pk=pk)

    # 阅读量 +1
    post.increase_views()

    # 对 post 的 body 的值做一下渲染，把 Markdown 文本转为 HTML 文本再传递给模板
    # 这样我们在模板中展示 {{post.body}} 的时候就不再是原始的 Markdown 文本了,而是渲染过后的 HTML 文本
    post.body = markdown.markdown(post.body,
                                  # 参数 extensions 它是对 Markdown 语法的拓展，这里我们使用了三个拓展，分别是 extra、codehilite、toc
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ])
    # 记得在顶部导入 CommentForm
    form = CommentForm()
    # 获取这篇 post 下的全部评论
    comment_list = post.comment_set.all()
    # 将文章、表单、以及文章下的评论列表作为模板变量传给 detail.html 模板，以便渲染相应数据。
    context = {'post': post,
               'form': form,
               'comment_list': comment_list
               }

    return render(request, 'blog/detail.html', context=context)

def archives(request, year, month):
    # 使用模型管理器（objects）的 filter 函数来过滤文章
    #  由于这里作为函数的参数列表 Django 要求我们把点替换成了两个下划线 即 created_time__year
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    ).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

def category(request, pk):
    # 记得在开始部分导入 Category 类
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

class IndexView(ListView):
    """
    把 index 视图函数改造成类视图函数
    IndexView 的功能是从数据库中获取文章（Post）列表
    ListView 就是从数据库中获取某个模型列表数据的 所以 IndexView 继承 ListView
    :param ListView:
    :return:
    """
    model = Post       # 将 model 指定为 Post 告诉 Django 我要获取的模型是 Post
    template_name = 'blog/index.html'   # 指定这个视图渲染的模板
    context_object_name = 'post_list'   # 指定获取的模型列表数据保存的变量名。这个变量会被传递给模板
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 5

    # 以下用于完善分页:

    def get_context_data(self, **kwargs):
        """
        在视图函数中将模板变量传递给模板是通过给 render 函数的 context 参数传递一个字典实现的，
        例如 render(request, 'blog/index.html', context={'post_list': post_list})，
        这里传递了一个 {'post_list': post_list} 字典给模板。
        在类视图中，这个需要传递的模板变量字典是通过 get_context_data 获得的，
        所以我们复写该方法，以便我们能够自己再插入一些我们自定义的模板变量进去。
        """

        # 首先获得父类生成的传递给模板的字典。
        context = super().get_context_data(**kwargs)

        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        # 例如如果规定每页 10 个数据，而本身只有 5 个数据，其实就用不着分页，此时 is_paginated=False。
        # 关于什么是 Paginator，Page 类在 Django Pagination 简单分页：http://zmrenwu.com/post/34/ 中已有详细说明。
        # 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用自己写的 pagination_data 方法获得显示分页导航条需要的数据，见下方。
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        # 将分页导航条的模板变量更新到 context 中，注意 pagination_data 方法返回的也是一个字典。
        context.update(pagination_data)

        # 将更新后的 context 返回，以便 ListView 使用这个字典中的模板变量去渲染模板。
        # 注意此时 context 字典中已有了显示分页导航条所需的数据。
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            # 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
            return {}

        # 当前页左边连续的页码号，初始值为空
        left = []

        # 当前页右边连续的页码号，初始值为空
        right = []

        # 标示第 1 页页码后是否需要显示省略号
        left_has_more = False

        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False

        # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        first = False

        # 标示是否需要显示最后一页的页码号。
        # 需要此指示变量的理由和上面相同。
        last = False

        # 获得用户当前请求的页码号
        page_number = page.number

        # 获得分页后的总页数
        total_pages = paginator.num_pages

        # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
        page_range = paginator.page_range

        if page_number == 1:
            # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
            # 此时只要获取当前页右边的连续页码号，
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
            # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            right = page_range[page_number:page_number + 2]

            # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
            if right[-1] < total_pages - 1:
                right_has_more = True

            # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
            # 所以需要显示最后一页的页码号，通过 last 来指示
            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
            # 此时只要获取当前页左边的连续页码号。
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

            # 如果最左边的页码号比第 2 页页码号还大，
            # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
            if left[0] > 2:
                left_has_more = True

            # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
            # 所以需要显示第一页的页码号，通过 first 来指示
            if left[0] > 1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
            # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第 1 页和第 1 页后的省略号
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return data


class CategoryView(ListView):
        """
        category 视图函数的功能也是从数据库中获取文章列表数据
        不过其和 index 视图函数不同的是它获取的是某个分类下的全部文章
        因此 category 视图函数中多了一步 :
            首先需要根据从 URL 中捕获的分类 id 并从数据库获取分类，然后使用 filter 函数过滤出该分类下的全部文章

        CategoryView 类中指定的属性值和 IndexView 中是一模一样的 如果为了进一步节省代码 可以直接继承 IndexView
        """
        model = Post
        template_name = 'blog/index.html'
        context_object_name = 'post_list'

        def get_queryset(self):
            cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
            return super(CategoryView, self).get_queryset().filter(category=cate)

class ArchivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,created_time__month=month )

# 记得在顶部导入 DetailView
class PostDetailView(DetailView):
    """
    从数据库获取模型的一条记录数据是常见的需求
    对于这种类型的需求 Django 提供了一个 DetailView 类视图 下面我们就来将 detail 视图函数转换为等价的类视图 PostDetailView
    """
    # 这些属性的含义和 ListView 是一样的
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    # 可以简单地把 get 方法的调用看成是 detail 视图函数的调用
    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response

    # 对应着 detail 视图函数中根据文章的 id（也就是 pk）获取文章 然后对文章的 post.body 进行 Markdown 渲染的代码部分
    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super(PostDetailView, self).get_object(queryset=None)
        post.body = markdown.markdown(post.body,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                      ])
        return post

    # 对应着 detail 视图函数中生成评论表单、获取 post 下的评论列表的代码部分
    def get_context_data(self, **kwargs):
        # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（DetailView 已经帮我们完成），
        # 还要把评论表单、post 下的评论列表传递给模板。
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context

class TagView(ListView):
    """
    和 CategoryView 一样，我们使用了类视图 代码几乎和 CategoryView 是一样的
    具体请参考 CategoryView 部分的代码和说明
    """
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)