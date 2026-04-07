from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. KATEGORİ MODELİ
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# 2. ÜRÜN MODELİ
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Kategori", null=True)
    brand = models.CharField(max_length=100, verbose_name="Marka")
    name = models.CharField(max_length=200, verbose_name="Ürün Adı")
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(verbose_name="Ürün Açıklaması")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    image = models.ImageField(upload_to='products/', verbose_name="Ürün Resmi")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# 3. SLIDER MODELİ
class Slider(models.Model):
    title = models.CharField(max_length=100, verbose_name="Görsel Adı (Admin Panelinde Görünür)")
    image = models.ImageField(upload_to='sliders/')
    is_active = models.BooleanField(default=True, verbose_name="Yayında mı?")

    def __str__(self):
        return self.title

# 4. PROFİL MODELİ (Kullanıcı bilgilerini saklar)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    phone = models.CharField(max_length=15, verbose_name="Telefon", null=True, blank=True)
    city = models.CharField(max_length=50, verbose_name="Şehir", null=True, blank=True)
    address = models.TextField(verbose_name="Kalıcı Adres", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Profil"

# 5. SİPARİŞ MODELİ
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Müşteri")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sipariş Tarihi")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="Toplam Tutar")
    is_completed = models.BooleanField(default=False, verbose_name="Ödeme Tamamlandı mı?")
    
    # Sipariş anındaki iletişim bilgileri
    phone = models.CharField(max_length=15, verbose_name="Siparişteki Telefon", null=True, blank=True)
    city = models.CharField(max_length=50, verbose_name="Siparişteki Şehir", null=True, blank=True)
    address = models.TextField(verbose_name="Siparişteki Açık Adres", null=True, blank=True)

    def __str__(self):
        return f"Sipariş #{self.id} - {self.user.username}"

# 6. SİPARİŞ KALEMLERİ MODELİ
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Sipariş")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Adet")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sipariş Anındaki Fiyat")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# --- OTOMATİK PROFİL SİNYALLERİ ---

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Yeni bir kullanıcı (müşteri) oluştuğunda profilini de oluşturur
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # 'hasattr' kontrolü sayesinde profili olmayan (admin gibi) kullanıcılar hata vermez
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()