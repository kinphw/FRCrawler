"""ListItem과 DetailItem 결합 담당"""
from typing import Optional
from ..models import ListItem, DetailItem, CombinedItem

class DetailCombiner:
    """상세 정보와 목록 정보 결합"""
    
    @staticmethod
    def combine(list_item: ListItem, detail_item: Optional[DetailItem]) -> CombinedItem:
        """ListItem과 DetailItem을 CombinedItem으로 결합"""
        return CombinedItem.from_list_and_detail(list_item, detail_item)