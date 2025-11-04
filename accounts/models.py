from django.contrib.auth.models import User
from django.db import models

User.add_to_class('phone', models.CharField(max_length=15, blank=True))
User.add_to_class('address', models.TextField(blank=True))
