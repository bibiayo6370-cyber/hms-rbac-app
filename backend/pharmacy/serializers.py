from rest_framework import serializers
from .models import Medication, Prescription, DispensingRecord


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ["id", "name", "strength", "form", "unit_price", "stock_quantity"]
        read_only_fields = ["id"]


class PrescriptionSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source="medication.name", read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id", "encounter", "medication", "medication_name", "prescribed_by",
            "dosage_instructions", "quantity", "status", "prescribed_at",
        ]
        read_only_fields = ["id", "prescribed_by", "prescribed_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["prescribed_by"] = request.user
        return super().create(validated_data)


class DispensingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispensingRecord
        fields = ["id", "prescription", "dispensed_by", "quantity_dispensed", "dispensed_at", "notes"]
        read_only_fields = ["id", "dispensed_by", "dispensed_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["dispensed_by"] = request.user
        return super().create(validated_data)
