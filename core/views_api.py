from rest_framework import viewsets, permissions
from . import models, serializers

class DefaultPerms(permissions.AllowAny):  # open during development
    pass

# -------- Catalog --------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all().order_by("title")
    serializer_class = serializers.ProductSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["product_type", "is_active", "series", "artist"]
    search_fields = ["title", "sku", "description", "series", "artist"]
    ordering_fields = ["title", "created_at"]

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = models.ProductVariant.objects.select_related("product").all()
    serializer_class = serializers.ProductVariantSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["product", "edition_size", "taxable"]
    search_fields = ["option_label", "product__title"]
    ordering_fields = ["price_cents", "edition_sold"]

class MediaViewSet(viewsets.ModelViewSet):
    queryset = models.Media.objects.select_related("product").all()
    serializer_class = serializers.MediaSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["product", "kind"]
    search_fields = ["alt_text", "product__title"]

# -------- Contacts / CRM --------
class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["kind"]
    search_fields = ["name", "email", "phone", "notes"]

class CrmNoteViewSet(viewsets.ModelViewSet):
    queryset = models.CrmNote.objects.select_related("contact").all()
    serializer_class = serializers.CrmNoteSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["contact"]
    search_fields = ["note", "contact__name"]

# -------- Locations / Inventory --------
class LocationViewSet(viewsets.ModelViewSet):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["is_sellable"]
    search_fields = ["name"]

class InventoryByLocationViewSet(viewsets.ModelViewSet):
    queryset = models.InventoryByLocation.objects.select_related("variant", "location", "variant__product").all()
    serializer_class = serializers.InventoryByLocationSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["variant", "location"]
    search_fields = ["variant__option_label", "variant__product__title", "location__name"]

# -------- Orders / Payments --------
class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.select_related("buyer_contact").prefetch_related("items").all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["status", "channel", "buyer_contact"]
    search_fields = ["id"]
    ordering_fields = ["created_at", "total_cents"]

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = models.OrderItem.objects.select_related("order", "variant", "variant__product").all()
    serializer_class = serializers.OrderItemSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["order", "variant"]
    search_fields = ["order__id", "variant__option_label"]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = models.Payment.objects.select_related("order").all()
    serializer_class = serializers.PaymentSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["method", "order"]
    search_fields = ["order__id"]

# -------- COAs --------
class CoaCertificateViewSet(viewsets.ModelViewSet):
    queryset = models.CoaCertificate.objects.select_related("product", "variant", "purchaser_contact").all()
    serializer_class = serializers.CoaCertificateSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["product", "variant", "purchaser_contact"]
    search_fields = ["serial_no", "product__title", "variant__option_label"]

# -------- Consignments --------
class ConsignmentViewSet(viewsets.ModelViewSet):
    queryset = models.Consignment.objects.select_related("gallery_contact").prefetch_related("items").all()
    serializer_class = serializers.ConsignmentSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["gallery_contact", "start_date"]
    search_fields = ["gallery_contact__name"]

class ConsignmentItemViewSet(viewsets.ModelViewSet):
    queryset = models.ConsignmentItem.objects.select_related("consignment", "variant", "variant__product").all()
    serializer_class = serializers.ConsignmentItemSerializer
    permission_classes = [DefaultPerms]
    filterset_fields = ["consignment", "variant"]
    search_fields = ["consignment__id", "variant__option_label", "variant__product__title"]
