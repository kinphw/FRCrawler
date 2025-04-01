# 법령해석/비조치의견서, 과거비조치의견, 현장점검의견 3개를 합쳐서 lq용 df로 변환하는 파일
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class Harmonizer:
    """데이터프레임 조화 및 통합 클래스"""

    def __init__(self, past_df: pd.DataFrame, late_df: pd.DataFrame, integ_df: pd.DataFrame, **kwargs):
        """
        Harmonizer 클래스 초기화
        
        Args:
            past_df: 과거회신사례 데이터프레임
            late_df: 법령해석/비조치의견서 데이터프레임
            integ_df: 현장점검의견 데이터프레임
            **kwargs: 추가 매개변수
        """
        self.past_df = past_df.copy() if past_df is not None else pd.DataFrame()
        self.late_df = late_df.copy() if late_df is not None else pd.DataFrame()
        self.integ_df = integ_df.copy() if integ_df is not None else pd.DataFrame()
        
        # 로깅 설정
        self._setup_logging()
        
        # 데이터프레임 확인
        self._validate_dataframes()

    def _setup_logging(self):
        """로깅 설정"""
        logger.info(f"Harmonizer 초기화: past_df={len(self.past_df)}행, late_df={len(self.late_df)}행, integ_df={len(self.integ_df)}행")

    def _validate_dataframes(self):
        """데이터프레임 유효성 검증"""
        for name, df in [("past_df", self.past_df), ("late_df", self.late_df), ("integ_df", self.integ_df)]:
            if df.empty:
                logger.warning(f"{name} 데이터프레임이 비어 있습니다.")
            else:
                logger.info(f"{name} 컬럼: {list(df.columns)}")

    def run(self) -> pd.DataFrame:
        """
        Harmonizer 실행 메서드
        
        Returns:
            pd.DataFrame: 통합된 DataFrame
        """
        # 각 데이터프레임 전처리
        logger.info("데이터프레임 전처리 시작...")
        
        past_processed = self._process_past_df()
        late_processed = self._process_late_df()
        integ_processed = self._process_integ_df()
        
        # 데이터프레임 병합
        logger.info("데이터프레임 병합...")
        merged_df = self._merge_dataframes(past_processed, late_processed, integ_processed)
        
        # ID 부여 및 최종 정리
        logger.info("최종 정리 및 ID 부여...")
        final_df = self._finalize_dataframe(merged_df)
        
        logger.info(f"처리 완료: 최종 {len(final_df)}개 항목")
        return final_df

    def _process_past_df(self) -> pd.DataFrame:
        """
        past_df 전처리
        
        Returns:
            pd.DataFrame: 전처리된 past_df
        """
        if self.past_df.empty:
            return pd.DataFrame(columns=self._get_standard_columns())
            
        logger.info("past_df 처리 중...")
        df = self.past_df.copy()
        
        # 컬럼 매핑
        df_mapped = pd.DataFrame()
        
        # 기본 컬럼 매핑
        df_mapped['구분'] = df['pastreqType']
        df_mapped['분야'] = np.nan  # 해당 정보 없음
        df_mapped['제목'] = df['pastreqSubject']
        df_mapped['회신부서'] = np.nan  # 해당 정보 없음
        df_mapped['담당자'] = np.nan  # 해당 정보 없음
        df_mapped['회신일자'] = df['regDate']
        df_mapped['일련번호'] = df['serialNum']
        
        # 복합 필드 생성
        df_mapped['질의요지'] = df.apply(
            lambda row: self._combine_fields([
                row.get('inquiry', ''),
                row.get('fact', ''),
                row.get('baseLaw', '')
            ]), axis=1
        )
        
        df_mapped['회답'] = df.apply(
            lambda row: self._combine_fields([
                row.get('answer', '')
            ]), axis=1
        )
        
        df_mapped['이유'] = df.apply(
            lambda row: self._combine_fields([
                row.get('reason', '')
            ]), axis=1
        )
        
        # 소스 표시
        df_mapped['source'] = 'past'
        
        # 디버그 로깅
        logger.debug(f"past_df 처리 완료: {len(df_mapped)}행")
        
        return df_mapped
    
    def _process_late_df(self) -> pd.DataFrame:
        """
        late_df 전처리
        
        Returns:
            pd.DataFrame: 전처리된 late_df
        """
        if self.late_df.empty:
            return pd.DataFrame(columns=self._get_standard_columns())
            
        logger.info("late_df 처리 중...")
        df = self.late_df.copy()
        
        # 컬럼 매핑
        df_mapped = pd.DataFrame()
        
        # 기본 컬럼 매핑
        df_mapped['구분'] = df['gubun']
        df_mapped['분야'] = df['category']
        df_mapped['제목'] = df['list_title']
        df_mapped['회신부서'] = df['registrant']
        df_mapped['담당자'] = np.nan  # 해당 정보 없음
        df_mapped['회신일자'] = df['reply_date']
        df_mapped['일련번호'] = df['number']
        
        # 복합 필드 생성
        df_mapped['질의요지'] = df['inquiry']
        
        df_mapped['회답'] = df.apply(
            lambda row: self._combine_fields([
                row.get('answer', '')
            ]), axis=1
        )
        
        df_mapped['이유'] = df.apply(
            lambda row: self._combine_fields([
                row.get('reason', '')
            ]), axis=1
        )
        
        # 소스 표시
        df_mapped['source'] = 'late'
        
        # 디버그 로깅
        logger.debug(f"late_df 처리 완료: {len(df_mapped)}행")
        
        return df_mapped

    def _process_integ_df(self) -> pd.DataFrame:
        """
        integ_df 전처리
        
        Returns:
            pd.DataFrame: 전처리된 integ_df
        """
        if self.integ_df.empty:
            return pd.DataFrame(columns=self._get_standard_columns())
            
        logger.info("integ_df 처리 중...")
        df = self.integ_df.copy()
        
        # 컬럼 매핑
        df_mapped = pd.DataFrame()
        
        # 기본 컬럼 매핑
        df_mapped['구분'] = df['pastreqType']
        df_mapped['분야'] = df['category']
        df_mapped['제목'] = df['list_title']
        df_mapped['회신부서'] = np.nan  # 해당 정보 없음
        df_mapped['담당자'] = np.nan  # 해당 정보 없음
        df_mapped['회신일자'] = df['reply_date']
        df_mapped['일련번호'] = df['dataIdx']
        
        # 복합 필드 생성
        df_mapped['질의요지'] = df['inquiry']
        
        df_mapped['회답'] = df.apply(
            lambda row: self._combine_fields([
                row.get('answer_conclusion', ''),
                row.get('answer_content', '')
            ]), axis=1
        )
        
        df_mapped['이유'] = df.apply(
            lambda row: self._combine_fields([
                row.get('plan', '')
            ]), axis=1
        )
        
        # 소스 표시
        df_mapped['source'] = 'integ'
        
        # 디버그 로깅
        logger.debug(f"integ_df 처리 완료: {len(df_mapped)}행")
        
        return df_mapped

    def _merge_dataframes(self, past_df: pd.DataFrame, late_df: pd.DataFrame, integ_df: pd.DataFrame) -> pd.DataFrame:
        """
        데이터프레임 병합
        
        Args:
            past_df: 전처리된 past_df
            late_df: 전처리된 late_df
            integ_df: 전처리된 integ_df
            
        Returns:
            pd.DataFrame: 병합된 DataFrame
        """
        # 공통 컬럼 확인
        standard_columns = self._get_standard_columns()
        
        # 각 DataFrame에 공통 컬럼이 있는지 확인하고 조정
        for df, name in [(past_df, 'past'), (late_df, 'late'), (integ_df, 'integ')]:
            for col in standard_columns:
                if col not in df.columns:
                    logger.warning(f"{name} 데이터프레임에 '{col}' 컬럼이 없습니다. 빈 값으로 추가합니다.")
                    df[col] = np.nan
        
        # 모든 DataFrame 병합
        merged_df = pd.concat([past_df, late_df, integ_df], ignore_index=True)
        logger.info(f"병합된 데이터프레임: {len(merged_df)}행")
        
        return merged_df

    def _finalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        최종 데이터프레임 정리
        
        Args:
            df: 병합된 DataFrame
            
        Returns:
            pd.DataFrame: 정리된 최종 DataFrame
        """
        # 회신일자 형식 표준화
        if '회신일자' in df.columns:
            df['회신일자'] = pd.to_datetime(df['회신일자'], errors='coerce')
            
            # 회신일자 있는/없는 데이터 분리
            df_with_date = df[df['회신일자'].notna()].copy()
            df_no_date = df[df['회신일자'].isna()].copy()
            
            # 회신일자 있는 데이터만 정렬
            df_with_date = df_with_date.sort_values(by='회신일자')
            
            # 다시 합치기 (회신일자 없는 데이터는 마지막에)
            df = pd.concat([df_with_date, df_no_date]).reset_index(drop=True)
        
        # ID 부여
        df.insert(0, 'id', range(1, len(df) + 1))
        
        # source 컬럼 제거 (필요 없는 경우)
        if 'source' in df.columns:
            df = df.drop('source', axis=1)
        
        # NA 값 빈 문자열로 변경
        df = df.fillna('')
        
        return df

    def _combine_fields(self, fields: List[str]) -> str:
        """
        여러 필드를 하나로 결합
        
        Args:
            fields: 결합할 필드 값 목록
            
        Returns:
            str: 결합된 텍스트
        """
        # None 필터링 및 빈 문자열 처리
        valid_fields = [str(f).strip() for f in fields if f is not None and str(f).strip()]
        
        if not valid_fields:
            return ""
        
        # 구분자로 결합
        return "\n\n".join(valid_fields)

    def _get_standard_columns(self) -> List[str]:
        """표준 컬럼 목록 반환"""
        return [
            '구분', '분야', '제목', '회신부서', '담당자', '회신일자', '일련번호', 
            '질의요지', '회답', '이유', 'source'
        ]


if __name__ == "__main__":
    # 테스트 용도
    
    past_df = pd.read_pickle("past_df.pkl")
    late_df = pd.read_pickle("late_df.pkl")
    integ_df = pd.read_pickle("integ_df.pkl")

    result_df = Harmonizer(
        past_df=past_df, 
        late_df=late_df, 
        integ_df=integ_df
    ).run()

    import pandasgui as pg
    pg.show(result_df)


    
    