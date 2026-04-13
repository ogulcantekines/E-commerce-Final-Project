from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('', views.index, name="index"),
    path('kategori/<slug:category_slug>/', views.category_list, name='category_list'),
    path('urun/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('hesap/', views.user_account, name='user_account'),
    path('sepetim/', views.cart, name='cart'),
    path('logout/', views.user_logout, name='logout'),
    path('siparislerim/', views.orders, name='orders'),
    path('siparislerim/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Sepet İşlemleri
    path('sepete-ekle/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('sepetten-azalt/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('sepetten-sil/<int:product_id>/', views.delete_cart_item, name='delete_cart_item'),
    
    # Arama ve Ödeme - BURASI DÜZELTİLDİ
    path('ara/', views.search, name='search'),
    path('odeme/', views.checkout_view, name='checkout'), 

    # Şifre İşlemleri
    path('sifre-degistir/', views.change_password, name='change_password'),
    
    # Şifre Sıfırlama
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('profilim/', views.profile_view, name='profile'),
    path('urun/<slug:product_slug>/yorum/', views.add_review, name='add_review'),

    # Karşılaştırma
    path('karsilastir/', views.compare_view, name='compare'),
    path('karsilastir/ekle/<int:product_id>/', views.add_to_compare, name='add_to_compare'),
    path('karsilastir/cikar/<int:product_id>/', views.remove_from_compare, name='remove_from_compare'),
]