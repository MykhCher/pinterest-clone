from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Board(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board')
    title = models.CharField(max_length=250, unique=True)
    pins = models.ManyToManyField('pins.Pin', related_name='pins', blank=True)
    cover = models.ImageField(upload_to='boards', default='boards/default.png')
    is_private = models.BooleanField(default=False)
    description = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.title
