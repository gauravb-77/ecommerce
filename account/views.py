from django.shortcuts import render, redirect

from .forms import CreateUserForm, LoginForm, UpdateUserForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress, Order, OrderItem

from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.sites.shortcuts import get_current_site
from .token import user_tokenizer_generate

from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from django.contrib import messages


def register(request):

    form = CreateUserForm()

    if request.method == 'POST':

        form = CreateUserForm(request.POST)

        if form.is_valid():

            user = form.save()

            user.is_active = False

            user.save()

            # Email verification setup (template)

            current_site = get_current_site(request)

            subject = 'Account verification email'
        
            message = render_to_string('account/registration/email-verification.html', {

                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': user_tokenizer_generate.make_token(user),

            })

            user.email_user(subject=subject, message=message)


            return redirect('email-verification-sent')

    context = {'form': form}

    return render(request, 'account/registration/register.html', context)


def email_verification(request, uidb64, token):
    
    # uniqueid
    
    unique_id = force_str(urlsafe_base64_decode(uidb64))

    user = User.objects.get(pk=unique_id)

    # Success 

    if user and user_tokenizer_generate.check_token(user, token):

        user.is_active = True

        user.save()

        return redirect('email-verification-success')


    # Failed 

    else:

        return redirect('email-verification-failed')        



def email_verification_sent(request):
    
    return render(request, 'account/registration/email-verification-sent.html')


def email_verification_success(request):
    
    return render(request, 'account/registration/email-verification-success.html')

def email_verification_failed(request):
    
    return render(request, 'account/registration/email-verification-failed.html')



# Login

def my_login(request):

    if request.user.is_authenticated:

        return redirect('store')

    form = LoginForm()

    if request.method == 'POST':

        form = LoginForm(request, request.POST)

        if form.is_valid():

            username = request.POST.get('username')

            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                login(request, user)

                return redirect('dashboard')

    context = {'form': form}

    return render(request, 'account/my-login.html', context)



# Logout

def user_logout(request):

    try:

        for key in list(request.session.keys()):

            if key == 'session_key':

                continue

            else:

                del request.session[key]

    except KeyError:

        pass

    messages.success(request, 'Logout success')

    return redirect('store')


@login_required(login_url='my-login')
def dashboard(request):

    return render(request, 'account/dashboard.html')


@login_required(login_url='my-login')
def profile_management(request):

    user_form = UpdateUserForm(instance=request.user)

    # Updating our user's username and email

    if request.method == 'POST':

        user_form = UpdateUserForm(request.POST, instance=request.user)

        if user_form.is_valid():

            user_form.save()

            messages.info(request, 'Profile updated successfully!')

            return redirect('dashboard')

    context = {'form': user_form}

    return render(request, 'account/profile-management.html', context)


@login_required(login_url='my-login')
def delete_account(request):

    if request.method == 'POST':

        user = User.objects.get(id=request.user.id)

        user.delete()

        messages.error(request, 'Account deleted')

        return redirect('store')

    return render(request, 'account/delete-account.html')


# Shipping view

@login_required(login_url='my-login')
def manage_shipping(request):

    try:

        # Account user with shipment information

        shipping = ShippingAddress.objects.get(user=request.user)

    except ShippingAddress.DoesNotExist:

        # Account user with no shipment information

        shipping = None

    
    form = ShippingForm(instance=shipping)

    if request.method == 'POST':

        form = ShippingForm(request.POST, instance=shipping)

        if form.is_valid():

            # Assign the user FK on the object 

            user_shipping = form.save(commit=False)

            # Adding the FK itself

            user_shipping.user = request.user

            user_shipping.save()

            return redirect('dashboard')

    context = {'form': form}

    return render(request, 'account/manage-shipping.html', context)


@login_required(login_url='my-login')
def track_orders(request):

    try:

        orders = OrderItem.objects.filter(user=request.user)

        context = {'orders': orders}

        return render(request, 'account/track-orders.html', context)

    except Order.DoesNotExist:

        return render(request, 'account/track-orders.html') 

