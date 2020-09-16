from django_filters import rest_framework as filters
from item.models import ItemHistory


class ItemHistoryFilter(filters.FilterSet):
    start_date = filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = ItemHistory
        fields = ['created_at']
        