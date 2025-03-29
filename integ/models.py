"""
통합회신사례 데이터 모델
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ListItem:
    """목록 페이지 항목"""
    dataIdx: int                # 게시물 번호
    title: str             # 제목
    replyRegDate: str              # 등록일    
    pastreqType: str            # 법령해석/비조치의견서/현장건의과제 구분

@dataclass
class DetailItem:
    """상세 페이지 공통 항목"""
    title: str
    reply_date: Optional[str] = None         # 회신일

    # 법령해석/비조치의견서 필드
    registrant: Optional[str] = None         # 신청인
    inquiry: Optional[str] = None            # 질의내용
    answer: Optional[str] = None             # 회신내용
    reason: Optional[str] = None             # 판단이유 (법령해석만)

    # 현장건의과제 필드
    department: Optional[str] = None         # 소관부서
    category_detail: Optional[str] = None    # 과제분류
    proposal: Optional[str] = None           # 건의내용
    review_opinion: Optional[str] = None     # 검토의견
    review_reason: Optional[str] = None      # 사유
    future_plan: Optional[str] = None        # 향후계획

@dataclass
class CombinedItem:
    """목록과 상세 정보가 결합된 항목"""
    # 목록 정보
    idx: int
    title: str
    date: str
    category: str
    gubun: str

    # 상세 정보 (DetailItem의 모든 필드 포함)
    reply_date: Optional[str] = None
    registrant: Optional[str] = None
    inquiry: Optional[str] = None
    answer: Optional[str] = None
    reason: Optional[str] = None
    department: Optional[str] = None
    category_detail: Optional[str] = None
    proposal: Optional[str] = None
    review_opinion: Optional[str] = None
    review_reason: Optional[str] = None
    future_plan: Optional[str] = None

    @classmethod
    def from_items(cls, list_item: ListItem, detail_item: DetailItem) -> 'CombinedItem':
        """목록과 상세 항목으로부터 통합 항목 생성"""
        combined_data = {
            'idx': list_item.idx,
            'title': list_item.title,
            'date': list_item.date,
            'category': list_item.category,
            'gubun': list_item.gubun
        }
        
        # DetailItem의 필드 추가
        for field in DetailItem.__dataclass_fields__:
            value = getattr(detail_item, field, None)
            if value is not None:
                combined_data[field] = value
                
        return cls(**combined_data)