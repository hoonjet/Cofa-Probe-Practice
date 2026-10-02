🤖 AI 해커톤 단계별 프롬프트 실제 응답 시뮬레이션 (의료 도메인)

응급실(ER) 환자 분류(Triage) 시스템에 AI를 도입했을 때 발생할 수 있는 치명적인 리스크를 방어하고, 전문의와 AI가 협력하는 파이프라인을 구축하는 과정에 대한 LLM의 실제 응답과 코드 예시입니다.

1️⃣ [의도 관리] 현업과의 대화 시뮬레이션 실제 응답

👨‍💻 사용자(개발자) 입력:

(Step 1의 프롬프트 템플릿 입력) "너는 지금부터 대학병원 응급실(ER) 환자 분류(Triage) AI 시스템 운영팀 실무자 역할을 맡아줘..."

🤖 AI(운영팀 실무자) 응답 예시:

"아, 개발팀이시죠? 지금 응급실 현장에서 난리가 났습니다. 이번에 도입한 'AI 응급도 자동 분류 모델'이 중증 환자를 경증으로 잘못 판단해서 응급 환자가 대기실에 방치되는 아찔한 사건이 발생할 뻔했어요. 의사 선생님들도 이 AI 못 믿겠다고 시스템을 끄라고 하시네요. AI가 무조건 100% 빠르고 정확하게 환자를 분류하도록 당장 고쳐주세요!"

(개발자가 AI의 100% 완벽성은 불가능함을 알리며, 생명과 직결된 리스크를 방어하기 위한 역질문을 던진 후 AI의 구체화된 답변)

"아... 제가 AI의 정확도가 100%일 수 없다는 사실을 간과했네요. 무작정 AI에게만 맡겼다가 골든타임을 놓치면 치명적인 의료 사고(비즈니스 리스크)로 이어질 수밖에 없겠습니다.

그렇다면 AI가 중증도를 확신하지 못하는 **'애매한 중증 확률 구간(예: 40%~75%)'**에 해당하는 환자이거나, 입력된 바이탈 데이터가 부족할 경우에는 절대 대기실로 보내지 말고 즉시 '전문의 수동 재진단(Require Doctor Review)' 알림을 띄우게 해주세요.

그리고, AI 판단을 기다릴 필요도 없이 산소포화도(SpO2)가 90% 미만이거나 심박수가 130 이상인 환자는 룰 베이스 필터를 적용해서 무조건 최우선 응급 코드(Code Red)를 부여하는 안전장치도 만들어 주시면 안심이 될 것 같습니다!"

2️⃣ [기술 관리] 방어적 파이프라인 코드 실제 생성 결과

👨‍💻 사용자(개발자) 입력:

(Step 2의 프롬프트 템플릿 입력) "앞서 우리가 합의한 비즈니스 룰(위험 수치 프리패스, 신뢰도 구간 분기, 전문의 폴백 안전망)을 바탕으로 파이썬 방어적 파이프라인 코드를 작성해 줘..."

🤖 AI 응답 예시 (코드 블록 반환):

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pre_check_critical_vitals(patient_data) -> bool:
    """가벼운 전처리 필터: 생명 위협 수치 즉각 판별 (룰 베이스)"""
    spo2 = patient_data.get('spo2', 100)
    heart_rate = patient_data.get('heart_rate', 70)

    if spo2 < 90 or heart_rate >= 130:
        logger.critical("🚨 치명적 바이탈 감지: AI 검사 생략, 즉각 응급 처리!")
        return True
    return False

def call_ai_triage_model(patient_data) -> float:
    """AI 환자 중증도 예측 모델 호출 (가상의 외부 API)"""
    # 임시 중증도 점수(Severity Score) 반환
    return 0.60 

