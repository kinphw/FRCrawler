"""
목록 및 상세 데이터 결합 클래스
"""

from integ.models import ListItem, DetailItem, CombinedItem

class DetailCombiner:
    """목록 및 상세 데이터 결합기"""
    
    def combine(self, list_item: ListItem, detail_item: DetailItem = None) -> CombinedItem:
        """ListItem과 DetailItem을 CombinedItem으로 결합"""
        return CombinedItem.from_list_and_detail(list_item, detail_item)