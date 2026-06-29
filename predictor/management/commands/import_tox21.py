import pandas as pd

from django.core.management.base import BaseCommand

from rdkit import Chem

from predictor.models import Molecule


class Command(BaseCommand):
    help = "Import Tox21 CSV data into Molecule table"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path to tox21.csv"
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        df = pd.read_csv(csv_path, encoding="utf-8-sig")

        # name은 없어도 됨
        required_columns = [
            "smiles",
            "NR-ER",
            "SR-p53",
        ]

        for column in required_columns:
            if column not in df.columns:
                raise ValueError(
                    f"{column} 컬럼이 CSV에 없습니다."
                )

        use_columns = [
            "smiles",
            "NR-ER",
            "SR-p53",
        ]

        if "name" in df.columns:
            use_columns.insert(0, "name")

        if "mol_id" in df.columns:
            use_columns.insert(0, "mol_id")

        df = df[use_columns].copy()

        # name 컬럼 없으면 빈 문자열로 생성
        if "name" not in df.columns:
            df["name"] = ""

        # mol_id 컬럼 없으면 None으로 생성
        if "mol_id" not in df.columns:
            df["mol_id"] = None

        # smiles 정리
        df = df.dropna(subset=["smiles"]).copy()
        df["smiles"] = df["smiles"].astype(str).str.strip()
        df = df[df["smiles"] != ""].copy()

        # name 정리
        df["name"] = df["name"].fillna("").astype(str).str.strip()

        def to_canonical(smiles):
            mol = Chem.MolFromSmiles(smiles)

            if mol is None:
                return None

            return Chem.MolToSmiles(
                mol,
                canonical=True
            )

        df["canonical_smiles"] = df["smiles"].apply(to_canonical)
        df = df.dropna(subset=["canonical_smiles"]).copy()

        def clean_label(value):
            if pd.isna(value):
                return None

            value = str(value).strip()

            if value == "":
                return None

            try:
                value = int(float(value))
            except ValueError:
                return None

            if value in [0, 1]:
                return value

            return None

        df["NR-ER"] = df["NR-ER"].apply(clean_label)
        df["SR-p53"] = df["SR-p53"].apply(clean_label)

        created_count = 0
        updated_count = 0
        skipped_conflict_count = 0

        for canonical_smiles, group in df.groupby("canonical_smiles"):
            first_row = group.iloc[0]

            def resolve_label(target_col):
                labels = (
                    group[target_col]
                    .dropna()
                    .unique()
                    .tolist()
                )

                # 라벨이 하나면 사용
                if len(labels) == 1:
                    return int(labels[0])

                # 라벨이 없거나 충돌하면 None
                return None

            nr_er = resolve_label("NR-ER")
            sr_p53 = resolve_label("SR-p53")

            # name은 같은 canonical_smiles 그룹 안에서 가장 먼저 있는 값 사용
            name_list = (
                group["name"]
                .dropna()
                .astype(str)
                .str.strip()
            )
            name_list = name_list[name_list != ""].tolist()

            if len(name_list) > 0:
                name = name_list[0]
            else:
                name = ""

            obj, created = Molecule.objects.update_or_create(
                canonical_smiles=canonical_smiles,
                defaults={
                    "mol_id": first_row["mol_id"],
                    "name": name,
                    "smiles": first_row["smiles"],
                    "nr_er": nr_er,
                    "sr_p53": sr_p53,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Created: {created_count}, Updated: {updated_count}, Skipped conflicts: {skipped_conflict_count}"
            )
        )