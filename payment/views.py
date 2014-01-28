from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions

from payment.models import Charge
from payment.serializers import ChargeSerializer
from payment.serializers import UserSerializer
from payment.permissions import IsAdminOrOwner
from payment.vad import PaymentFormManager


pm = PaymentFormManager()


class ChargeCreate(generics.CreateAPIView):
    queryset = Charge.objects.all()
    serializer_class = ChargeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def pre_save(self, charge, **kwargs):
        # Not used: self.kwargs['pos_key']
        charge.owner = self.request.user
        if (charge.used_instruments is not None) and (len(charge.used_instruments) > 0):
            charge.update_from_silent_form_submit(pm.make_silent_payment(charge))
            charge.update_from_payment(pm.request_payment_from_ws(charge), save=False)
        else:
            charge.update_from_form_submit(pm.submit_payment_form(charge))
            charge.update_from_context(pm.request_payment_context(charge))


class ChargeDetail(generics.RetrieveAPIView):
    queryset = Charge.objects.all()
    serializer_class = ChargeSerializer
    permission_classes = (IsAdminOrOwner,)

    def get_object(self, queryset=None):
        charge = generics.RetrieveAPIView.get_object(self, queryset)
        charge.update_from_payment(pm.request_payment_from_ws(charge))
        charge.update_from_context(pm.request_payment_context(charge))
        return charge


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer