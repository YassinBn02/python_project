from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import re

ROLE_CHOICES = (
    (0, 'Admin'),
    (1, 'Member'),
    (2,'Creator'),
    (3,'blocked'),
    (4,'pending_creator')
)

STATUS_CHOICES = (
    (0, 'Pending'),
    (1, 'Published'),
    (2, 'Blocked'),
)

class UserManager(models.Manager):
    def basic_validator(self,postData):
        errors={}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if len(postData['first-name'])<3:
            errors["first_name"]="first name should be at least 3 characters "
        if len(postData['last-name'])<3:
            errors["last_name"]="last name should be at least 3 characters "
        if not EMAIL_REGEX.match(postData['email']):
            errors['email']="invalid email address"
        if len(postData['birth'])<1:
            errors['birth']="please enter your bithdate!"
        if len(postData['password'])<7:
            errors["password"]="password should be at least 7 character"
        if postData['password']!=postData['confirm-password']:
            errors["confirm-password"]="confirm password have to match the passsword"
        return errors
        
class User(models.Model):
    first_name=models.CharField(max_length=45)
    last_name=models.CharField(max_length=45)
    email=models.EmailField(unique=True)
    birth=models.DateField()
    password=models.CharField(max_length=255)
    role=models.SmallIntegerField(choices=ROLE_CHOICES,default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=UserManager()

class Event(models.Model):
    title=models.CharField(max_length=200)
    location=models.CharField(max_length=200)
    start_date=models.DateField()
    end_date=models.DateField()
    description=models.TextField()
    image=models.ImageField(upload_to='event_images/')
    category=models.CharField(max_length=200)
    status=models.SmallIntegerField(choices=STATUS_CHOICES,default=0)
    total_number=models.IntegerField(validators=[MinValueValidator(1)])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    user=models.ForeignKey(User,related_name="owned_events",on_delete=models.CASCADE)
    members=models.ManyToManyField(User,related_name="joined_events",blank=True)
    favorites=models.ManyToManyField(User,related_name="favorited_events",blank=True)

class Comment(models.Model):
    event=models.ForeignKey(Event,related_name="comments",on_delete=models.CASCADE)
    user=models.ForeignKey(User,related_name="comments",on_delete=models.CASCADE)
    comment=models.TextField()
    rate=models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(10)])
    comment_status=models.SmallIntegerField(choices=STATUS_CHOICES,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

