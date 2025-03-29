# 최근회신사례_세부_파싱 후 취합_테스터

import requests
import pandas as pd
import re
from bs4 import BeautifulSoup

def get_detail_html(idx_value, gubun_value):
    """
    1) HTML 수신 (HTTP 요청) 함수
    idx_value : 상세화면 idx (lawreqIdx/opinionIdx)
    gubun_value : '법령해석' 또는 '비조치의견서' 등
    """
    stNo = "11"
    muNo = "171"
    actCd = "R"

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

    response = requests.post(url, headers=headers, data=data)
    return response.text  # HTML 원문을 문자열로 반환


def html_to_text_preserve_p_br(html_snippet):
    """
    <p>와 <br>만 개행(\n)으로 치환하고,
    그 외 모든 태그는 제거(태그 안 텍스트는 남김).
    """
    # 1) <p ...> => '\n'
    text = re.sub(r'<p[^>]*>', '\n', html_snippet, flags=re.IGNORECASE)
    # 2) </p> => '' (굳이 라인브레이크를 중복해서 넣지 않음)
    text = re.sub(r'</p\s*>', '', text, flags=re.IGNORECASE)

    # 3) <br ...> => '\n'
    text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)

    # 4) 그 외 모든 태그 제거 (안의 텍스트는 남김)
    #    예: <span>TEXT</span> -> "TEXT"
    text = re.sub(r'<.*?>', '', text, flags=re.DOTALL)

    # 5) 연속 개행 \n\n\n... -> \n
    text = re.sub(r'\n+', '\n', text)

    # 마무리
    return text.strip()


def parse_opinion_detail(html_content):
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
        th_tag = soup.find("th", string=lambda x: x and x.strip() == th_text)
        if not th_tag:
            return None
        td_tag = th_tag.find_next("td")
        return str(td_tag) if td_tag else None

    # 이렇게 추출한 td HTML에 대해, p/br 개행 변환 + 나머지태그 제거
    registrant_html = get_td_html_after_th("등록자")
    registrant = html_to_text_preserve_p_br(registrant_html) if registrant_html else None

    reply_date_html = get_td_html_after_th("회신일")
    reply_date = html_to_text_preserve_p_br(reply_date_html) if reply_date_html else None

    inquiry_html = get_td_html_after_th("질의요지")
    inquiry = html_to_text_preserve_p_br(inquiry_html) if inquiry_html else None

    answer_html = get_td_html_after_th("회답")
    answer = html_to_text_preserve_p_br(answer_html) if answer_html else None

    reason_html = get_td_html_after_th("이유")
    reason = html_to_text_preserve_p_br(reason_html) if reason_html else None

    data_dict = {
        "제목": title,
        "등록자": registrant,
        "회신일": reply_date,
        "질의요지": inquiry,
        "회답": answer,
        "이유": reason
    }
    return pd.DataFrame([data_dict])


if __name__ == "__main__":
    # [사용 예시] "법령해석" (lawreqIdx=5107)
    # idx_test = 5107
    # gubun_test = "법령해석"

    idx_test = 2258
    gubun_test = "비조치의견서"

    html_content = get_detail_html(idx_test, gubun_test)
    df = parse_opinion_detail(html_content)

    print(df)

df.to_excel("b.xlsx")
