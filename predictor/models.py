from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from rdkit import Chem

LABEL_CHOICES = [
    (0, "0 - 비활성 / 저위험"),
    (1, "1 - 활성 / 고위험"),
]

class Molecule(models.Model):
    """
    Tox21 데이터를 저장하는 테이블.
    관리자 페이지에서는 name, smiles, NR-ER, SR-p53만 입력하고,
    canonical_smiles는 smiles로부터 자동 생성한다.
    """

    mol_id = models.CharField(max_length=100, blank=True, null=True)

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    smiles = models.TextField()

    canonical_smiles = models.TextField(
        unique=True,
        editable=False
    )

    nr_er = models.IntegerField(
        "NR-ER",
        choices=LABEL_CHOICES,
        null=True,
        blank=True
    )

    sr_p53 = models.IntegerField(
        "SR-p53",
        choices=LABEL_CHOICES,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.smiles:
            raise ValidationError({
                "smiles": "SMILES를 입력해야 합니다."
            })

        mol = Chem.MolFromSmiles(self.smiles)

        if mol is None:
            raise ValidationError({
                "smiles": "유효하지 않은 SMILES입니다."
            })

        if self.nr_er not in [0, 1, None]:
            raise ValidationError({
                "nr_er": "NR-ER 값은 0, 1 또는 빈 값이어야 합니다."
            })

        if self.sr_p53 not in [0, 1, None]:
            raise ValidationError({
                "sr_p53": "SR-p53 값은 0, 1 또는 빈 값이어야 합니다."
            })

    def save(self, *args, **kwargs):
        mol = Chem.MolFromSmiles(self.smiles)

        if mol is not None:
            self.canonical_smiles = Chem.MolToSmiles(
                mol,
                canonical=True
            )

        super().save(*args, **kwargs)

    def __str__(self):
        if self.name:
            return self.name

        return self.canonical_smiles[:80]

    def clean(self):
        """
        관리자 페이지에서 저장하기 전에 SMILES 유효성 검사.
        """

        if not self.smiles:
            raise ValidationError({
                "smiles": "SMILES를 입력해야 합니다."
            })

        mol = Chem.MolFromSmiles(self.smiles)

        if mol is None:
            raise ValidationError({
                "smiles": "유효하지 않은 SMILES입니다."
            })

        if self.nr_er not in [0, 1, None]:
            raise ValidationError({
                "nr_er": "NR-ER 값은 0 또는 1이어야 합니다."
            })

        if self.sr_p53 not in [0, 1, None]:
            raise ValidationError({
                "sr_p53": "SR-p53 값은 0 또는 1이어야 합니다."
            })

    def save(self, *args, **kwargs):
        """
        저장할 때 canonical_smiles 자동 생성.
        """

        mol = Chem.MolFromSmiles(self.smiles)

        if mol is not None:
            self.canonical_smiles = Chem.MolToSmiles(
                mol,
                canonical=True
            )

        super().save(*args, **kwargs)

    def __str__(self):
        if self.name:
            return self.name

        return self.canonical_smiles[:80]

    @property
    def compound_name(self):
        if self.name:
            return self.name
        return "명칭 정보 없음"

    @compound_name.setter
    def compound_name(self, value):
        self.name = value

    @property
    def nr_er_true(self):
        return self.nr_er

    @property
    def sr_p53_true(self):
        return self.sr_p53

    def __str__(self):
        return self.name or self.canonical_smiles or self.smiles
class AnalysisJob(models.Model):
    """
    CSV 파일 업로드 1번을 하나의 작업으로 저장.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    file_name = models.CharField(max_length=255)
    total_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} - {self.created_at}"


class AnalysisResult(models.Model):
    """
    CSV 안의 각 화합물별 분석 결과.
    smiles 입력 또는 name 입력 결과를 저장한다.
    """

    job = models.ForeignKey(
        AnalysisJob,
        on_delete=models.CASCADE,
        related_name="results"
    )

    row_number = models.IntegerField()

    # 입력 정보
    input_smiles = models.TextField(blank=True, null=True)
    input_name = models.CharField(max_length=255, blank=True, null=True)
    input_type = models.CharField(max_length=20, blank=True, null=True)
    resolved_name = models.CharField(max_length=255, blank=True, null=True)
    # SMILES, NAME, EMPTY

    canonical_smiles = models.TextField(null=True, blank=True)

    is_valid = models.BooleanField(default=True)

    # NR-ER 결과
    nr_er_source = models.CharField(max_length=20, default="-")
    # DB, ML, INVALID

    nr_er_result = models.IntegerField(null=True, blank=True)
    nr_er_prob = models.FloatField(null=True, blank=True)
    nr_er_threshold = models.FloatField(null=True, blank=True)
    nr_er_risk = models.CharField(max_length=20, default="-")

    # SR-p53 결과
    sr_p53_source = models.CharField(max_length=20, default="-")
    # DB, ML, INVALID

    sr_p53_result = models.IntegerField(null=True, blank=True)
    sr_p53_prob = models.FloatField(null=True, blank=True)
    sr_p53_threshold = models.FloatField(null=True, blank=True)
    sr_p53_risk = models.CharField(max_length=20, default="-")

    message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["row_number"]

    def __str__(self):
        if self.input_name:
            return f"{self.row_number}: {self.input_name}"

        if self.input_smiles:
            return f"{self.row_number}: {self.input_smiles[:50]}"

        return f"{self.row_number}: 입력 없음"
    