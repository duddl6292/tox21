from django.db import models
from predictor.models import Molecule


class Tox21Chemical(Molecule):
    class Meta:
        proxy = True
        verbose_name = "화학물질"
        verbose_name_plural = "화학물질"
        
class Chemical(models.Model):

    name = models.CharField("name(화학물질명)", max_length=100)

    smiles = models.TextField("SMILES")

    nr_er = models.CharField(
        "NR-ER",
        max_length=20,
        blank=True
    )

    sr_p53 = models.CharField(
        "SR-p53",
        max_length=20,
        blank=True
    )

    created_at = models.DateTimeField(
        "등록일",
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "화학물질"
        verbose_name_plural = "화학물질"