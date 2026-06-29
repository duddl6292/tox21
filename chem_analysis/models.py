from django.db import models

class MoleculeMaster(models.Model):
    # 표준화된 SMILES 구조식
    canonical_smiles = models.CharField(max_length=500, unique=True, db_index=True)
    
    # 화합물 이름 ('ch' 등 부분 검색을 위해 사용)
    compound_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    # 실제 정답값 (나중에 머신러닝 결과와 비교할 때 사용)
    nr_er_true = models.IntegerField(null=True, blank=True)
    sr_p53_true = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'molecule_master'

    def __str__(self):
        return self.compound_name if self.compound_name else self.canonical_smiles