# 최근회신사례_세부_테스터

import requests
import clipboard

def get_detail_html(idx_value, gubun_value):
    """
    idx_value : 상세 화면에서 lawreqIdx 또는 opinionIdx가 될 값 (예: 2258)
    gubun_value : 목록에서 가져온 게시글 구분 (예: '법령해석', '비조치의견서' 등)
    """
    # 항상 고정된 파라미터
    stNo = "11"
    muNo = "117"
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
    elif gubun_value == "비조치의견서":
        url = "https://better.fsc.go.kr/fsc_new/replyCase/OpinionDetail.do"
        data = {
            "muNo": muNo,
            "stNo": stNo,
            "opinionIdx": idx_value,
            "actCd": actCd
        }
    elif gubun_value == "현장건의과제":
        url = "https://better.fsc.go.kr/fsc_new/ExmntTaskDetail.do"
        data = {
            "muNo": muNo,
            "stNo": stNo,
            "checkplaceNo": idx_value,
            "checkplaceSetIdx": "2",
            "actCd": actCd
        }        
        # goUrl(url, {muNo:$("#muNo").val(), stNo:$("#stNo").val(), checkplaceNo: idx, checkplaceSetIdx:"2", actCd: 'R'});

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
    
    # 1437784, 현장건의과제

    # idx_test = 4518
    # gubun_test = "법령해석"    

    # idx_test = 2253
    # gubun_test = "비조치의견서"

    idx_test = 1437784
    gubun_test = "현장건의과제"

    html_content = get_detail_html(idx_test, gubun_test)
    print(html_content)  # HTML 문자열 출력
    clipboard.copy(html_content)




# 원천 소스

# /* 이름: openReplyCaseLawreqDetail
#  * 설명: 상세화면 페이지로 이동
#  */
# function openReplyCasePastReqDetail(idx, gubun){
# 	 if(gubun == 1){ //법령해석
# 		 var url = "/fsc_new/replyCase/LawreqDetail.do";
# 		 goUrl(url, {muNo:$("#muNo").val(), stNo:$("#stNo").val(), lawreqIdx: idx, actCd: 'R'});
# 	 }else if(gubun == 2){ //비조치의견서
# 		 var url = "/fsc_new/replyCase/OpinionDetail.do";
# 		 goUrl(url, {muNo:$("#muNo").val(), stNo:$("#stNo").val(), opinionIdx: idx, actCd: 'R'});
# 	 }else if(gubun == 3){ //현장건의 과제
# 		 var url = "/fsc_new/ExmntTaskDetail.do";
# 		 goUrl(url, {muNo:$("#muNo").val(), stNo:$("#stNo").val(), checkplaceNo: idx, checkplaceSetIdx:"2", actCd: 'R'});
# 	 }else if(gubun == 4){ //과거회신 사례
# 		 var url = "/fsc_new/replyCase/PastReqDetail.do";
# 		 goUrl(url, {muNo:$("#muNo").val(), stNo:$("#stNo").val(), pastreqIdx: idx, actCd: 'R'});
# 	 }
# }