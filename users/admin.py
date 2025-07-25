from django.contrib import admin
from .models import Profile
from ai.models import EventSuggestion
from activities.models import Activity
from applications.models import Application, QuestionList

# Register your models here.
admin.site.register(Profile)
admin.site.register(EventSuggestion)
admin.site.register(Activity)
admin.site.register(Application)
admin.site.register(QuestionList)
