from django.db import models

# Create your models here.



class Employer(models.Model):
    FilteringTermSynonym = models.ManyToManyField(AcademicDegree)