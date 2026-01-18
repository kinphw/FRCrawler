"""
Exporter
------------------------
DataFrame을 SQLite DB로 변환하고 이를 base64로 인코딩하여 
JavaScript 파일로 내보내는 클래스

작성자: kinphw
작성일: 2025-03-31
버전: 0.0.1
"""

import pandas as pd
import sqlite3
import base64
import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class Exporter:
    """데이터 내보내기 클래스"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = "data"):
        """
        Args:
            df: 변환할 DataFrame
            output_dir: 출력 파일을 저장할 디렉토리
        """
        self.df = df
        self.output_dir = Path(output_dir)
        
        # 타임스탬프 생성 (yyMMdd_hhmmss 형식)
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        
        self.pickle_file = self.output_dir / f"db_i_{timestamp}.pkl"
        self.db_file = self.output_dir / f"db_i_{timestamp}.db"
        self.js_file = self.output_dir / f"db_i_{timestamp}.js"
        self.excel_file = self.output_dir / f"db_i_{timestamp}.xlsx"
        
        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export(self, format_choice: int = 4) -> None:
        """전체 내보내기 프로세스 실행
        
        Args:
            format_choice: 1=pickle, 2=excel, 3=js, 4=all
        """
        try:
            if format_choice == 1 or format_choice == 4:
                self._to_pickle()
            
            if format_choice == 2 or format_choice == 4:
                self._to_excel()
            
            if format_choice == 3 or format_choice == 4:
                self._to_sqlite()
                self._to_javascript()
            
            logger.info(f"✅ 내보내기 완료")
        except Exception as e:
            logger.error(f"내보내기 중 오류 발생: {str(e)}")
            raise

    def _to_pickle(self) -> None:
        """DataFrame을 pickle 파일로 저장 (선택적)"""
        logger.info(f"Pickle 파일 생성 중: {self.pickle_file}")
        
        # DataFrame을 pickle 파일로 저장
        self.df.to_pickle(self.pickle_file)
        logger.info(f"✓ Pickle 파일 생성 완료: {self.pickle_file}")
    
    def _to_excel(self) -> None:
        """DataFrame을 Excel 파일로 저장"""
        logger.info(f"Excel 파일 생성 중: {self.excel_file}")
        
        # DataFrame을 Excel 파일로 저장
        self.df.to_excel(self.excel_file, index=False, engine='openpyxl')
        logger.info(f"✓ Excel 파일 생성 완료: {self.excel_file}")        

    def _to_sqlite(self) -> None:
        """DataFrame을 SQLite DB로 변환"""
        logger.info(f"SQLite DB 생성 중: {self.db_file}")
        
        # DB 연결
        conn = sqlite3.connect(self.db_file)
        
        try:
            # 테이블 생성 (기존 테이블 삭제)
            self.df.to_sql("db_i", conn, if_exists="replace", index=False)
            conn.commit()
            logger.info(f"✓ SQLite DB 생성 완료: {len(self.df)}행")
            
        finally:
            conn.close()
            
    def _to_javascript(self) -> None:
        """SQLite DB를 Base64로 인코딩하여 JavaScript 파일로 변환"""
        logger.info(f"JavaScript 파일 생성 중: {self.js_file}")
        
        # DB 파일을 Base64로 인코딩
        with open(self.db_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            
        # JavaScript 클래스 템플릿
        js_content = f"""class Dataset {{
    databaseBase64 = "{encoded}";

    // Base64를 바이너리로 변환하여 Uint8Array 반환
    getDatabaseBinary() {{
        const binaryString = atob(this.databaseBase64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {{
            bytes[i] = binaryString.charCodeAt(i);
        }}
        return bytes;
    }}
}};

window.Dataset = Dataset;
"""
        
        # JavaScript 파일로 저장
        with open(self.js_file, "w", encoding="utf-8") as f:
            f.write(js_content)
            
        logger.info(f"✓ JavaScript 파일 생성 완료")
        
    def cleanup(self) -> None:
        """임시 파일 정리"""
        try:
            if self.db_file.exists():
                self.db_file.unlink()
                logger.info(f"임시 DB 파일 삭제: {self.db_file}")
        except Exception as e:
            logger.warning(f"임시 파일 정리 중 오류: {str(e)}")


def export_dataframe(df: pd.DataFrame, output_dir: str = "data") -> None:
    """
    DataFrame을 사용자가 선택한 형식으로 내보내는 편의 함수
    
    Args:
        df: 변환할 DataFrame
        output_dir: 출력 파일을 저장할 디렉토리
    """
    print("\n=== 출력 형식 선택 ===")
    print("1. Pickle (.pkl)")
    print("2. Excel (.xlsx)")
    print("3. JavaScript (.js)")
    print("4. 전부 저장")
    
    while True:
        try:
            choice = int(input("선택하세요 (1-4): ").strip())
            if 1 <= choice <= 4:
                break
            else:
                print("1에서 4 사이의 숫자를 입력하세요.")
        except ValueError:
            print("올바른 숫자를 입력하세요.")
    
    exporter = Exporter(df, output_dir)
    try:
        exporter.export(format_choice=choice)
        
        # 선택한 형식 출력
        formats = []
        if choice == 1 or choice == 4:
            formats.append("Pickle")
        if choice == 2 or choice == 4:
            formats.append("Excel")
        if choice == 3 or choice == 4:
            formats.append("JavaScript")
        
        print(f"\n✅ {', '.join(formats)} 형식으로 저장되었습니다.")
    finally:
        if choice == 3 or choice == 4:
            # JavaScript 선택 시에만 cleanup 메시지 표시
            print("db파일은 정리하지 않습니다. db파일과 js파일 중 선택하여 사용하세요.")


if __name__ == "__main__":
    # 테스트용 코드
    test_df = pd.DataFrame({
        'id': range(1, 4),
        'name': ['테스트1', '테스트2', '테스트3']
    })
    
    try:
        export_dataframe(test_df)
        print("변환 완료!")
    except Exception as e:
        print(f"오류 발생: {str(e)}")