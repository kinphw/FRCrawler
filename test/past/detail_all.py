# 과거 회신사례_세부_파싱 후 취합_테스터

import requests
import pandas as pd
import re
from bs4 import BeautifulSoup

def get_detail_html(pastreq_idx):
    """
    1) HTML 수신 (HTTP 요청) 함수
    pastreq_idx : 상세화면 pastreqIdx 값 (예: 1892)
    """
    # 항상 고정된 파라미터
    stNo = "11"
    muNo = "172"  # 과거 법령해석 질의회신 메뉴 번호
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
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReqList.do?stNo=11&muNo=172&muGpNo=75",
        "Origin": "https://better.fsc.go.kr"
    }

    # POST로 요청
    response = requests.post(url, headers=headers, data=data)
    return response.text  # HTML 원문을 문자열로 반환


def html_to_text_preserve_p_br(html_snippet):
    """
    <p>와 <br>만 개행(\n)으로 치환하고,
    그 외 모든 태그는 제거(태그 안 텍스트는 남김).
    """
    if not html_snippet:
        return ""
    
    try:
        # 1) <p ...> => '\n'
        text = re.sub(r'<p[^>]*>', '\n', html_snippet, flags=re.IGNORECASE)
        # 2) </p> => '' (굳이 라인브레이크를 중복해서 넣지 않음)
        text = re.sub(r'</p\s*>', '', text, flags=re.IGNORECASE)

        # 3) <br ...> => '\n'
        text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)

        # 4) 그 외 모든 태그 제거 (안의 텍스트는 남김)
        #    예: <span>TEXT</span> -> "TEXT"
        text = re.sub(r'<[^<]*?>', '', text, flags=re.DOTALL)
        
        # 특수 마크업 및 메타데이터 제거
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        text = re.sub(r'<!\[CDATA\[.*?\]\]>', '', text, flags=re.DOTALL)

        # 5) 연속 개행 \n\n\n... -> \n
        text = re.sub(r'\n+', '\n', text)

        # 마무리
        return text.strip()
    except Exception as e:
        print(f"HTML 텍스트 변환 오류: {str(e)}")
        # 오류 발생 시 원본 HTML에서 가능한 많은 텍스트 추출 시도
        try:
            # 간단한 태그 제거 시도
            return re.sub(r'<[^>]*>', ' ', html_snippet).strip()
        except:
            # 완전히 실패한 경우
            return "[HTML 변환 오류]"


def parse_past_req_detail(html_content):
    """
    2) BeautifulSoup으로 HTML을 파싱.
       * 특정 <td>나 <th>~<td> 구조를 찾은 뒤,
         위의 html_to_text_preserve_p_br() 함수를 통해
         <p>와 <br>만 개행 처리하고, 나머지 태그는 무시.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # [1] 제목: <td class="subject">
    title_td = soup.find("td", class_="subject")
    title_html = str(title_td) if title_td else ""
    title = html_to_text_preserve_p_br(title_html)

    # [2] 특정 <th> 텍스트를 찾아서, 바로 옆 <td> 텍스트만 추출
    def get_td_html_after_th(th_text):
        # 방법 1: 정확한 텍스트 매칭
        th_tag = soup.find("th", string=lambda x: x and x.strip() == th_text)
        if th_tag:
            td_tag = th_tag.find_next("td")
            return str(td_tag) if td_tag else None
            
        # 방법 2: 클래스 속성 고려 매칭
        all_th_tags = soup.find_all("th", attrs={"scope": "row"})
        for th in all_th_tags:
            if th.text.strip() == th_text:
                td_tag = th.find_next("td")
                return str(td_tag) if td_tag else None
                
        # 방법 3: 더 일반적인 검색
        all_th_tags = soup.find_all("th")
        for th in all_th_tags:
            if th.text.strip() == th_text:
                td_tag = th.find_next("td")
                return str(td_tag) if td_tag else None
                
        return None

    # 각 필드별 파싱
    serial_number_html = get_td_html_after_th("일련번호")
    serial_number = html_to_text_preserve_p_br(serial_number_html) if serial_number_html else None
    
    type_html = get_td_html_after_th("타입")
    type_text = html_to_text_preserve_p_br(type_html) if type_html else None
    
    inquiry_html = get_td_html_after_th("질의요지")
    inquiry = html_to_text_preserve_p_br(inquiry_html) if inquiry_html else None
    
    # 법령해석요청의 원인이 되는 사실관계 추가
    factual_background_html = get_td_html_after_th("법령해석요청의 원인이 되는 사실관계")
    factual_background = html_to_text_preserve_p_br(factual_background_html) if factual_background_html else None
    
    answer_html = get_td_html_after_th("회답")
    answer = html_to_text_preserve_p_br(answer_html) if answer_html else None
    
    reason_html = get_td_html_after_th("이유")
    reason = html_to_text_preserve_p_br(reason_html) if reason_html else None

    # 정규식으로 이유 필드 추가 확인 (필드가 없는 경우)
    if not reason:
        reason_pattern = re.search(r'<th[^>]*>이유</th>\s*<td[^>]*>(.*?)</td>', html_content, re.DOTALL | re.IGNORECASE)
        if reason_pattern:
            reason_html = reason_pattern.group(1)
            reason = html_to_text_preserve_p_br(f"<td>{reason_html}</td>")
            print("정규식으로 이유를 찾았습니다.")
    
    # 정규식으로 법령해석요청의 원인이 되는 사실관계 추가 확인 (필드가 없는 경우)
    if not factual_background:
        fact_pattern = re.search(r'<th[^>]*>법령해석요청의 원인이 되는 사실관계</th>\s*<td[^>]*>(.*?)</td>', 
                                html_content, re.DOTALL | re.IGNORECASE)
        if fact_pattern:
            fact_html = fact_pattern.group(1)
            factual_background = html_to_text_preserve_p_br(f"<td>{fact_html}</td>")
            print("정규식으로 법령해석요청의 원인이 되는 사실관계를 찾았습니다.")

    data_dict = {
        "제목": title,
        "일련번호": serial_number,
        "타입": type_text,
        "질의요지": inquiry,
        "법령해석요청의 원인이 되는 사실관계": factual_background,  # 추가
        "회답": answer,
        "이유": reason
    }
    return pd.DataFrame([data_dict])


if __name__ == "__main__":
    # 예시 pastreqIdx 값
    idx_test = 1892
    
    print(f"\n=== 과거 회신사례 테스트 (pastreqIdx={idx_test}) ===\n")
    
    # HTML 가져오기
    html_content = get_detail_html(idx_test)
    
    # 파싱
    df = parse_past_req_detail(html_content)
    
    # 결과 출력
    for col in df.columns:
        value = df[col].iloc[0]
        if value:
            if len(str(value)) > 100:
                print(f"{col}: {str(value)[:100]}...")
            else:
                print(f"{col}: {value}")
        else:
            print(f"{col}: (없음)")
    
    # 엑셀로 저장
    output_file = "past_req_detail.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n결과가 {output_file}로 저장되었습니다.")