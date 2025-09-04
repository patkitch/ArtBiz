
from django.utils.html import format_html
from django.contrib import admin
from . import models

# ---------- Inlines ----------
class ProductVariantInline(admin.TabularInline):
    model = models.ProductVariant
    extra = 1
    fields = ("option_label", "price_cents", "edition_size", "edition_sold", "taxable")
    show_change_link = True

class MediaInline(admin.TabularInline):
    model = models.Media
    extra = 1
    fields = ("kind", "image", "alt_text", "preview")
    list_display = ("product", "kind", "image", "thumb")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.file:
            return format_html('<img src="{}" style="height:80px; border:1px solid #ddd;"/>', obj.file.url)
        return "—"
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px; border:1px solid #ddd;"/>', obj.image.url)
        return "—"

class InventoryByLocationInline(admin.TabularInline):
    model = models.InventoryByLocation
    extra = 1
    fields = ("location", "on_hand")
    # This inline will be attached to ProductVariant (via FK variant)

class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 1
    fields = ("variant", "qty", "unit_price_cents")

class ConsignmentItemInline(admin.TabularInline):
    model = models.ConsignmentItem
    extra = 1
    fields = ("variant", "qty", "listed_price_cents")


# ---------- Admins ----------
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "title", "product_type", "artist", "is_active", "created_at")
    search_fields = ("sku", "title", "description", "series", "artist")
    list_filter = ("product_type", "is_active", "artist")
    date_hierarchy = "created_at"
    inlines = [ProductVariantInline, MediaInline]  # add variants + media directly on the product page


@admin.register(models.ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "option_label", "price_cents", "edition_size", "edition_sold", "taxable")
    search_fields = ("option_label", "product__title", "product__sku")
    list_filter = ("taxable",)
    inlines = [InventoryByLocationInline]  # manage inventory for this variant right on the variant page
# Optional: show a read-only pretty price on the form too
    readonly_fields = ("price_preview",)

    def price_display(self, obj):
        return f"${obj.price:.2f}"
    price_display.short_description = "Price"

    def price_preview(self, obj):
        return f"${obj.price:.2f}" if obj.pk else "—"
    price_preview.short_description = "Price (preview)"


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_sellable")
    search_fields = ("name",)
    list_filter = ("is_sellable",)


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "email", "phone")
    list_filter = ("kind",)
    search_fields = ("name", "email", "phone", "notes")


@admin.register(models.CrmNote)
class CrmNoteAdmin(admin.ModelAdmin):
    list_display = ("contact", "created_at")
    search_fields = ("contact__name", "note")
    date_hierarchy = "created_at"


@admin.register(models.InventoryByLocation)
class InventoryByLocationAdmin(admin.ModelAdmin):
    list_display = ("variant", "location", "on_hand")
    search_fields = ("variant__option_label", "variant__product__title", "location__name")
    list_filter = ("location",)


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "channel", "total_cents", "buyer_contact", "created_at", "paid_at")
    list_filter = ("status", "channel")
    search_fields = ("id", "buyer_contact__name")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "amount_cents", "received_at")
    list_filter = ("method",)
    date_hierarchy = "received_at"
    search_fields = ("order__id",)


@admin.register(models.CoaCertificate)
class CoaCertificateAdmin(admin.ModelAdmin):
    list_display = ("product", "variant", "serial_no", "purchaser_contact", "issued_at")
    search_fields = ("serial_no", "product__title", "variant__option_label", "purchaser_contact__name")
    date_hierarchy = "issued_at"


@admin.register(models.Consignment)
class ConsignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "gallery_contact", "start_date", "end_date", "commission_rate")
    search_fields = ("gallery_contact__name",)
    date_hierarchy = "start_date"
    inlines = [ConsignmentItemInline]


@admin.register(models.ConsignmentItem)
class ConsignmentItemAdmin(admin.ModelAdmin):
    list_display = ("consignment", "variant", "qty", "listed_price_cents")
    search_fields = ("consignment__id", "variant__option_label", "variant__product__title")


@admin.register(models.Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("product", "kind", "image", "thumb")
    list_filter = ("kind",)
    search_fields = ("product__title", "alt_text")

    def thumb(self, obj):
        if obj.file:
            return format_html('<img src="{}" style="height:50px; border:1px solid #ddd;"/>', obj.file.url)
        return "—"
    thumb.short_description = "Preview"

