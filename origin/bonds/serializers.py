from rest_framework import serializers

from bonds.models import Bond


class BondSerializer(serializers.ModelSerializer):
    """
    Bond serializer

    Enables all fields except user (not necessary)
    + makes legal_name read only as data is received from external API
    """

    class Meta:
        model = Bond
        fields = ('isin', 'size', 'currency', 'maturity', 'lei', 'legal_name')
        read_only_fields = ('legal_name',)
