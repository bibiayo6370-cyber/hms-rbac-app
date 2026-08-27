from rest_framework import serializers
from .models import Encounter, Diagnosis, Allergy, Observation, Appointment


class EncounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encounter
        fields = [
            "id", "patient", "provider", "department", "status",
            "chief_complaint", "examination_findings", "treatment_plan",
            "started_at", "completed_at",
        ]
        read_only_fields = ["id", "started_at"]


class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = ["id", "encounter", "description", "icd10_code", "is_primary", "diagnosed_at"]
        read_only_fields = ["id", "diagnosed_at"]


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ["id", "patient", "substance", "reaction", "severity", "recorded_at"]
        read_only_fields = ["id", "recorded_at"]


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = [
            "id", "encounter", "recorded_by", "temperature_c",
            "blood_pressure_systolic", "blood_pressure_diastolic",
            "pulse_rate", "respiratory_rate", "weight_kg", "recorded_at",
        ]
        read_only_fields = ["id", "recorded_by", "recorded_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["recorded_by"] = request.user
        return super().create(validated_data)


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["id", "patient", "provider", "department", "scheduled_for", "status", "notes"]
        read_only_fields = ["id"]
