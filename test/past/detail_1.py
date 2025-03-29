# 기존 회신사례_세부_테스터

import requests
import clipboard

def get_detail_html(pastreq_idx):
    """
    pastreq_idx : 상세 화면에서 pastreqIdx가 될 값 (예: 1892)
    """
    # 항상 고정된 파라미터
    stNo = "11"
    muNo = "172"  # 법령해석 질의회신 메뉴 번호
    actCd = "R"

    # 과거 법령해석 질의회신 상세 URL
    url = "https://better.fsc.go.kr/fsc_new/replyCase/PastReqDetail.do"
    
    # 요청 데이터
    data = {
        "muNo": muNo,
        "stNo": stNo,
        "pastreqIdx": pastreq_idx,
        "actCd": actCd
    }

    # 요청 헤더
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReqList.do?stNo=11&muNo=172&muGpNo=75",
        "Origin": "https://better.fsc.go.kr"
    }

    # POST로 요청
    response = requests.post(url, headers=headers, data=data)
    
    # 응답 상태 확인
    if response.status_code != 200:
        print(f"오류: 상태 코드 {response.status_code}")
        return None
        
    # HTML 응답 텍스트 반환
    return response.text


if __name__ == "__main__":
    # 테스트: 예제 pastreqIdx=1892 사용
    test_idx = 1892
    
    print(f"pastreqIdx={test_idx}인 항목의 상세 내용을 가져오는 중...")
    html_content = get_detail_html(test_idx)
    
    if html_content:
        # 결과 출력
        print("\n=== HTML 응답 일부 (처음 500자) ===")
        print(html_content[:500])
        print("...")
        
        # 응답 길이 출력
        print(f"\nHTML 응답 길이: {len(html_content)} 문자")
        
        # 클립보드에 복사
        clipboard.copy(html_content)
        print("\nHTML 내용이 클립보드에 복사되었습니다.")
        
        # HTML 파일로도 저장 (선택 사항)
        # with open(f"past_req_detail_{test_idx}.html", "w", encoding="utf-8") as f:
        #     f.write(html_content)
        # print(f"HTML 내용이 past_req_detail_{test_idx}.html 파일로 저장되었습니다.")
        
        # 간단한 확인
        if "법령해석" in html_content:
            print("\n※ 응답에 '법령해석' 문자열이 포함되어 있습니다.")
        if "질의요지" in html_content:
            print("※ 응답에 '질의요지' 문자열이 포함되어 있습니다.")
        if "회신" in html_content:
            print("※ 응답에 '회신' 문자열이 포함되어 있습니다.")
    else:
        print("HTML 내용을 가져오지 못했습니다.")