from rest_framework import serializers
from .models import Invoice, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "invoice", "amount", "method", "received_by", "paid_at", "reference"]
        read_only_fields = ["id", "received_by", "paid_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["received_by"] = request.user
        return super().create(validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_paid = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id", "invoice_number", "patient", "encounter",
            "consultation_fee", "laboratory_charges", "pharmacy_charges", "other_charges",
            "total_amount", "amount_paid", "balance_due",
            "status", "created_by", "created_at", "payments",
        ]
        read_only_fields = ["id", "invoice_number", "created_by", "created_at"]

    def get_amount_paid(self, obj):
        return obj.amount_paid

    def get_balance_due(self, obj):
        return obj.balance_due

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)
