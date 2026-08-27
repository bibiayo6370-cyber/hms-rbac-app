from rest_framework import serializers
from .models import Patient, Provider


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    registered_by_name = serializers.CharField(source="registered_by.get_full_name", read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id", "patient_number", "first_name", "last_name", "date_of_birth",
            "age", "gender", "phone_number", "email", "address",
            "next_of_kin_name", "next_of_kin_phone",
            "registered_by", "registered_by_name", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "patient_number", "registered_by", "created_at", "updated_at"]

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - (
            (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
        )

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["registered_by"] = request.user
        return super().create(validated_data)


class ProviderSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Provider
        fields = ["id", "user", "full_name", "license_number", "specialty", "department"]
