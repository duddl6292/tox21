from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
import requests
from django.http import HttpResponse
from html import escape
import re

from chemicals.models import (
    Chemical,
    ChemicalCategory,
    ToxicityEndpoint,
    CSVUploadHistory,
    PredictionHistory,
    DatasetVersion,
    Notice,
    ChemicalNews,
    Inquiry,
)

def get_json_or_empty(response):
    try:
        return response.json()
    except Exception:
        print("JSON 변환 실패")
        print("status:", response.status_code)
        print("content-type:", response.headers.get("Content-Type"))
        print(response.text[:500])
        return {}

# HTML 태그 제거용 함수 ###############################################################
def remove_html_tags(text):
    if text is None:
        return ""
    clean_text = re.sub("<.*?>", "", text)
    clean_text = clean_text.replace("&nbsp;", " ")
    clean_text = clean_text.replace("&middot;", "·")
    clean_text = clean_text.replace("&#xFF65;", "·")
    return clean_text.strip()


# 최신뉴스 TOP5#########################################################################
def home(request):
    domestic_news = []
    overseas_news = []
    policy_data = []
    press_data = []

    # 국내/해외 뉴스 API ################################################################
    news_api_url = "https://kpis.krict.re.kr/portal/news/selectNewsPrtlList.do"

    news_base_params = {
        "srchDtlCd": "01",
        "srchBgngYmd": "",
        "srchRlsYn": "Y",
        "menuNo": "",
        "mngNo": "",
        "srchGbnSub": "00",
        "srchCd": "",
        "page": "1",
        "listSize": "5",
        "srchWordSub": "",
        "srchWrd": "",
    }

    news_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://kpis.krict.re.kr/portal/news/newsPrtlList.do",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    # 국내뉴스 TOP5
    domestic_params = news_base_params.copy()
    domestic_params["srchCntnsClsfCd"] = "03"

    domestic_response = requests.post(news_api_url, data=domestic_params, headers=news_headers)
    domestic_response.encoding = "utf-8"
    domestic_news = domestic_response.json().get("newsMngVOList", [])

    # 해외뉴스 TOP5
    overseas_params = news_base_params.copy()
    overseas_params["srchCntnsClsfCd"] = "04"

    overseas_response = requests.post(news_api_url, data=overseas_params, headers=news_headers)
    overseas_response.encoding = "utf-8"
    overseas_news = overseas_response.json().get("newsMngVOList", [])

    # ############################### 부처별 자료 정책자료 TOP3 ###############################
    policy_api_url = "https://kpis.krict.re.kr/portal/policy/selectPolicyNewsPrtlList.do"

    policy_params = {
        "menuNo": "020100",
        "mngNo": "",
        "page": "1",
        "srchRlsYn": "Y",
        "srchGbnSub": "00",
        "srchWordSub": "",
        "srchCd": "",
        "srchWrd": "",
        "srchRegFromDt": "",
        "listSize": "3",
    }

    policy_response = requests.post(policy_api_url, data=policy_params, headers={
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://kpis.krict.re.kr",
        "Referer": "https://kpis.krict.re.kr/portal/policy/policyNewsPrtlList.do",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    })
    policy_response.encoding = "utf-8"
    policy_data = get_json_or_empty(policy_response).get("policyNewsVOList", [])


    # ############################### 부처별 자료 보도자료 TOP3 ###############################
    press_api_url = "https://kpis.krict.re.kr/portal/nscvrg/selectNscvrgPrtList.do"

    press_params = {
        "menuNo": "020200",
        "mngNo": "",
        "page": "1",
        "srchRlsYn": "Y",
        "srchGbnSub": "00",
        "srchWordSub": "",
        "srchCd": "",
        "srchWrd": "",
        "srchRegFromDt": "",
        "listSize": "3",
    }

    press_response = requests.post(press_api_url, data=press_params, headers={
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://kpis.krict.re.kr",
        "Referer": "https://kpis.krict.re.kr/portal/nscvrg/nscvrgPrtlList.do",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    })
    press_response.encoding = "utf-8"
    press_data = get_json_or_empty(press_response).get("nscvrgMngVOList", [])

    return render(request, "home.html", {
        "domestic_news": domestic_news,
        "overseas_news": overseas_news,
        "policy_data": policy_data,
        "press_data": press_data,
    })

# ########################################################################


# ============================================================
# 여기가 최신뉴스 URL 장고 연결하는곳!!!!!!!!!!
def chemical_news(request):
    news_list = [
        {
            "category": "연구개발",
            "title": "AI 기반 화학물질 독성 예측 기술 고도화 연구 확대",
            "date": "2026-06-25",
            "url": "/kpis/news/",
        },
        {
            "category": "산업",
            "title": "화학물질 안전관리 플랫폼 구축 및 데이터 활용 증가",
            "date": "2026-06-24",
            "url": "/kpis/news/",
        },
        {
            "category": "정책",
            "title": "환경·바이오 분야 인공지능 활용 지원 사업 추진",
            "date": "2026-06-23",
            "url": "/kpis/news/",
        },
    ]

    return render(request, "chemical_news.html", {
        "news_list": news_list,
    })

