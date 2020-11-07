import django_filters.rest_framework
from rest_framework import viewsets, mixins

from bonds.models import Bond
from bonds.serializers import BondSerializer


class BondViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Bond.objects.all()
    serializer_class = BondSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('isin', 'size', 'currency', 'maturity', 'lei')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
