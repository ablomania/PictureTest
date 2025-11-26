from django.contrib import admin
from .models import Test, Page, SubQuestion, Images, Question, Instruction

# Register your models here.
admin.site.register(Test)
admin.site.register(Page)
admin.site.register(SubQuestion)
admin.site.register(Images)
admin.site.register(Question)
admin.site.register(Instruction)