"""
데이터 모델 클래스
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class ListItem:
    """목록 아이템 데이터 클래스"""
    rownumber: int
    pastreqIdx: int  # 과거회신사례 인덱스
    pastreqType: str # 법령해석/비조치의견서 (실제로는 다 법령해석)
    pastreqSubject: str # 제목
    serialNum: Optional[str]  # 일련번호
    regDate: str # 등록일자        

@dataclass
class DetailItem:
    """상세 내용 데이터 클래스"""
    inquiry: Optional[str]  # 질의요지
    fact: Optional[str]  # 법령해석요청의 원인이 되는 사실관계
    baseLaw: Optional[str] # 해석대상 법령 조문 및 관련 법령
    answer: Optional[str] # 회답
    reason: Optional[str] # 이유    

@dataclass
class CombinedItem:
    """목록과 상세 내용을 결합한 데이터 클래스"""
    # 목록 항목
    rownumber: int
    pastreqIdx: int  # 과거회신사례 인덱스
    pastreqType: str # 법령해석/비조치의견서 (실제로는 다 법령해석)
    pastreqSubject: str # 제목
    serialNum: Optional[str]  # 일련번호
    regDate: str # 등록일자    
    
    # 상세 항목
    inquiry: Optional[str]  # 질의요지
    fact: Optional[str]  # 법령해석요청의 원인이 되는 사실관계
    baseLaw: Optional[str] # 해석대상 법령 조문 및 관련 법령
    answer: Optional[str] # 회답
    reason: Optional[str] # 이유   
    
    @classmethod
    def from_list_and_detail(cls, list_item: ListItem, detail_item: Optional[DetailItem] = None):
        """목록 아이템과 상세 아이템으로부터 결합된 아이템 생성"""
        # 기본적으로 ListItem의 모든 필드를 가져옴
        combined = cls(
            rownumber=list_item.rownumber,
            pastreqIdx=list_item.pastreqIdx,
            pastreqType=list_item.pastreqType,
            pastreqSubject=list_item.pastreqSubject,
            serialNum=list_item.serialNum,
            regDate=list_item.regDate,
            
            # DetailItem 필드는 None으로 초기화
            inquiry=None,
            fact=None,
            baseLaw=None,
            answer=None,
            reason=None
        )
        
        # DetailItem이 제공된 경우 해당 필드 업데이트
        if detail_item:
            combined.inquiry = detail_item.inquiry
            combined.fact = detail_item.fact
            combined.baseLaw = detail_item.baseLaw
            combined.answer = detail_item.answer
            combined.reason = detail_item.reason
            
        return combined