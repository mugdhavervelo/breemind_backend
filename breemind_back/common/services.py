from typing import Any
from typing import TypeVar

from django.db import models

Model = TypeVar("Model", bound=models.Model)


def model_update(
    *,
    instance: Model,
    fields: list[str],
    data: dict[str, Any],
) -> tuple[Model, bool]:
    """
    Generic update service for any model.
    """
    has_updated = False
    updated_fields = []

    for field in fields:
        if field not in data:
            continue

        field_value = data[field]
        field_old_value = getattr(instance, field)

        if field_old_value != field_value:
            has_updated = True
            setattr(instance, field, field_value)
            updated_fields.append(field)

    if has_updated:
        instance.full_clean()
        instance.save(update_fields=updated_fields)

    return instance, has_updated
