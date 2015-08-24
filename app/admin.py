from django.contrib import admin
from .models import (
    AccessToken, Person, Followees, Table
)

# Register your models here.
admin.site.register(AccessToken)
admin.site.register(Person)
admin.site.register(Followees)
admin.site.register(Table)
