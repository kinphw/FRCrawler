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
    title: str
    regDate: str
    reqPart: Optional[str]  # 요청부처
    reqPartSub: Optional[str]  # 요청부서
    accNum: Optional[str]  # 접수번호

@dataclass
class DetailItem:
    """상세 내용 데이터 클래스"""
    title: str
    serial_number: Optional[str]  # 일련번호
    type_text: Optional[str]  # 타입
    inquiry: Optional[str]  # 질의요지
    factual_background: Optional[str]  # 법령해석요청의 원인이 되는 사실관계 (추가)
    answer: Optional[str]  # 회답
    reason: Optional[str]  # 이유

@dataclass
class CombinedItem:
    """목록과 상세 내용을 결합한 데이터 클래스"""
    # 목록 항목
    rownumber: int
    pastreqIdx: int
    list_title: str
    regDate: str
    reqPart: Optional[str]
    reqPartSub: Optional[str]
    accNum: Optional[str]
    
    # 상세 항목
    detail_title: Optional[str] = None
    serial_number: Optional[str] = None
    type_text: Optional[str] = None
    inquiry: Optional[str] = None
    factual_background: Optional[str] = None  # 법령해석요청의 원인이 되는 사실관계 (추가)
    answer: Optional[str] = None
    reason: Optional[str] = None
    
    @classmethod
    def from_list_and_detail(cls, list_item: ListItem, detail_item: Optional[DetailItem] = None):
        """목록 아이템과 상세 아이템으로부터 결합된 아이템 생성"""
        combined = cls(
            rownumber=list_item.rownumber,
            pastreqIdx=list_item.pastreqIdx,
            list_title=list_item.title,
            regDate=list_item.regDate,
            reqPart=list_item.reqPart,
            reqPartSub=list_item.reqPartSub,
            accNum=list_item.accNum
        )
        
        if detail_item:
            combined.detail_title = detail_item.title
            combined.serial_number = detail_item.serial_number
            combined.type_text = detail_item.type_text
            combined.inquiry = detail_item.inquiry
            combined.factual_background = detail_item.factual_background  # 추가
            combined.answer = detail_item.answer
            combined.reason = detail_item.reason
            
        return combined