"""
특정 항목 파싱 테스트
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detail_crawler import DetailCrawler
import traceback

def test_specific_item(idx, gubun):
    """특정 항목을 테스트합니다."""
    try:
        detail_crawler = DetailCrawler()
        
        print(f"\n테스트 시작: idx={idx}, gubun={gubun}")
        
        # 상세 내용 가져오기
        detail_item = detail_crawler.get_detail_item(idx, gubun)
        
        if detail_item:
            # 결과 출력
            print("\n=== 파싱 결과 ===")
            print(f"제목: {detail_item.title}")
            print(f"등록자: {detail_item.registrant}")
            print(f"회신일: {detail_item.reply_date}")
            print(f"질의요지: {detail_item.inquiry if detail_item.inquiry else '(없음)'}")
            print(f"회답: {detail_item.answer[:100] + '...' if detail_item.answer and len(detail_item.answer) > 100 else detail_item.answer}")
            print(f"이유: {detail_item.reason[:100] + '...' if detail_item.reason and len(detail_item.reason) > 100 else detail_item.reason}")
            
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
            
            return detail_item
        else:
            print(f"❌ 항목을 가져오지 못했습니다: idx={idx}, gubun={gubun}")
            return None
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    # # 비조치의견서 테스트
    # print("\n=== 비조치의견서 테스트 ===")
    # test_specific_item(892, "비조치의견서")
    
    # 법령해석 테스트 
    print("\n=== 법령해석 테스트 ===")
    test_specific_item(2770, "법령해석")