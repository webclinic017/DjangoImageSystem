from django.urls import path, include
from core.models import ProductPicture, Product, Vendor
from rest_framework import routers, serializers, viewsets
from django_filters.rest_framework import DjangoFilterBackend


# Serializers define the API representation.
class VendorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vendor
        fields = ['url', 'id', 'name']


# Serializers define the API representation.
class ProductPictureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductPicture
        fields = ['url', 'id', 'picture_src', 'state', 'small', 'medium', 'large']


# Serializers define the API representation.
class ProductSerializer(serializers.HyperlinkedModelSerializer):

    pictures = ProductPictureSerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['url', 'id', 'product_hash', 'vendor', 'pictures']


# ViewSets define the view behavior.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-updated_at')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pictures__state']


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class ProductPictureViewSet(viewsets.ModelViewSet):
    queryset = ProductPicture.objects.all()
    serializer_class = ProductPictureSerializer