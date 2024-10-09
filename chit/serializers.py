from django.contrib.auth import authenticate
from django.db.models import Max
from rest_framework import serializers
from .models import *


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    conf_password = serializers.CharField(write_only=True, min_length=8, required=True)



class PaymentSerializer(serializers.ModelSerializer):
    chit_plan_id = serializers.IntegerField(source='chit_plan.id')

    class Meta:
        model = Payment
        fields = ['chit_plan_id', 'installment_number', 'amount_paid', 'status']



class ChitPlanSerializer(serializers.ModelSerializer):
    chit_id = serializers.IntegerField(source='id')
    
    class Meta:
        model = ChitPlan
        fields = ['plan', 'chit_id']


class InstallmentSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = User
        fields = ['total_amount_paid','total_pending_amount','installment_number','missed_months']





class UserSerializer(serializers.ModelSerializer):
    chit_plan = ChitPlanSerializer()
    installment_number = serializers.SerializerMethodField()  # Use SerializerMethodField

    class Meta:
        model = User
        fields = [
            'username', 'date_joined', 'months_paid', 'pending_amount', 
            'total_amount_paid', 'total_pending_amount','installment_number', 'missed_months', 'chit_plan'
        ]

    def get_installment_number(self, obj):
        """Fetch the latest installment number from the user's payments."""
        latest_payment = Payment.objects.filter(user=obj).order_by('-installment_number').first()
        return latest_payment.installment_number if latest_payment else None



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