# ################################################################


# ============================================================    
# 외부사이트 이동하여 배너 안보이게!!! 장고 이용 함수
def kpis_view(request, page):
    current_page = request.GET.get("page","1")
    news_type = request.GET.get("type", "all")
    policy_type = request.GET.get("policy_type", "policy")

    # 국내외뉴스 #####################################################################
    if page == "news":
        api_url = "https://kpis.krict.re.kr/portal/news/selectNewsPrtlList.do"
        title = "국내외뉴스"

        if news_type == "domestic":
            srchCntnsClsfCd = "03"
        elif news_type == "overseas":
            srchCntnsClsfCd = "04"
        else:
            srchCntnsClsfCd = ""

        params = {
            "srchDtlCd": "01",
            "srchBgngYmd": "",
            "srchRlsYn": "Y",
            "menuNo": "",
            "mngNo": "",
            "srchGbnSub": "00",
            "srchCntnsClsfCd": srchCntnsClsfCd,
            "srchCd": "",
            "page": current_page,
            "listSize": "10",
            "srchWordSub": "",
            "srchWrd": "",
        }

        referer_url = "https://kpis.krict.re.kr/portal/news/newsPrtlList.do"

    # 부처별 자료#####################################################################
    elif page == "policy":

        # 보도자료
        if policy_type == "press":
            api_url = "https://kpis.krict.re.kr/portal/nscvrg/selectNscvrgPrtList.do"
            title = "보도자료"

            params = {
                "menuNo": "020200",
                "mngNo": "",
                "page": "1",
                "srchRlsYn": "Y",
                "srchGbnSub": "00",
                "srchWordSub": "",
                "srchCd": "",
                "srchWrd": "",
                "srchRegFromDt": "",
                "listSize": "10",
            }

            referer_url = "https://kpis.krict.re.kr/portal/nscvrg/nscvrgPrtlList.do"

        # 정책자료!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        else:
            api_url = "https://kpis.krict.re.kr/portal/policy/selectPolicyNewsPrtlList.do"
            title = "정책자료"

            params = {
                "menuNo": "020100",
                "mngNo": "",
                "page": "1",
                "srchRlsYn": "Y",
                "srchGbnSub": "00",
                "srchWordSub": "",
                "srchCd": "",
                "srchWrd": "",
                "srchRegFromDt": "",
                "listSize": "10",
            }

            referer_url = "https://kpis.krict.re.kr/portal/policy/policyNewsPrtlList.do"

    else:
        api_url = "https://kpis.krict.re.kr/portal/news/selectNewsPrtlList.do"
        title = "화학정보플랫폼"
        params = {}
        referer_url = "https://kpis.krict.re.kr/"

    # API 요청 #######################################################################
    response = requests.post(api_url, data=params, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "Origin": "https://kpis.krict.re.kr",
        "Referer": referer_url,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    })
    response.encoding = "utf-8"

    data = get_json_or_empty(response)

    # 리스트 키 분기 ##################################################################
    if page == "policy":
        if policy_type == "press":
            news_list = data.get("nscvrgMngVOList", [])
        else:
            news_list = data.get("policyNewsVOList", [])
    else:
        news_list = data.get("newsMngVOList", [])

    total_count = data.get("listTotalCnt", 0)

    # 탭 active 처리 ###################################################################
    all_active = "active" if news_type == "all" else ""
    domestic_active = "active" if news_type == "domestic" else ""
    overseas_active = "active" if news_type == "overseas" else ""

    policy_active = "active" if policy_type == "policy" else ""
    press_active = "active" if policy_type == "press" else ""

    if page == "news":
        tab_html = f"""
        <div class="tab-box">
          <a href="/kpis/news/?type=all" class="{all_active}">전체</a>
          <a href="/kpis/news/?type=domestic" class="{domestic_active}">국내</a>
          <a href="/kpis/news/?type=overseas" class="{overseas_active}">해외</a>
        </div>
        """
    elif page == "policy":
        tab_html = f"""
        <div class="tab-box">
          <a href="/kpis/policy/?policy_type=policy" class="{policy_active}">정책자료</a>
          <a href="/kpis/policy/?policy_type=press" class="{press_active}">보도자료</a>
        </div>
        """
    else:
        tab_html = ""

    # HTML 화면 구성 ###################################################################
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
      <meta charset="UTF-8">
      <title>{title}</title>
      <style>
        body {{
          margin: 0;
          font-family: Arial, sans-serif;
          background: #ffffff;
          color: #111;
        }}

        .kpis-wrap {{
          max-width: 1100px;
          margin: 30px auto;
          padding: 20px 28px;
        }}

        .top-btn {{
          display: inline-block;
          margin-bottom: 24px;
          padding: 10px 16px;
          background: #123b63;
          color: white;
          text-decoration: none;
          border-radius: 8px;
          font-weight: bold;
        }}

        h1 {{
          font-size: 30px;
          border-bottom: 1px solid #ccc;
          padding-bottom: 20px;
          margin-bottom: 32px;
        }}

        .tab-box {{
          display: flex;
          border: 1px solid #ddd;
          border-radius: 8px;
          overflow: hidden;
          margin-bottom: 24px;
        }}

        .tab-box a {{
          flex: 1;
          text-align: center;
          padding: 16px 0;
          text-decoration: none;
          color: #111;
          font-weight: bold;
          border-right: 1px solid #ddd;
        }}

        .tab-box a:last-child {{
          border-right: none;
        }}

        .tab-box a.active {{
          background: #3854b8;
          color: white;
        }}

        .list-info {{
          margin: 22px 0;
          font-size: 14px;
        }}

        .news-item {{
          padding: 24px 0;
          border-top: 1px solid #ddd;
        }}

        .policy-item {{
          display: flex;
          gap: 26px;
          padding: 24px 0;
          border-top: 1px solid #ddd;
        }}

        .policy-img {{
          width: 210px;
          height: 115px;
          object-fit: cover;
          flex-shrink: 0;
          background: #e5e7eb;
        }}

        .policy-text {{
          flex: 1;
        }}

        .badge {{
          display: inline-block;
          padding: 5px 14px;
          margin-right: 12px;
          border: 1px solid #315cff;
          color: #315cff;
          border-radius: 18px;
          font-size: 13px;
        }}

        .news-title {{
          font-size: 19px;
          font-weight: bold;
          color: #111;
          text-decoration: none;
        }}

        .news-title:hover {{
          text-decoration: underline;
        }}

        .summary {{
          margin-top: 14px;
          line-height: 1.7;
          color: #333;
          font-size: 15px;
          white-space: pre-line;
        }}

        .meta {{
          margin-top: 14px;
          color: #555;
          font-size: 14px;
        }}
        
        .pagination {{
          text-align:center;
          margin:40px 0;
        }}
        
        .pagination a {{
          display:inline-block;
          width:36px;
          height:36px;
          line-height:36px;
          margin:0 5px;
          border:1px solid #ddd;
          border-radius:50%;
          text-decoration:none;
          color:#333;
          font-weight:bold;
        }}d
        
        .pagination a:hover {{
          background:#f3f4f6;
        }}
        
        .pagination a.active {{
          background:#3854b8;
          color:white;
          border-color:#3854b8;
        }}
      </style>
    </head>

    <body>
      <div class="kpis-wrap">
        <a href="/" class="top-btn">← 메인으로</a>

        <h1>{title}</h1>

        {tab_html}

        <div class="list-info">
          전체 {total_count}건
        </div>
    """

    # 리스트 출력 #####################################################################
    for news in news_list:
        category = escape(news.get("lclsfCdNmPrtl", ""))
        title_text = escape(news.get("ttlNm", ""))
        date = escape(news.get("pblcnYmd") or news.get("pstgYmd") or "")
        media = escape(news.get("mdiaNm") or news.get("gvmtMtofNm") or "")
        summary = remove_html_tags(
            news.get("sumryCn")
            or news.get("plcyCn")
            or news.get("nscvrgDataCn")
            or ""
        )
        link = news.get("newsLnkgAddr") or news.get("dataLnkgAddr") or "#"
        img = news.get("imgAddr", "")

        if page == "policy":
            html += f"""
            <div class="policy-item">
                {'' if policy_type == "press" else (f'<img src="{img}" class="policy-img">' if img else '<div class="policy-img"></div>')}

              <div class="policy-text">
                <div>
                  <span class="badge">{category}</span>
                  <a href="{link}" target="_blank" class="news-title">{title_text}</a>
                </div>

                <div class="summary">{escape(summary[:280])}...</div>

                <div class="meta">
                  출처 : {media} &nbsp;&nbsp; | &nbsp;&nbsp; 작성일 : {date}
                </div>
              </div>
            </div>
            """
        else:
            html += f"""
            <div class="news-item">
              <div>
                <span class="badge">{category}</span>
                <a href="{link}" target="_blank" class="news-title">{title_text}</a>
              </div>
              </div>
            """
    total_page = (int(total_count) + 9) // 10
    html += '<div class="pagination">'
    for i in range(1, total_page + 1):
      active = "active" if str(i) == str(current_page) else ""
      html += f'<a class="{active}"href="?type={news_type}&page={i}">{i}</a>'
    html += "</div>"
    html += """
      </div>
    </body>
    </html>
    """

    return HttpResponse(html)

# ============================================================        


@staff_member_required
def admin_dashboard(request):
    context = {
        "user_count": User.objects.count(),
        "staff_count": User.objects.filter(is_staff=True).count(),
        "chemical_count": Chemical.objects.count(),
        "category_count": ChemicalCategory.objects.count(),
        "endpoint_count": ToxicityEndpoint.objects.count(),
        "csv_count": CSVUploadHistory.objects.count(),
        "prediction_count": PredictionHistory.objects.count(),
        "dataset_count": DatasetVersion.objects.count(),
        "notice_count": Notice.objects.count(),
        "news_count": ChemicalNews.objects.count(),
        "inquiry_count": Inquiry.objects.count(),
        "unanswered_count": Inquiry.objects.filter(is_answered=False).count(),
    }

    return render(request, "admin_dashboard.html", context)

# ##################################################################