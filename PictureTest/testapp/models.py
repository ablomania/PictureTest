from django.db import models

# Create your models here    

class Page(models.Model):
    viewed = models.BooleanField(default=False)
    test = models.ForeignKey("Test", on_delete=models.CASCADE, null=True)
    page_number = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"Page {self.page_number} for {self.test.name}"


class Question(models.Model):
    text = models.TextField(null=True)
    number = models.IntegerField(null=True)
    page = models.ForeignKey('Page', on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)

class SubQuestion(models.Model):
    text = models.TextField(null=True)
    number = models.IntegerField(null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)


class Instruction(models.Model):
    body = models.TextField(null=True)
    header = models.TextField(null=True)
    footer = models.TextField(null=True)
    test = models.ForeignKey("Test", on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True) 


class Images(models.Model):
    image = models.ImageField(upload_to="test/images", null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)



class Test(models.Model):
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    timer_count = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    page_count = models.IntegerField(null=True)
    time_per_page = models.BooleanField(default=False)
    password = models.CharField(max_length=255, null=True)
    def __str__(self):
        return self.name