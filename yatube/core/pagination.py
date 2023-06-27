from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate(request, queryset, count_per_page):
    paginator = Paginator(queryset, count_per_page)
    page = request.GET.get('page')
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)
    return paginated_queryset
