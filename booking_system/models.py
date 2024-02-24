from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length = 50)
    email = models.EmailField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        
class Train(models.Model):
    type = models.CharField(max_length = 100)
    name = models.CharField(max_length = 100)
    way = models.CharField(max_length = 200)
    departure = models.CharField(max_length = 30)
    
    def __str__(self):
        return f'Користувач: {self.name} Тип потягу: {self.type}  Шлях: {self.way} Відправка: {self.departure
    }'
    
    class Meta:
        unique_together = (('name','type','way'),)
        
        
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    date = models.DateField()
    
    def __str__(self):
        return f'Користувач: {self.user} Потяг: {self.train} Дата: {self.date}'
    
    