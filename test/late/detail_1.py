# 최근회신사례_세부_테스터

import requests

def get_detail_html(idx_value, gubun_value):
    """
    idx_value : 상세 화면에서 lawreqIdx 또는 opinionIdx가 될 값 (예: 2258)
    gubun_value : 목록에서 가져온 게시글 구분 (예: '법령해석', '비조치의견서' 등)
    """
    # 항상 고정된 파라미터
    stNo = "11"
    muNo = "171"
    actCd = "R"

    # gubun이 '법령해석'이면 LawreqDetail, 그 외면 OpinionDetail
    if gubun_value == "법령해석":
        url = "https://better.fsc.go.kr/fsc_new/replyCase/LawreqDetail.do"
        data = {
            "muNo": muNo,
            "stNo": stNo,
            "lawreqIdx": idx_value,
            "actCd": actCd
        }
    else:
        url = "https://better.fsc.go.kr/fsc_new/replyCase/OpinionDetail.do"
        data = {
            "muNo": muNo,
            "stNo": stNo,
            "opinionIdx": idx_value,
            "actCd": actCd
        }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0"
    }

    # POST로 요청
    response = requests.post(url, headers=headers, data=data)
    # HTML 응답 텍스트 그대로 출력(또는 return)
    return response.text


if __name__ == "__main__":
    # 테스트: 예를 들어 idx=2258, gubun='비조치의견서'
    idx_test = 892
    gubun_test = "비조치의견서"

    html_content = get_detail_html(idx_test, gubun_test)
    print(html_content)  # HTML 문자열 출력

import clipboard
clipboard.copy(html_content)
