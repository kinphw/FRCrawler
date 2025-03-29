"""
통합회신사례 데이터 모델 정의
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ListItem:
    """목록 아이템 데이터 클래스"""
    rownumber: int
    idx: int  # 문서 식별자 (lawreqIdx, opinionIdx, checkplaceNo 등)
    gubun: str  # 구분 (법령해석, 비조치의견서, 현장건의과제)
    category: Optional[str]  # 카테고리
    title: str  # 제목
    regDate: str  # 등록일
    number: Optional[str] = None  # 번호


@dataclass
class DetailItem:
    """상세 내용 데이터 클래스"""
    # 공통 필드
    title: str  # 제목
    
    # 법령해석, 비조치의견서 공통 필드
    registrant: Optional[str] = None  # 등록자
    reply_date: Optional[str] = None  # 회신일
    inquiry: Optional[str] = None  # 질의요지
    answer: Optional[str] = None  # 회답
    reason: Optional[str] = None  # 이유
    
    # 현장건의과제 필드
    department: Optional[str] = None  # 소관부서
    category_detail: Optional[str] = None  # 과제분류
    proposal: Optional[str] = None  # 건의내용
    review_opinion: Optional[str] = None  # 검토의견
    review_reason: Optional[str] = None  # 사유
    future_plan: Optional[str] = None  # 향후계획


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
    number: Optional[str] = None
    
    # 상세 항목 (공통)
    detail_title: Optional[str] = None
    
    # 법령해석, 비조치의견서 공통 필드
    registrant: Optional[str] = None
    reply_date: Optional[str] = None
    inquiry: Optional[str] = None
    answer: Optional[str] = None
    reason: Optional[str] = None
    
    # 현장건의과제 필드
    department: Optional[str] = None  # 소관부서
    category_detail: Optional[str] = None  # 과제분류
    proposal: Optional[str] = None  # 건의내용
    review_opinion: Optional[str] = None  # 검토의견
    review_reason: Optional[str] = None  # 사유
    future_plan: Optional[str] = None  # 향후계획
    
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
            
            # 법령해석, 비조치의견서 필드
            combined.registrant = detail_item.registrant
            combined.reply_date = detail_item.reply_date
            combined.inquiry = detail_item.inquiry
            combined.answer = detail_item.answer
            combined.reason = detail_item.reason
            
            # 현장건의과제 필드
            combined.department = detail_item.department
            combined.category_detail = detail_item.category_detail
            combined.proposal = detail_item.proposal
            combined.review_opinion = detail_item.review_opinion
            combined.review_reason = detail_item.review_reason
            combined.future_plan = detail_item.future_plan
            
        return combined