from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Horse(models.Model):
    title = models.CharField(max_length=200)
    registered_name = models.CharField(max_length=200)
    age = models.IntegerField()
    sire = models.CharField(max_length=200)
    color = models.CharField(max_length=50)
    dam = models.CharField(max_length=100)
    height = models.CharField(max_length=100)
    sex = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='upload/featured')
    address = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    listed_on = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=100, default='Unpaid',
                                      choices=(('Paid', 'Paid'), ('Unpaid', 'Unpaid')))

    def __str__(self):
        return self.title.title()


class SliderImage(models.Model):
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE, related_name='SliderImages')
    image = models.ImageField(upload_to='upload/slider')

    def __str__(self):
        return self.horse.title.title()


class Message(models.Model):
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    message_text = models.TextField()
    message_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.horse.id)
