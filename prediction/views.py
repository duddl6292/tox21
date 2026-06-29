import io
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from predictor.models import Molecule
from prediction.utils.pubchem_utils import get_smiles_from_pubchem_name, get_name_from_pubchem_smiles
from rdkit import Chem
from rdkit.Chem import Draw, AllChem

def search_engine_view(request):
    """
    최적화 버전 검색 엔진 (페이징 + 실시간 PubChem 명칭 보완 + 에러 출력 방어)
    """
    query = request.GET.get('query', '').strip()
    search_mode = None
    error_message = None
    page_obj = None

    if query:
        # 1. 로컬 DB에서 조건에 맞는 데이터 전체 조회
        raw_results = Molecule.objects.filter(
            Q(mol_id__icontains=query) |
            Q(name__icontains=query) |
            Q(smiles__icontains=query) |
            Q(canonical_smiles__icontains=query)
        ).order_by("id")
        
        if raw_results.exists():
            search_mode = "로컬 Tox21 DB"
            paginator = Paginator(raw_results, 10)
            page_number = request.GET.get('page', 1)
            
            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
                
            for mol in page_obj:
                if not mol.name:
                    fetched_name, _ = get_name_from_pubchem_smiles(mol.canonical_smiles)

                    if fetched_name:
                        mol.name = fetched_name
                        mol.save(update_fields=["name"])
                    else:
                        mol.name = "명칭 정보 없음"
                        
        else:
            # 2. 로컬 DB에 없으면 외부 PubChem 명칭으로 역조회
            smiles, error = get_smiles_from_pubchem_name(query)
            if smiles:
                search_mode = "PubChem API"
                page_obj = [{
                    'compound_name': query,
                    'canonical_smiles': smiles,
                    'nr_er_true': '-',
                    'sr_p53_true': '-',
                }]
                # 💡 [핵심 수정] 데이터를 성공적으로 찾았으면 에러 메시지를 확실히 없앱니다.
                error_message = None 
            else:
                # 💡 데이터를 못 찾았을 때만 에러 문구를 띄우고 표(page_obj)를 비웁니다.
                error_message = f"'{query}'에 대한 데이터를 찾을 수 없습니다."
                page_obj = None

    return render(request, 'prediction/search_results.html', {
        'query': query,
        'page_obj': page_obj,
        'search_mode': search_mode,
        'error_message': error_message
    })


def molecule_visualize_view(request):
    """
    기획서: SMILES를 넣으면 분자 모형을 3D, 2D로 보여주는 페이지
    (이 함수가 지워져서 에러가 났던 것입니다!)
    """
    smiles = request.GET.get('smiles', '').strip()
    context = {'smiles': smiles, 'sdf_block': None, 'error': None}
    
    if smiles:
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                context['error'] = '유효하지 않은 SMILES 구조식입니다.'
            else:
                # 3D 렌더링을 위해 수소 추가 및 3D 좌표 임베딩 수행
                mol_3d = Chem.AddHs(mol)
                AllChem.EmbedMolecule(mol_3d, AllChem.ETKDG())
                AllChem.MMFFOptimizeMolecule(mol_3d)
                
                # 프론트엔드(3Dmol.js)로 넘길 SDF 문자열 생성
                context['sdf_block'] = Chem.MolToMolBlock(mol_3d)
        except Exception as e:
            context['error'] = f'구조 처리 중 오류가 발생했습니다: {str(e)}'
            
    return render(request, 'prediction/molecule_view.html', context)


def download_2d_image(request):
    """
    기획서: 2D 이미지를 PNG나 JPG로 다운로드하는 기능
    """
    smiles = request.GET.get('smiles', '').strip()
    fmt = request.GET.get('format', 'png').lower()
    
    if not smiles:
        return HttpResponse("SMILES를 지정해주세요.", status=400)
        
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return HttpResponse("유효하지 않은 SMILES입니다.", status=400)
    
    # RDKit으로 이미지 드로잉
    img = Draw.MolToImage(mol, size=(600, 600))
    buffer = io.BytesIO()
    img_format = 'JPEG' if fmt == 'jpg' else 'PNG'
    img.save(buffer, format=img_format)
    
    content_type = 'image/jpeg' if fmt == 'jpg' else 'image/png'
    response = HttpResponse(buffer.getvalue(), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="molecule_2d.{fmt}"'
    return response