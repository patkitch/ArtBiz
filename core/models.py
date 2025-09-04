

# Create your models here.
from django.db import models
from django.utils import timezone
import re
from django.utils.text import slugify
from decimal import Decimal

SKU_MAX_LEN = 255

def normalize_code(text: str) -> str:
    """
    Uppercase A-Z0-9 with dashes, no spaces/symbols.
    """
    up = re.sub(r'[^A-Za-z0-9]+', '-', text).strip('-')
    return up.upper()

def unique_sku_for(model, base: str, max_len: int = SKU_MAX_LEN) -> str:
    """
    Returns a unique SKU for `model` by appending -2, -3, ... if needed.
    """
    base = normalize_code(base)[:max_len]
    if not model.objects.filter(sku=base).exists():
        return base
    i = 2
    while True:
        suffix = f"-{i}"
        sku_try = (base[: max_len - len(suffix)]) + suffix
        if not model.objects.filter(sku=sku_try).exists():
            return sku_try
        i += 1


# ---------- Core Catalog ----------
class Product(models.Model):
    class ProductType(models.TextChoices):
        ORIGINAL = 'original', 'Original'
        LIMITED = 'limited_print', 'Limited Edition Print'
        OPEN = 'open_print', 'Open Edition Print'
        MERCH = 'merch', 'Merch'

    sku = models.CharField(max_length=255, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    product_type = models.CharField(max_length=20, choices=ProductType.choices)
    artist = models.CharField(max_length=255, default='Patricia Forbes')
    series = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.sku})"
    def save(self, *args, **kwargs):
        # Auto-generate SKU if blank
        if not self.sku:
            base = f"{self.artist}-{self.title}"
            self.sku = unique_sku_for(Product, base)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    option_label = models.CharField(max_length=255)  # e.g., "18x24 Hahnemühle"
    price_cents = models.PositiveIntegerField()
    edition_size = models.PositiveIntegerField(blank=True, null=True)  # NULL = open edition
    edition_sold = models.PositiveIntegerField(default=0)
    weight_grams = models.PositiveIntegerField(blank=True, null=True)
    taxable = models.BooleanField(default=True)
    @property
    def price(self) -> Decimal:
        return Decimal(self.price_cents) / Decimal(100)

    class Meta:
        unique_together = ('product', 'option_label')

    def __str__(self):
        return f"{self.product.title} - {self.option_label}"


class Media(models.Model):
    class MediaKind(models.TextChoices):
        PRIMARY = 'primary', 'Primary'
        DETAIL = 'detail', 'Detail'
        FRAMED = 'framed', 'Framed'
        IN_SITU = 'in_situ', 'In Situ'

    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='media')
    kind = models.CharField(max_length=20, choices=MediaKind.choices)
        # replace URL with actual uploaded image file
    image = models.ImageField(upload_to="products/%Y/%m/", null=True, blank=True)   # e.g., media/products/2025/09/xxx.jpg
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.product.title} — {self.kind}"


# ---------- Contacts / CRM ----------
class Contact(models.Model):
    class Kind(models.TextChoices):
        COLLECTOR = 'collector', 'Collector'
        VENDOR = 'vendor', 'Vendor'
        GALLERY = 'gallery', 'Gallery'
        STAFF = 'staff', 'Staff'
        OTHER = 'other', 'Other'

    kind = models.CharField(max_length=20, choices=Kind.choices)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True, unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.kind})"


class CrmNote(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='crm_notes', related_query_name='crm_note',)
    note = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)


# ---------- Locations & Inventory ----------
class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)  # e.g., 'Studio', 'Gallery'
    is_sellable = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class InventoryByLocation(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='location_inventory')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='inventory')
    on_hand = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('variant', 'location')


# ---------- Orders / Payments ----------
class Order(models.Model):
    class Channel(models.TextChoices):
        ONLINE = 'online', 'Online'
        IN_PERSON = 'in_person', 'In Person'
        CONSIGNMENT = 'consignment', 'Consignment'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FULFILLED = 'fulfilled', 'Fulfilled'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'

    buyer_contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=20, choices=Channel.choices, default=Channel.ONLINE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    subtotal_cents = models.IntegerField(default=0)
    tax_cents = models.IntegerField(default=0)
    shipping_cents = models.IntegerField(default=0)
    total_cents = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    unit_price_cents = models.PositiveIntegerField()


class Payment(models.Model):
    class Method(models.TextChoices):
        CARD = 'card', 'Card'
        CASH = 'cash', 'Cash'
        CHECK = 'check', 'Check'
        STRIPE = 'stripe', 'Stripe'
        PAYPAL = 'paypal', 'PayPal'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=Method.choices)
    amount_cents = models.PositiveIntegerField()
    received_at = models.DateTimeField(default=timezone.now)


# ---------- COAs ----------
class CoaCertificate(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    serial_no = models.CharField(max_length=50)  # e.g., "7/50"
    purchaser_contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    issued_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('variant', 'serial_no')


# ---------- Consignments ----------
class Consignment(models.Model):
    gallery_contact = models.ForeignKey(Contact, on_delete=models.CASCADE, limit_choices_to={'kind': 'gallery'})
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 40.00 = 40%

    def __str__(self):
        return f"Consignment {self.id} ({self.gallery_contact})"


class ConsignmentItem(models.Model):
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    listed_price_cents = models.PositiveIntegerField()


   

