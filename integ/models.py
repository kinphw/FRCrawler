"""
데이터 모델 클래스들
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

@dataclass
class ListItem:
    """목록 페이지 항목 모델 - API 응답에 맞춤"""
    rownumber: int
    dataIdx: int
    pastreqType: str  # 유형 문자열 (법령해석, 비조치의견서 등)
    title: str
    replyRegDate: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListItem':
        """딕셔너리로부터 모델 객체 생성"""
        return cls(
            rownumber=int(data.get('rownumber', 0)),
            dataIdx=int(data.get('dataIdx', 0)),
            pastreqType=data.get('pastreqType', ''),
            title=data.get('title', ''),
            replyRegDate=data.get('replyRegDate', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            "rownumber": self.rownumber,
            "dataIdx": self.dataIdx,
            "pastreqType": self.pastreqType,
            "title": self.title,
            "replyRegDate": self.replyRegDate
        }

@dataclass
class DetailItem:
    """상세 페이지 항목 모델 - 모든 유형 공통"""
    
    dataIdx: int
    category: Optional[str] = None
    reply_date : Optional[str] = None  # 회신일자
    inquiry : Optional[str] = None  # 질의내용/신청내용
    answer_conclusion: Optional[str] = None  # 검토의견
    answer_content: Optional[str] = None  # 회신내용/답변내용
    plan: Optional[str] = None  # 향후계획
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = {
            "dataIdx": self.dataIdx,
            "category": self.category,
            "reply_date": self.reply_date,
            "inquiry": self.inquiry,  # 오타이지만 원래 필드명 그대로 유지
            "answer_conclusion": self.answer_conclusion,
            "answer_content": self.answer_content,
            "plan": self.plan
        }
        
        # None 값은 제외
        return {k: v for k, v in result.items() if v is not None}

@dataclass
class CombinedItem:
    """ListItem과 DetailItem을 결합한 모델"""
    # 목록 항목 필드 (ListItem)
    rownumber: int
    dataIdx: int
    pastreqType: str
    list_title: str  # 목록의 title 필드
    replyRegDate: str
    
    # 상세 항목 필드 (DetailItem)
    category: Optional[str] = None
    reply_date: Optional[str] = None
    inquiry: Optional[str] = None  # DetailItem의 오타 그대로 유지
    answer_conclusion: Optional[str] = None
    answer_content: Optional[str] = None
    plan: Optional[str] = None
    
    # 추가 필드 (유형별 특수 필드)
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_list_and_detail(cls, list_item: ListItem, detail_item: Optional[DetailItem] = None) -> 'CombinedItem':
        """목록 아이템과 상세 아이템으로부터 결합된 아이템 생성"""
        # ListItem 필드로 기본 객체 생성
        combined = cls(
            rownumber=list_item.rownumber,
            dataIdx=list_item.dataIdx,
            pastreqType=list_item.pastreqType,
            list_title=list_item.title,
            replyRegDate=list_item.replyRegDate
        )
        
        # DetailItem이 있는 경우 해당 필드 추가
        if detail_item:
            combined.category = detail_item.category
            combined.reply_date = detail_item.reply_date
            combined.inquiry = detail_item.inquiry
            combined.answer_conclusion = detail_item.answer_conclusion
            combined.answer_content = detail_item.answer_content
            combined.plan = detail_item.plan
            
            # 추가 필드가 있는 경우를 대비
            combined.extra_data = {}
        
        return combined

    def to_dict(self) -> Dict[str, Any]:
        """데이터프레임 변환용 딕셔너리"""
        # 기본 필드
        result = {
            "rownumber": self.rownumber,
            "dataIdx": self.dataIdx,
            "pastreqType": self.pastreqType,
            "list_title": self.list_title,
            "replyRegDate": self.replyRegDate,
            "category": self.category,
            "reply_date": self.reply_date,
            "inquiry": self.inquiry,
            "answer_conclusion": self.answer_conclusion,
            "answer_content": self.answer_content,
            "plan": self.plan
        }
        
        # None 값 제외
        result = {k: v for k, v in result.items() if v is not None}
        
        # 특수 필드 추가 (있는 경우)
        for key, value in self.extra_data.items():
            if value is not None:
                result[f"extra_{key}"] = value
            
        return result