from rest_framework import serializers
from .models import (
    weekly_flags,
    weekly_metrics,
    pre_mid_term,
    pre_end_term,
    risk_of_failing,
    pre_sem_watchlist,
)


class weekly_flagSerializer(serializers.ModelSerializer):
    class Meta:
        model = weekly_flags
        fields = '__all__'


class performanceSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = weekly_metrics
        fields = '__all__'


class PreMidTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = pre_mid_term
        fields = '__all__'


class PreEndTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = pre_end_term
        fields = '__all__'


class RiskOfFailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = risk_of_failing
        fields = '__all__'


class PreSemWatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = pre_sem_watchlist
        fields = '__all__'
