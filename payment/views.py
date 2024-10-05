from django.shortcuts import render

from django.forms import Form

from django.http import JsonResponse

from payment.forms import ShippingForm

from payment.models import ShippingAddress, Order, OrderItem

from store.models import Product

from cart.cart import Cart

from django.core.mail import send_mail

from django.conf import settings


def checkout(request):

    # Users with accounts -- Pre-fill the form

    if request.user.is_authenticated:

        try:

            # Authenticated users WITH shipping information

            shipping_address = ShippingAddress.objects.get(user=request.user)

            context = {'shipping_address': shipping_address}

            return render(request, 'payment/checkout.html', context)

        except:

            # Authenticated users with NO shipping information

            return render(request, 'payment/checkout.html')

    else:

        # Guest users 
        
        return render(request, 'payment/checkout.html')


def complete_order(request):

    if request.POST.get('action') == 'post':

        name = request.POST.get('name')
        email = request.POST.get('email')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')

        # All-in-one shipping address 

        shipping_address = address1 + '\n' + address2 + '\n' + city + '\n' + state + '\n' + zipcode

        # Shopping cart information

        cart = Cart(request)

        total_cost = cart.get_total()


        '''

        Order variations

        1) Create order -> Account users WITH + WITHOUT shipping information

        2) Create order -> Guest users without an account

        '''

        # 1) Create order -> Account users WITH + WITHOUT shipping information

        products_list = []

        if request.user.is_authenticated:

            order = Order.objects.create(full_name=name, email=email, shipping_address=shipping_address, amount_paid=total_cost, user=request.user)

            for item in cart:
                
                OrderItem.objects.create(order=order, product=item['product'], quantity=item['qty'], price=item['price'], user=request.user)

                products_list.append(item['product'].title)


        # 2) Create order -> Guest users without an account

        else:

            order = Order.objects.create(full_name=name, email=email, shipping_address=shipping_address, amount_paid=total_cost)

            for item in cart:
                
                OrderItem.objects.create(order=order, product=item['product'], quantity=item['qty'], price=item['price'])

                products_list.append(item['product'].title)

        all_products = products_list


        # Email user

        send_mail('Order received', 'Hi ! ' + '\n\n' + 'Thank you for placing your order' + '\n\n' + 'Please see your order below :' + '\n\n' + '\n'.join(all_products) + '\n\n' + 'Total paid: ₹ ' + str(cart.get_total()), from_email=settings.EMAIL_HOST_USER, recipient_list=[email], fail_silently=False)


        order_success = True

        response = JsonResponse({'order_success': order_success})

        return response



def payment_success(request):

    # Clear the shopping cart

    for key in list(request.session.keys()):

        if key == 'session_key':

            del request.session[key]

    return render(request, 'payment/payment-success.html')


def payment_failed(request):

    print(request)

    return render(request, 'payment/payment-failed.html')
