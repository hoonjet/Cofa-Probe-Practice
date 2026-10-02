🚀 [유형 2] 비즈니스 도메인 결합 AI 기능 구현 (기술 관리)

이 문서는 [유형 1]에서 도출한 기술 명세서를 바탕으로, 오류가 발생하지 않는 견고한 파이프라인 코드를 AI와 함께 구현하는 단계별 가이드입니다.

💡 단계 1: 방어적 코딩 및 모듈화 원칙이 적용된 코드 초안 요청하기

단순히 "코드를 짜줘"가 아니라, 엔지니어링 원칙(Error Handling, SRP)을 강제하여 AI가 신뢰성 높은 코드를 작성하도록 유도합니다.

[사용자 프롬프트 입력]

# Role
너는 시스템 장애를 절대 용납하지 않는 글로벌 탑티어 파이썬 시니어 백엔드 엔지니어이다.

# Context
앞서 정의한 요구사항(일일 10만 건 CSV 로그 파싱, PDF 매뉴얼 기준 에러 분류, 슬랙 요약 보고서 발송)을 바탕으로 파이썬 파이프라인 모듈을 개발하려고 한다.

# Instructions
1. 거대한 함수 하나로 짜지 말고, 단일 책임 원칙(SRP)에 따라 클래스와 메서드를 모듈화하라.
2. [필수] 모든 파일 읽기 및 API 호출 부분에는 반드시 `try-except` 예외 처리와 `logging` 모듈을 활용한 로그 기록을 포함하라.
3. 존재하지 않는 가상의 외부 라이브러리(Hallucination)를 사용하지 말고, `pandas`와 내장 표준 라이브러리만 사용하라.
4. 우선 '데이터 로드 및 결측치 전처리' 부분을 담당하는 클래스 코드 초안만 작성하라.


<!-- 
💡 [주의 및 핵심 포인트 - 기술 관리]
- 이 단계의 핵심은 '제약 조건(Constraints)의 명시'입니다. AI가 멋대로 코드를 짜지 않도록 예외 처리, 모듈화, 사용할 라이브러리를 제한하는 모습을 보여주어야 높은 기술 관리 점수를 받습니다.
- 한 번에 전체 파이프라인을 다 짜라고 하면 코드가 누락될 수 있으므로, 핵심 모듈부터 순차적으로 요청하는 것이 좋습니다.
-->


💬 단계 2: AI의 코드 생성 및 디버깅 시뮬레이션

[AI 응답 시뮬레이션 (파이썬 시니어 엔지니어)]

"명시해주신 원칙에 따라, 안전하게 데이터를 로드하고 결측치를 처리하는 LogProcessor 클래스 초안을 작성했습니다. 예외 처리와 로깅을 꼼꼼히 적용했습니다."

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogProcessor")

class LogProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_and_clean_data(self) -> pd.DataFrame:
        try:
            logger.info(f"데이터 로드 시도: {self.file_path}")
            df = pd.read_csv(self.file_path)
            
            # 결측치 처리 로직
            if df.isnull().values.any():
                logger.warning("결측치 발견, 전방 보간법(ffill)으로 처리합니다.")
                df = df.ffill()
                
            return df
            
        except FileNotFoundError:
            logger.error("파일을 찾을 수 없습니다. 경로를 확인해주세요.")
            raise
        except pd.errors.EmptyDataError:
            logger.error("CSV 파일이 비어있습니다.")
            raise
        except Exception as e:
            logger.error(f"알 수 없는 오류 발생: {e}")
            raise


[사용자 프롬프트 입력 (추가 엣지 케이스 대응)]

좋은 코드야. 하지만 현장에서는 센서 통신 불량으로 파일 자체가 중간에 끊기거나, 'Err' 같은 문자열이 섞여 들어올 수도 있어. 
위 코드의 `load_and_clean_data` 메서드에 'Err' 문자열을 NaN으로 치환하는 로직과, 3행 이상 연속으로 결측치가 발생하면 ffill 대신 에러 로그를 남기고 해당 데이터를 버리는(Drop) 방어 로직을 추가해 줘.


<!-- 
💡 [주의 및 핵심 포인트 - 에러 핸들링 고도화]
- AI가 생성한 1차 코드를 그대로 쓰지 말고, 현장의 특수한 '악조건(Edge Case)'을 부여하여 코드를 고도화(Refactoring)하는 지시를 내리세요.
- Cofa-Probe는 참가자가 코드를 어떻게 발전시켜 나가는지의 과정(History)을 추적합니다.
-->
