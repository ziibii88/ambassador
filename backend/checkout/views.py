from logging import getLogger

from django.db import transaction
from rest_framework import generics, exceptions

from common.serializers import OrderSerializer
from .serializers import LinkSerializer
from core.models import Link, Order

logger = getLogger(__name__)


class LinkRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    lookup_field = 'code'


class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            link = Link.objects.get(code=request.data.get('code'))
            request.data.update({
                'user_id': link.user.pk,
                'amb_email': link.user.email})
            return super().post(request, *args, **kwargs)
        except Link.DoesNotExist:
            raise exceptions.APIException('Invalid code!')
        except Exception as e:
            transaction.rollback()
            logger.error(e)
            raise exceptions.APIException('Something went wrong!')
