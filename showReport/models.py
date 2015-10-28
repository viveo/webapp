from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class AssetRating(models.Model):
    ip = models.GenericIPAddressField(blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
		
class ReportTable(models.Model):
    businessRisk = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    title = models.TextField()
    cveId = models.CharField(max_length=14)
    threat = models.TextField()
    impact = models.TextField()
    solution = models.TextField()
    severity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    assetInfo = models.ForeignKey(AssetRating)