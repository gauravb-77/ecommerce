from django.shortcuts import render, get_object_or_404

from .models import Category, Product


def store(request):

    search_query = request.GET.get('q', '')

    all_products = Product.objects.filter(title__icontains=search_query).order_by('title')

    context = {'all_products': all_products, 'search_query': search_query}

    return render(request, 'store/store.html', context)


def categories(request):

    all_categories = Category.objects.all().order_by('name')

    return {'all_categories': all_categories}


def list_category(request, category_slug):

    category = get_object_or_404(Category, slug=category_slug)

    products = Product.objects.filter(category=category).order_by('title')

    context = {'category': category, 'products': products}

    return render(request, 'store/list-category.html', context)


def product_info(request, product_slug):

    product = get_object_or_404(Product, slug=product_slug)

    context = {'product': product}

    return render(request, 'store/product-info.html', context)

