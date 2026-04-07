from django.contrib import admin
from .models import Category, Product, Slider, Order, OrderItem
from django.db.models import Sum

# 1. Başlıkları Özelleştir
admin.site.site_header = "Online Shop Yönetim Paneli"
admin.site.site_title = "Admin Paneli"
admin.site.index_title = "Mağaza Özetine Hoş Geldiniz"

# 2. Sipariş Ürünleri (Inline)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False

# 3. Sipariş Yönetimi
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at', 'is_completed')
    list_filter = ('is_completed', 'created_at')
    search_fields = ('user__username', 'user__first_name')
    inlines = [OrderItemInline]

    def changelist_view(self, request, extra_context=None):
        total_revenue = Order.objects.filter(is_completed=True).aggregate(Sum('total_price'))['total_price__sum'] or 0
        extra_context = extra_context or {}
        extra_context['total_revenue'] = total_revenue
        return super().changelist_view(request, extra_context=extra_context)

# 4. Ürün Yönetimi
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'brand')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'brand')
    prepopulated_fields = {'slug': ('name',)}

# 5. Diğer Modeller (Bunları bir kez kaydetmek yeterli)
admin.site.register(Category)
admin.site.register(Slider)