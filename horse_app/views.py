# Create your views here.
import re

import stripe
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from horse_app.custom_permission import IsOwner
from horse_app.models import Horse, SliderImage, Message
from horse_app.serializer import HorseCreateSerializer, HorseViewSerializer, SliderSerializer, HorseSearchSerializer, \
    StripeSerializer, MessageSerializer
from horseworld.settings import STRIPE_API_KEY, STRIPE_PRICE_ID


class HorseAPIView(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin):
    queryset = Horse.objects.all()
    serializer_class = HorseViewSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        slider = re.search("^/api/horse/.*/sliders/$", self.request.path)
        message = re.search("^/api/horse/.*/message/$", self.request.path)
        if self.action in ['create', 'update']:
            if slider:
                return SliderSerializer
            if message:
                return MessageSerializer
            return HorseCreateSerializer
        else:
            if slider:
                return SliderSerializer
            if message:
                return MessageSerializer
            return HorseViewSerializer

    def get_queryset(self):
        return self.queryset.filter(payment_status='Paid')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], serializer_class=SliderSerializer)
    def sliders(self, request, pk):
        if self.request.method == 'GET':
            sliders = SliderImage.objects.filter(horse_id=pk)
            return Response(SliderSerializer(sliders, many=True, context={'request': request}).data)
        elif self.request.method == 'POST':
            images = dict((request.data).lists())['image']
            flag = 1
            arr = []
            for img in images:
                modified_data = self.modify_input_for_multiple_files(img)
                file_serializer = self.serializer_class(data=modified_data)
                if file_serializer.is_valid():
                    file_serializer.save(horse_id=pk)
                    arr.append(file_serializer.data.get('image'))
                else:
                    flag = 0

            if flag == 1:
                return Response({'horse': pk, 'image': arr})
            else:
                return Response(arr, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'delete'], url_path='slider/(?P<pk2>[^/.]+)',
            serializer_class=SliderSerializer)
    def slider(self, request, pk, pk2):
        if self.request.method == 'GET':
            try:
                sliders = SliderImage.objects.get(horse_id=pk, id=pk2)
                return Response(SliderSerializer(sliders, many=False, context={'request': request}).data)
            except:
                return Response({'status': 'No image found found'}, status.HTTP_404_NOT_FOUND)
        elif self.request.method == 'DELETE':
            try:
                slider = SliderImage.objects.get(horse_id=pk, id=pk2)
                slider.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({'status': 'No image found found'}, status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get', 'post'], serializer_class=MessageSerializer)
    def message(self, request, pk):
        if self.request.method == 'GET':
            try:
                Horse.objects.get(id=pk)
            except:
                return Response({'error': 'No product found for id '+pk}, status.HTTP_404_NOT_FOUND)
            messages = Message.objects.filter(horse_id=pk)
            return Response(MessageSerializer(messages, many=True).data)
        elif self.request.method == 'POST':
            try:
                Horse.objects.get(id=pk)
            except:
                return Response({'error': 'No product found for id '+pk}, status.HTTP_404_NOT_FOUND)
            serializer = MessageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(horse_id=pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def modify_input_for_multiple_files(self, img):
        dict = {}
        dict['image'] = img
        return dict

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []

        return super().get_parsers()


class HorseSearchAPIView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin):
    serializer_class = HorseSearchSerializer
    queryset = Horse.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = Horse.objects.filter(payment_status='Paid')
        if self.request.GET.get('age'):
            queryset = queryset.filter(age__lte=self.request.GET.get('age'))
        if self.request.GET.get('price'):
            queryset = queryset.filter(price__lte=self.request.GET.get('price'))
        if self.request.GET.get('listed_date'):
            queryset = queryset.filter(listed_on__lte=self.request.GET.get('listed_date'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


stripe.api_key = STRIPE_API_KEY


class StripeSubscriptionAPIView(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin):
    authentication_classes = []
    permission_classes = []
    serializer_class = StripeSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        email = data['email']
        payment_method_id = data['payment_method_id']
        extra_msg = ''
        customer_data = stripe.Customer.list(email=email).data
        if len(customer_data) == 0:
            # creating customer
            try:
                customer = stripe.Customer.create(
                    email=email,
                    payment_method=payment_method_id,
                    invoice_settings={
                        'default_payment_method': payment_method_id
                    }
                )
            except:
                return Response({'error': 'Invalid payment information'}, status.HTTP_400_BAD_REQUEST)
        else:
            customer = customer_data[0]
            extra_msg = "Customer already existed."
        stripe.Subscription.create(
            customer=customer,
            items=[
                {
                    'price': STRIPE_PRICE_ID
                }
            ]
        )
        product = Horse.objects.get(id=data['product_id'])
        product.payment_status = 'Paid'
        product.save()
        res = {'message': 'Success', 'data': {'customer_id': customer.id, 'extra_msg': extra_msg}}
        return Response(status=status.HTTP_200_OK, data=res)
