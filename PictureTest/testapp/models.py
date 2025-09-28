from django.db import models

# Create your models here.

class TestType(models.Model):
    class TimeUnit(models.TextChoices):
        Seconds = "Seconds", "seconds"
        Minutes = "Minutes", "minutes"
        Hours = "Hours", "hours"
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    timer_count = models.IntegerField(null=True)
    time_per_page = models.BooleanField(default=False)
    page_count = models.IntegerField(null=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    unit = models.CharField(max_length=10, choices=TimeUnit.choices, default=TimeUnit.Seconds)

    def __str__(self):
        return self.name
    

class Page(models.Model):
    image = models.ImageField(upload_to="test/images", null=True)
    question = models.TextField(null=True)
    viewed = models.BooleanField(default=False)
    test = models.ForeignKey("Test", on_delete=models.CASCADE, null=True)
    page_number = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"Page {self.page_number} for {self.test.name}"
    

class Test(models.Model):
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    test_type = models.ForeignKey("TestType", on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name