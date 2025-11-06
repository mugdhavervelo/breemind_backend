from django.http import Http404
from django.shortcuts import get_object_or_404


def get_object(model_or_queryset, **kwargs):
    try:
        return get_object_or_404(model_or_queryset, **kwargs)
    except Http404:
        return None


def inline_serializer(many=False, fields=None):
    """inline serializer."""
    from rest_framework import serializers

    if fields is None:
        fields = {}

    class InlineSerializer(serializers.Serializer):
        pass

    for field_name, field_type in fields.items():
        setattr(InlineSerializer, field_name, field_type)

    return InlineSerializer(many=many)
