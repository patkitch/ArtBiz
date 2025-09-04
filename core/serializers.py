from rest_framework import serializers
from . import models
from decimal import Decimal, InvalidOperation

# -------- Catalog --------
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = "__all__"


class ProductVariantSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    # Readable price (e.g., "19.99")
    price = serializers.SerializerMethodField(read_only=True)
    # Optional write-only field so clients can POST/PUT in dollars
    price_dollars = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = models.ProductVariant
        fields = "__all__"  # includes price_cents
        # or explicitly include: ["id","product","option_label","price_cents","price","price_dollars",...]

    def get_price(self, obj):
        return f"{obj.price:.2f}"

    def _assign_price_cents(self, attrs):
        """Allow clients to send price_dollars or price_cents."""
        pd = attrs.pop("price_dollars", None)
        if pd is not None:
            try:
                cents = int((Decimal(pd) * 100).quantize(Decimal("1")))
            except (InvalidOperation, ValueError):
                raise serializers.ValidationError({"price_dollars": "Invalid money amount"})
            attrs["price_cents"] = cents
        return attrs

    def create(self, validated_data):
        validated_data = self._assign_price_cents(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._assign_price_cents(validated_data)
        return super().update(instance, validated_data)

class MediaSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Media
        fields = "__all__"  # includes 'image'

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# -------- Contacts / CRM --------
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = "__all__"

class CrmNoteSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.name", read_only=True)
    class Meta:
        model = models.CrmNote
        fields = "__all__"

# -------- Locations / Inventory --------
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = "__all__"

class InventoryByLocationSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="variant.product.title", read_only=True)
    variant_label = serializers.CharField(source="variant.option_label", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)

    class Meta:
        model = models.InventoryByLocation
        fields = "__all__"

# -------- Orders / Payments --------
class OrderItemSerializer(serializers.ModelSerializer):
    variant_label = serializers.CharField(source="variant.option_label", read_only=True)
    product_title = serializers.CharField(source="variant.product.title", read_only=True)

    class Meta:
        model = models.OrderItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    buyer_name = serializers.CharField(source="buyer_contact.name", read_only=True)

    class Meta:
        model = models.Order
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)
    class Meta:
        model = models.Payment
        fields = "__all__"

# -------- COAs --------
class CoaCertificateSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    variant_label = serializers.CharField(source="variant.option_label", read_only=True)
    purchaser_name = serializers.CharField(source="purchaser_contact.name", read_only=True)

    class Meta:
        model = models.CoaCertificate
        fields = "__all__"

# -------- Consignments --------
class ConsignmentItemSerializer(serializers.ModelSerializer):
    variant_label = serializers.CharField(source="variant.option_label", read_only=True)
    product_title = serializers.CharField(source="variant.product.title", read_only=True)

    class Meta:
        model = models.ConsignmentItem
        fields = "__all__"

class ConsignmentSerializer(serializers.ModelSerializer):
    items = ConsignmentItemSerializer(many=True, read_only=True)
    gallery_name = serializers.CharField(source="gallery_contact.name", read_only=True)

    class Meta:
        model = models.Consignment
        fields = "__all__"
