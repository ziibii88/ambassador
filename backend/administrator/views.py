from logging import getLogger

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from common.serializers import UserSerializer, ProductSerializer, \
    LinkSerializer, OrderSerializer
from core.models import Product, Link, Order

logger = getLogger(__name__)


class AmbassadorsAPIView(APIView):
    def get(self, _):
        amb = get_user_model().objects.filter(is_ambassador=True)
        ser = UserSerializer(amb, many=True)

        return Response(ser.data)


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD view set for Product model and serializer"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # authentication_classes = ()  # check defaults in settings
    # permission_classes = ()  # check defaults in settings
    # filter_backends = ()  # check defaults in settings
    search_field = ('id', 'title')
    ordering_fields = ('id', 'title', 'price')
    ordering = 'id'

    def create(self, request, *args, **kwargs):
        """overriding to enable logging"""
        logger.debug(f"Creating product: {request.POST.get('title')}")
        response = super().create(request, *args, **kwargs)
        self.clear_cache()
        return response

    def retrieve(self, request, *args, **kwargs):
        """overriding to enable logging"""
        logger.debug(f"Retrieving product: {self.lookup_field}={kwargs[self.lookup_field]}")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """overriding to enable logging"""
        logger.debug(f"Updating product: {self.lookup_field}={kwargs[self.lookup_field]}")
        response = super().update(request, *args, **kwargs)
        self.clear_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        """overriding to enable logging"""
        logger.debug(f"Partial update: {self.lookup_field}={kwargs[self.lookup_field]}")
        response = super().partial_update(request, *args, **kwargs)
        self.clear_cache()
        return response

    def list(self, request, *args, **kwargs):
        """overriding to enable logging"""
        logger.debug("Listing products...")
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """overriding to enable logging"""
        logger.debug(f"Deleting product... {self.lookup_field}={kwargs[self.lookup_field]}")
        response = super().destroy(request, *args, **kwargs)
        self.clear_cache()
        return response

    @staticmethod
    def clear_cache():
        logger.debug("Clearing products cache...")
        cache.delete('products_backend')
        [cache.delete(k) for k in cache.keys('*') if 'products_frontend' in k]


class LinksAPIView(APIView):
    def get(self, request, pk=None):
        links = Link.objects.filter(pk=pk)
        ser = LinkSerializer(links, many=True)

        return Response(ser.data)


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD view set for Order model and serializer"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # authentication_classes = ()  # check defaults in settings
    # permission_classes = ()  # check defaults in settings
    # filter_backends = ()  # check defaults in settings
    search_field = ('id', 'trans_id', 'code', 'amb_email', 'email',
                    'first_name', 'last_name', 'city', 'country', 'zip')
    ordering_fields = ('id', 'trans_id', 'code', 'created_at', 'updated_at')
    ordering = 'id'