def process_patient_triage(patient_data) -> str:
    """방어적 코딩(Fail-Safe)이 적용된 응급실 환자 분류 파이프라인"""
    # 1. 룰 베이스 사전 통과 (골든타임 확보)
    if pre_check_critical_vitals(patient_data):
        return "CODE_RED" # 즉시 최우선 응급 조치

    try:
        # AI 모델 호출
        severity_score = call_ai_triage_model(patient_data)
        logger.info(f"AI 중증도 예측 점수: {severity_score}")

        # 2. 확률 기반 3단계 분기 처리
        if severity_score >= 0.75:
            return "CODE_RED" # 명백한 중증 환자
        elif 0.40 <= severity_score < 0.75:
            return "REQUIRE_DOCTOR_REVIEW" # 애매한 구간: 전문의 수동 재진단 호출
        else:
            return "WAITING_ROOM" # 경증: 일반 대기

    except TimeoutError:
        # 3. 안전망(Fail-Safe): AI 서버 다운 시 무조건 의사에게 이관 (생명 보호)
        logger.error("AI 모델 응답 지연. 안전을 위해 전문의 진단 모드로 전환합니다.")
        return "REQUIRE_DOCTOR_REVIEW" 
    except Exception as e:
        logger.error(f"분류 시스템 예기치 못한 오류: {e}")
        return "REQUIRE_DOCTOR_REVIEW" # 시스템 오류 시 절대 경증으로 임의 분류 금지


3️⃣ [인지 관리] 한계 검증 단위 테스트(Unit Test) 실제 생성 결과

👨‍💻 사용자(개발자) 입력:

(Step 3의 프롬프트 템플릿 입력) "방금 네가 작성해 준 의료 Triage 파이프라인 코드에 대해 발생 가능한 엣지 케이스와 시스템 장애 상황을 모두 검증하는 단위 테스트 코드를 작성해 줘..."

🤖 AI 응답 예시 (코드 블록 반환):

import unittest
from unittest.mock import patch

class TestMedicalTriagePipeline(unittest.TestCase):

    # 1. 룰 베이스 경계값 테스트 (골든타임 필터)
    def test_pre_check_critical_vitals(self):
        # SpO2가 89%인 치명적 상태 시 AI 호출 없이 즉시 CODE_RED가 되는지 확인
        critical_patient = {'spo2': 89, 'heart_rate': 80}
        result = process_patient_triage(critical_patient)
        self.assertEqual(result, "CODE_RED")

    # 2. 경계값 신뢰도 테스트 (AI 응답 분기)
    @patch('main.call_ai_triage_model')
    @patch('main.pre_check_critical_vitals', return_value=False)
    def test_boundary_severity_score(self, mock_precheck, mock_ai):
        # 중증도 점수가 애매한 경계인 0.749일 때 의사 리뷰로 넘어가는지 확인
        mock_ai.return_value = 0.749
        result = process_patient_triage({'spo2': 98, 'heart_rate': 75})
        self.assertEqual(result, "REQUIRE_DOCTOR_REVIEW")

    # 3. 데이터 누락 및 AI 환각 방어 테스트
    @patch('main.call_ai_triage_model')
    @patch('main.pre_check_critical_vitals', return_value=False)
    def test_missing_vitals_handling(self, mock_precheck, mock_ai):
        # AI 모델이 비정상적인 음수 값을 반환했을 때 (환각 현상)
        mock_ai.return_value = -0.1

        # 개발자가 코드 내에 예외 처리를 구현하도록 강제하는 테스트
        with self.assertRaises(ValueError):
            # 이 테스트를 통과하기 위해 본 코드에 score < 0.0 검증 로직이 추가되어야 함
            pass 

    # 4. 서버 장애 모킹 (Fail-Safe 핵심)
    @patch('main.call_ai_triage_model')
    @patch('main.pre_check_critical_vitals', return_value=False)
    def test_timeout_fallback(self, mock_precheck, mock_ai):
        # TimeoutError 발생 시 환자를 대기실(WAITING_ROOM)로 방치하지 않고 의사에게 이관하는지 철저히 검증
        mock_ai.side_effect = TimeoutError("AI Server Down")
        result = process_patient_triage({'spo2': 98, 'heart_rate': 75})
        self.assertEqual(result, "REQUIRE_DOCTOR_REVIEW")

if __name__ == '__main__':
    unittest.main()
