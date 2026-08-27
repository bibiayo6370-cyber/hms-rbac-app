from rest_framework import serializers
from .models import LaboratoryOrder, LaboratoryResult


class LaboratoryOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaboratoryOrder
        fields = ["id", "encounter", "ordered_by", "test_name", "loinc_code", "status", "ordered_at", "accepted_at"]
        read_only_fields = ["id", "ordered_by", "ordered_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["ordered_by"] = request.user
        return super().create(validated_data)


class LaboratoryResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaboratoryResult
        fields = [
            "id", "order", "performed_by", "result_value", "unit",
            "reference_range", "is_abnormal", "notes", "entered_at",
        ]
        read_only_fields = ["id", "performed_by", "entered_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["performed_by"] = request.user
        return super().create(validated_data)
