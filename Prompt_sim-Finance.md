🤖 AI 해커톤 단계별 프롬프트 실제 응답 시뮬레이션 (금융 도메인)

앞서 공유해 드린 '실전 프롬프트 템플릿'을 금융 회사의 신용카드 이상거래 탐지(FDS) 시스템에 적용했을 때, LLM이 반환하는 실제 응답과 코드의 예시입니다. 엄격한 보안과 고객 편의성의 밸런스를 맞추는 과정에 집중해 보세요.

1️⃣ [의도 관리] 현업과의 대화 시뮬레이션 실제 응답

👨‍💻 사용자(개발자) 입력:

(Step 1의 프롬프트 템플릿 입력) "너는 지금부터 금융 회사의 FDS(이상거래탐지) 운영팀 실무자 역할을 맡아줘..."

🤖 AI(운영팀 실무자) 응답 예시:

"아, 개발팀이시죠? 지금 VIP 고객들 민원이 엄청납니다. 이번에 도입한 AI가 고객이 해외 출장 가서 결제하는 정상적인 호텔비나 식대를 자꾸 '도난 카드'로 인식하고 무조건 결제를 차단해 버리고 있어요. 이거 고객들이 화나서 카드 다 해지하겠다고 난리니까, 차단 안 되게 당장 고쳐주세요!

(개발자가 무조건 통과 시의 금전적 리스크를 짚으며 역질문을 던진 후 AI의 구체화된 답변)

아.. 무작정 다 통과시키면 실제 카드 도용 범죄가 발생했을 때 회사가 물어내야 할 엄청난 금전적 손실(비즈니스 리스크)이 발생하겠네요. 그렇다고 억울한 VIP 고객을 잃을 수도 없고...

그렇다면 AI가 사기 결제라고 확신하기 어려운 **'애매한 사기 확률 구간(예: 50%~85%)'**에 대해서는 무조건 결제 차단을 하지 말고, 고객의 앱이나 문자로 본인 인증 알림(ARS/생체인증)을 즉시 보내서 고객이 직접 승인하게 해주세요.

그리고 결제 금액이 5만 원 이하의 소액이면서 자주 가는 가맹점이라면, 룰 베이스 필터로 AI 판독 전에 바로 통과시키면 오탐지 민원을 훨씬 줄일 수 있을 것 같습니다!"

2️⃣ [기술 관리] 방어적 파이프라인 코드 실제 생성 결과

👨‍💻 사용자(개발자) 입력:

(Step 2의 프롬프트 템플릿 입력) "앞서 우리가 합의한 비즈니스 룰(소액결제 프리패스, 신뢰도 구간 분기, 본인 인증 폴백)을 바탕으로 파이썬 방어적 파이프라인 코드를 작성해 줘..."

🤖 AI 응답 예시 (코드 블록 반환):

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pre_check_safe_transaction(transaction_data) -> bool:
    """가벼운 전처리 필터: 5만 원 이하 소액 및 단골 가맹점 여부"""
    amount = transaction_data.get('amount', 0)
    is_frequent_merchant = transaction_data.get('is_frequent', False)
    
    if amount <= 50000 and is_frequent_merchant:
        logger.info("안전한 소액 결제: AI 검사 생략")
        return True
    return False

def call_ai_fraud_model(transaction_data) -> float:
    """AI 이상거래 탐지 모델 호출 (가상의 외부 API)"""
    # 임시 사기 확률(Fraud Probability) 반환
    return 0.70 

def process_transaction(transaction_data) -> str:
    """방어적 코딩이 적용된 결제 승인 파이프라인"""
    # 1. 룰 베이스 사전 통과 (비용 및 지연시간 최적화)
    if pre_check_safe_transaction(transaction_data):
        return "APPROVED" # 즉시 승인

    try:
        # AI 모델 호출
        fraud_prob = call_ai_fraud_model(transaction_data)
        logger.info(f"AI 사기 확률: {fraud_prob}")

        # 2. 확률 기반 3단계 분기 처리
        if fraud_prob < 0.50:
            return "APPROVED" # 정상 거래 승인
        elif 0.50 <= fraud_prob < 0.85:
            return "REQUIRE_USER_AUTH" # 애매한 구간: 고객 본인 인증(ARS/앱) 요구
        else:
            return "BLOCKED" # 명백한 사기 의심: 즉시 차단

    except TimeoutError:
        # 3. 안전망(Fail-Safe): AI 서버 다운 시 무작정 차단 방지
        logger.error("AI 모델 응답 지연. 안전을 위해 고객 인증 모드로 전환합니다.")
        return "REQUIRE_USER_AUTH" 
    except Exception as e:
        logger.error(f"결제 시스템 예기치 못한 오류: {e}")
        return "REQUIRE_USER_AUTH" # 에러 상황에서도 결제 거절보다 인증 기회 부여


3️⃣ [인지 관리] 한계 검증 단위 테스트(Unit Test) 실제 생성 결과

👨‍💻 사용자(개발자) 입력:

(Step 3의 프롬프트 템플릿 입력) "방금 네가 작성해 준 금융 FDS 파이프라인 코드에 대해 발생 가능한 엣지 케이스를 모두 검증하는 단위 테스트 코드를 작성해 줘..."

🤖 AI 응답 예시 (코드 블록 반환):

import unittest
from unittest.mock import patch

class TestFraudPipeline(unittest.TestCase):

    # 1. 룰 베이스 경계값 테스트 (Edge Case)
    def test_pre_check_safe_transaction_boundary(self):
        # 50,000원 이하 단골 결제 통과 확인
        safe_txn = {'amount': 50000, 'is_frequent': True}
        result = process_transaction(safe_txn)
        self.assertEqual(result, "APPROVED")

    # 2. 경계값 신뢰도 테스트 (AI 응답 분기)
    @patch('main.call_ai_fraud_model')
    @patch('main.pre_check_safe_transaction', return_value=False)
    def test_boundary_fraud_prob(self, mock_precheck, mock_ai):
        # 사기 확률이 정확히 0.499일 때 즉시 승인되는지 확인
        mock_ai.return_value = 0.499
        result = process_transaction({'amount': 500000})
        self.assertEqual(result, "APPROVED")

    # 3. AI 환각 및 비정상 값 방어 테스트 (Hallucination)
    @patch('main.call_ai_fraud_model')
    @patch('main.pre_check_safe_transaction', return_value=False)
    def test_abnormal_fraud_score(self, mock_precheck, mock_ai):
        # AI 모델이 오류로 음수(-0.5)나 1을 초과하는 값을 반환했을 때
        mock_ai.return_value = -0.5

        # 코드 내에 0.0~1.0 사이 값인지 검증하는 방어 로직이 필요함을 입증
        with self.assertRaises(ValueError):
            # 개발자는 이 테스트를 통과시키기 위해 본 코드에 유효성 검사를 추가해야 함
            pass 

    # 4. 서버 장애 모킹 (Mocking)
    @patch('main.call_ai_fraud_model')
    @patch('main.pre_check_safe_transaction', return_value=False)
    def test_timeout_fallback(self, mock_precheck, mock_ai):
        # TimeoutError 발생 시 고객의 결제 기회를 박탈하지 않고 인증(AUTH)으로 넘어가는지 검증
        mock_ai.side_effect = TimeoutError("FDS Server Down")
        result = process_transaction({'amount': 500000})
        self.assertEqual(result, "REQUIRE_USER_AUTH")

if __name__ == '__main__':
    unittest.main()
