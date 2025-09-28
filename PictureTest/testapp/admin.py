from django.contrib import admin
from .models import Test, TestType, Page

# Register your models here.
admin.site.register(Test)
admin.site.register(TestType)
admin.site.register(Page)
