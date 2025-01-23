from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from cart.forms import CartAddProductForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from .models import Product, Order, OrderItem, BlogPost

def home(request):
    products = Product.objects.all()[:3]  # Show first 4 coffees
    return render(request, 'coffee/home.html', {'products': products})

def product_list(request):
    products = Product.objects.all() # get all product models.py product data to product listing
    context = {
        'products' : products,
    }
    return render(request, 'coffee/product_list.html',context) # render out into prouducts.html

def product_single(request, product_id):
    product = get_object_or_404(Product, pk=product_id, id=product_id)
    cart_product_form = CartAddProductForm()
    context = {
        'product' : product,
        'cart_product_form' : cart_product_form,
    }
    return render(request, 'coffee/product_single.html', context)

def about(request):
    return render(request, 'coffee/about.html')

def contact(request):
    return render(request, 'coffee/contact.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, '註冊成功！')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})





def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'total_price': float(item['price']) * item['quantity']
        })
        total += float(item['price']) * item['quantity']
    
    return render(request, 'coffee/cart.html', {
        'cart_items': cart_items,
        'cart_total': total
    })





def checkout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = request.session.get('cart', {})
            
            if not cart:
                return JsonResponse({'success': False, 'message': '購物車為空'})
            
            # Create order record
            order = Order.objects.create(
                customer_name=data['name'],
                customer_phone=data['phone'],
                customer_pickup=data['pickup'],
                total_price=float(data['cart_total']),
                status='pending'
            )
            
            # Create order items
            for product_id, item in cart.items():
                product = get_object_or_404(Product, id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=float(item['price'])
                )
            
            # Clear cart
            request.session['cart'] = {}
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        cart_items.append({
            'product_id': product_id,
            'name': product.name,  # Get name from Product model
            'price': float(item['price']),
            'quantity': item['quantity'],
            'total_price': float(item['price']) * item['quantity'],
            'image': product.image.url if product.image else '/static/images/menu-01.png'
        })
        total += float(item['price']) * item['quantity']
    
    return render(request, 'coffee/checkout.html', {
        'cart_items': cart_items,
        'cart_total': total
    })






def order_success(request):
    return render(request, 'coffee/order_success.html')

def fake_payment(request):
    cart_total = request.session.get('cart_total', 0)
    return render(request, 'coffee/fake_payment.html', {
        'cart_total': cart_total
    })

def profile(request):
    return render(request, 'coffee/profile.html')

def blog(request):
    posts_list = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    paginator = Paginator(posts_list, 6)  # Show 6 posts per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'coffee/blog.html', {
        'posts': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages()
    })

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Get recent posts (last 3 published posts)
    recent_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(id=post.id).order_by('-created_at')[:3]
    
    # Get related posts (posts with same tags)
    related_posts = BlogPost.objects.filter(
        tags__in=post.tags.all(),
        is_published=True
    ).exclude(id=post.id).distinct()[:3]
    
    return render(request, 'coffee/blog_detail.html', {
        'post': post,
        'recent_posts': recent_posts,
        'related_posts': related_posts
    })

from django.views.decorators.csrf import csrf_exempt

import logging
logger = logging.getLogger(__name__)

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            logger.debug(f"Raw request body: {request.body}")
            
            # Validate request body
            if not request.body:
                logger.debug("Empty request body")
                return JsonResponse({
                    'success': False,
                    'message': '請求內容為空'
                }, status=400)
            
            try:
                data = json.loads(request.body)
                logger.debug(f"Parsed JSON data: {data}")
            except json.JSONDecodeError as e:
                logger.debug(f"JSON decode error: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': '無效的JSON格式'
                }, status=400)
            
            # Validate required fields
            if 'product_id' not in data:
                return JsonResponse({
                    'success': False,
                    'message': '缺少產品ID'
                }, status=400)
            
            try:
                product_id = int(data['product_id'])
                quantity = int(data.get('quantity', 1))
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': '無效的產品ID或數量'
                }, status=400)
            
            # Validate quantity
            if quantity < 1:
                return JsonResponse({
                    'success': False,
                    'message': '數量必須大於0'
                }, status=400)
            
            # Get product
            try:
                product = get_object_or_404(Product, id=product_id)
            except:
                return JsonResponse({
                    'success': False,
                    'message': '找不到該產品'
                }, status=404)
            
            # Update cart
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] += quantity
            else:
                cart[str(product_id)] = {
                    'quantity': quantity,
                    'price': str(product.price),
                    'name': product.name,
                    'image': product.image.url if product.image else '/static/images/menu-01.png'
                }
            
            request.session['cart'] = cart
            request.session.modified = True
            
            return JsonResponse({
                'success': True, 
                'cart_total_items': sum(item['quantity'] for item in cart.values())
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'伺服器錯誤: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': '僅接受POST請求'
    }, status=405)

@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = data.get('quantity')
        
        cart = request.session.get('cart', {})
        if product_id in cart:
            quantity = int(quantity)
            if quantity > 0:
                cart[product_id]['quantity'] = quantity
            else:
                del cart[product_id]
        
        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({
            'success': True, 
            'cart_total_items': sum(item['quantity'] for item in cart.values())
        })
    
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]
        
        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({
            'success': True, 
            'cart_total_items': sum(item['quantity'] for item in cart.values())
        })
    
    return JsonResponse({'success': False}, status=400)
