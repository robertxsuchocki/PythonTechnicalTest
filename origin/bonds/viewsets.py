import django_filters.rest_framework
import requests
from rest_framework import viewsets, mixins, serializers

from bonds.models import Bond
from bonds.serializers import BondSerializer


class BondViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for Bond model. Allows to create single bond and list already saved bonds

    Every queryset is filtered by authenticated user, perform_create adds information about user creating this object
    and additional data retrieved from external API
    """

    queryset = Bond.objects.all()
    serializer_class = BondSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('isin', 'size', 'currency', 'maturity', 'lei', 'legal_name')

    @classmethod
    def get_legal_name_from_api(cls, lei):
        """
        Makes a GET request to receive legal name of the entity

        :param lei: Legal Entity Identifier, used with API to receive additional data
        :return: legal name field if API data was received, None otherwise
        """
        response = requests.get(f'https://leilookup.gleif.org/api/v2/leirecords?lei={lei}').json()
        return response[0]['Entity']['LegalName']['$'] if response else None

    def get_queryset(self):
        """
        Overridden get_queryset method that filters out objects not belonging to user

        :return: queryset with user's objects
        """
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Receives data about legal name, passes it with user to a new object
        """
        legal_name = self.get_legal_name_from_api(serializer.validated_data['lei'])
        if legal_name is None:
            raise serializers.ValidationError('Entity with provided LEI does not exist')
        serializer.save(user=self.request.user, legal_name=legal_name.replace(' ', ''))
