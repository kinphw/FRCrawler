"""
데이터 모델 클래스
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class ListItem:
    """목록 아이템 데이터 클래스"""
    rownumber: int # 사용할 필요 없는 정보
    idx: int # 목록 아이템 인덱스
    gubun: str # 법령해석, 비조치의견서
    category: Optional[str] # 전자금융 등
    title: str # 제목
    regDate: str # 등록일자
    number: str # 일련번호

@dataclass
class DetailItem:
    """상세 내용 데이터 클래스"""
    title: str # 제목
    registrant: Optional[str] # 등록자
    reply_date: Optional[str] # 회신일자
    inquiry: Optional[str] # 질의요지
    answer: Optional[str] # 회답
    reason: Optional[str] # 이유

@dataclass
class CombinedItem:
    """목록과 상세 내용을 결합한 데이터 클래스"""
    # 목록 항목
    rownumber: int
    idx: int
    gubun: str
    category: Optional[str]
    list_title: str
    regDate: str
    number: str
    
    # 상세 항목
    detail_title: Optional[str] = None
    registrant: Optional[str] = None
    reply_date: Optional[str] = None
    inquiry: Optional[str] = None
    answer: Optional[str] = None
    reason: Optional[str] = None
    
    @classmethod
    def from_list_and_detail(cls, list_item: ListItem, detail_item: Optional[DetailItem] = None):
        """목록 아이템과 상세 아이템으로부터 결합된 아이템 생성"""
        combined = cls(
            rownumber=list_item.rownumber,
            idx=list_item.idx,
            gubun=list_item.gubun,
            category=list_item.category,
            list_title=list_item.title,
            regDate=list_item.regDate,
            number=list_item.number
        )
        
        if detail_item:
            combined.detail_title = detail_item.title
            combined.registrant = detail_item.registrant
            combined.reply_date = detail_item.reply_date
            combined.inquiry = detail_item.inquiry
            combined.answer = detail_item.answer
            combined.reason = detail_item.reason
            
        return combined