from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Appointment(models.Model):
    """
    Represents a single appointment booking
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    # Link to Django's built-in User model
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    
    # Appointment details
    name = models.CharField(max_length=100)
    age = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Automatic timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-time']  # Most recent first
        
    def __str__(self):
        return f"{self.name} - {self.date} at {self.time}"