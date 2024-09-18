from django.shortcuts import render

from .cart import Cart

from store.models import Product

from django.shortcuts import get_object_or_404

from django.http import JsonResponse

from django.shortcuts import redirect


def cart_summary(request):

    cart = Cart(request)

    if cart.get_total() > 500:

        shipping_amount = 70.00

    else:

        shipping_amount = 40.00

    total_amount_to_be_paid = float(cart.get_total()) + shipping_amount

    context = {'cart': cart, 'shipping_amount': shipping_amount, 'total_amount_to_be_paid': total_amount_to_be_paid}
    
    return render(request, 'cart/cart-summary.html', context)


def cart_add(request):
    
    cart = Cart(request)

    if request.POST.get('action') == 'post':

        product_id = int(request.POST.get('product_id'))

        product_quantity = int(request.POST.get('product_quantity'))

        product = get_object_or_404(Product, id=product_id)

        cart.add(product=product, product_qty=product_quantity)

        cart_quantity = cart.__len__()

        response = JsonResponse({'qty': cart_quantity})

        return response


def cart_delete(request):
    
    cart = Cart(request)

    if request.POST.get('action') == 'post':

        product_id = int(request.POST.get('product_id'))

        cart.delete(product=product_id)

        cart_quantity = cart.__len__()

        cart_total = cart.get_total()

        response = JsonResponse({'qty': cart_quantity, 'cart_total': cart_total})

        return response



def cart_update(request):

    cart = Cart(request)

    if request.POST.get('action') == 'post':

        product_id = int(request.POST.get('product_id'))

        product_qty = int(request.POST.get('product_qty'))

        product = Product.objects.get(pk=product_id)

        cart.update(product, product_qty)

        cart_quantity = cart.__len__()

        cart_total = cart.get_total()

        response = JsonResponse({'cart_quantity': cart_quantity, 'cart_total': cart_total})

        return response