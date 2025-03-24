# FRCrawler (FinReg Crawler)
금융법령해석 웹크롤러

## v0.0.3 DD 250325

#### History
v0.0.3 유닛2 추가  

## Unit 1. 최근법령해석

### Package 
late

### 실행예시
python -m late.main --max-items 100 --max-workers 10 --delay 0.3

## Unit 2. 과거법령해석

### Package
past

### 실행예시
#### 전체 크롤링
python -m past.main

#### 최대 100개 항목만 크롤링
python -m past.main --max-items 100

#### 병렬 처리 및 지연 시간 조정
python -m past.main --max-workers 10 --delay 0.3

#### 목록만 크롤링
python -m past.main --list-only

#### pickle 파일에서 로드
python -m past.main --load-pickle past_crawling_result.pkl