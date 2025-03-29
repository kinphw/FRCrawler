"""
특정 항목 파싱 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detail_crawler import DetailCrawler

def test_specific_item():
    """특정 항목을 테스트합니다."""
    detail_crawler = DetailCrawler()
    
    # 테스트할 항목
    idx = 892
    gubun = "비조치의견서"
    
    # 상세 내용 가져오기
    detail_item = detail_crawler.get_detail_item(idx, gubun)
    
    # 결과 출력
    print("\n=== 파싱 결과 ===")
    print(f"제목: {detail_item.title}")
    print(f"등록자: {detail_item.registrant}")
    print(f"회신일: {detail_item.reply_date}")
    print(f"질의요지: {detail_item.inquiry}")
    print(f"회답: {detail_item.answer}")
    print(f"이유: {detail_item.reason}")
    
    # 모든 필드가 있는지 확인
    fields = {
        "제목": detail_item.title,
        "등록자": detail_item.registrant,
        "회신일": detail_item.reply_date,
        "질의요지": detail_item.inquiry,
        "회답": detail_item.answer,
        "이유": detail_item.reason
    }
    
    missing_fields = [field for field, value in fields.items() if value is None]
    if missing_fields:
        print(f"\n⚠️ 누락된 필드: {', '.join(missing_fields)}")
    else:
        print("\n✅ 모든 필드가 정상적으로 파싱되었습니다!")

if __name__ == "__main__":
    test_specific_item()