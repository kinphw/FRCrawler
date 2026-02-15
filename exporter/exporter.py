"""
Exporter
------------------------
DataFrame을 Pickle 또는 Excel 파일로 내보내는 클래스

작성자: kinphw
작성일: 2025-03-31
버전: 0.0.2
"""

import pandas as pd
import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class Exporter:
    """데이터 내보내기 클래스"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = "data", export_format: str = "pickle"):
        """
        Args:
            df: 변환할 DataFrame
            output_dir: 출력 파일을 저장할 디렉토리
            export_format: 내보내기 형식 ('pickle' 또는 'excel')
        """
        self.df = df
        self.output_dir = Path(output_dir)
        self.export_format = export_format.lower()
        
        self.pickle_file = self.output_dir / "db_i.pkl"
        self.excel_file = self.output_dir / "db_i.xlsx"
        
        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export(self, format_choice: int = 4) -> None:
        """전체 내보내기 프로세스 실행
        
        Args:
            format_choice: 1=pickle, 2=excel, 3=js, 4=all
        """
        try:
            if self.export_format == "excel":
                self._to_excel()
            else:
                self._to_pickle()
                
            logger.info(f"✅ 내보내기 완료: {self.export_format}")
        except Exception as e:
            logger.error(f"내보내기 중 오류 발생: {str(e)}")
            raise

    def _to_pickle(self) -> None:
        """DataFrame을 pickle 파일로 저장"""
        logger.info(f"Pickle 파일 생성 중: {self.pickle_file}")
        
        try:
            self.df.to_pickle(self.pickle_file)
            logger.info(f"✓ Pickle 파일 생성 완료: {self.pickle_file}")
            
            # Excel 파일이 존재하면 삭제 (cleanup)
            if self.excel_file.exists():
                self.excel_file.unlink()
                logger.info(f"이전 Excel 파일 삭제됨: {self.excel_file}")
                
        except Exception as e:
            logger.error(f"Pickle 파일 생성 실패: {str(e)}")
            raise

    def _to_excel(self) -> None:
        """DataFrame을 Excel 파일로 저장"""
        logger.info(f"Excel 파일 생성 중: {self.excel_file}")
        
        try:
            # Excel 파일 저장 (index=False로 인덱스 제외)
            self.df.to_excel(self.excel_file, index=False)
            logger.info(f"✓ Excel 파일 생성 완료: {self.excel_file}")
            
            # Pickle 파일이 존재하면 삭제 (cleanup)
            if self.pickle_file.exists():
                self.pickle_file.unlink()
                logger.info(f"이전 Pickle 파일 삭제됨: {self.pickle_file}")

        except Exception as e:
            logger.error(f"Excel 파일 생성 실패: {str(e)}")
            # openpyxl dependency check guidance
            if "No module named 'openpyxl'" in str(e):
                 logger.error("openpyxl 모듈이 필요합니다. 'pip install openpyxl'을 실행하세요.")
            raise

def export_dataframe(df: pd.DataFrame, output_dir: str = "data", export_format: str = "pickle") -> None:
    """
    DataFrame을 지정된 형식으로 내보내는 편의 함수
    
    Args:
        df: 변환할 DataFrame
        output_dir: 출력 파일을 저장할 디렉토리
        export_format: 내보내기 형식 ('pickle' 또는 'excel')
    """
    exporter = Exporter(df, output_dir, export_format)
    exporter.export()
    print(f"{export_format} 형식으로 저장이 완료되었습니다.")


if __name__ == "__main__":
    # 테스트용 코드
    test_df = pd.DataFrame({
        'id': range(1, 4),
        'name': ['테스트1', '테스트2', '테스트3']
    })
    
    print("--- Pickle 내보내기 테스트 ---")
    try:
        export_dataframe(test_df, export_format="pickle")
    except Exception as e:
        print(f"Pickle 오류: {e}")

    print("\n--- Excel 내보내기 테스트 ---")
    try:
        export_dataframe(test_df, export_format="excel")
    except Exception as e:
        print(f"Excel 오류: {e}")
