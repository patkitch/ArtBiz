from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import (
    ProductViewSet, ProductVariantViewSet, MediaViewSet,
    ContactViewSet, CrmNoteViewSet,
    LocationViewSet, InventoryByLocationViewSet,
    OrderViewSet, OrderItemViewSet, PaymentViewSet,
    CoaCertificateViewSet,
    ConsignmentViewSet, ConsignmentItemViewSet,
)

router = DefaultRouter()
# Catalog
router.register(r"products", ProductViewSet)
router.register(r"variants", ProductVariantViewSet)
router.register(r"media", MediaViewSet)
# Contacts / CRM
router.register(r"contacts", ContactViewSet)
router.register(r"crm-notes", CrmNoteViewSet)
# Locations / Inventory
router.register(r"locations", LocationViewSet)
router.register(r"inventory", InventoryByLocationViewSet)
# Orders / Payments
router.register(r"orders", OrderViewSet)
router.register(r"order-items", OrderItemViewSet)
router.register(r"payments", PaymentViewSet)
# COAs
router.register(r"coas", CoaCertificateViewSet)
# Consignments
router.register(r"consignments", ConsignmentViewSet)
router.register(r"consignment-items", ConsignmentItemViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
