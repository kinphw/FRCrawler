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
        self.db_file = self.output_dir / "db_i.db"
        self.js_file = self.output_dir / "db_i.js"
        
        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export(self) -> None:
        """전체 내보내기 프로세스 실행"""
        try:
            self._to_sqlite()
            self._to_javascript()
            logger.info(f"✅ 내보내기 완료: {self.js_file}")
        except Exception as e:
            logger.error(f"내보내기 중 오류 발생: {str(e)}")
            raise
            
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
    DataFrame을 JavaScript 파일로 내보내는 편의 함수
    
    Args:
        df: 변환할 DataFrame
        output_dir: 출력 파일을 저장할 디렉토리
    """
    exporter = Exporter(df, output_dir)
    try:
        exporter.export()
    finally:
        exporter.cleanup()


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