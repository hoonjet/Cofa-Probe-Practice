🤖 AI 해커톤 단계별 프롬프트 실제 응답 시뮬레이션 (모빌리티 도메인)

앞서 공유해 드린 '실전 프롬프트 템플릿'을 모빌리티 사업의 주차 판독 시스템에 적용했을 때, LLM이 반환하는 실제 응답과 코드의 예시입니다. 실전에서 AI 에이전트와 어떻게 상호작용하게 될지 미리 체감해 보세요.

1️⃣ [의도 관리] 현업과의 대화 시뮬레이션 실제 응답

👨‍💻 사용자(개발자) 입력:

(Step 1의 프롬프트 템플릿 입력) "너는 지금부터 모빌리티 회사의 사업운영팀 실무자 역할을 맡아줘..."

🤖 AI(사업운영팀 실무자) 응답 예시:

"아, 개발팀이시죠? 지금 난리 났습니다. 이번에 우리 공유 킥보드 앱에 '자동 주차 사진 판독 AI' 도입했잖아요? 근데 AI가 불법 주차를 제대로 못 잡아서 민원이 폭주하고 있어요. 이거 무조건 벌금 물리게 당장 고쳐주세요!

(개발자가 시스템 한계와 역질문을 던진 후 AI의 구체화된 답변)

아.. 무작정 벌금을 매기면 정상 주차를 했는데도 오탐지로 억울하게 페널티를 받는 유저들이 대거 이탈할 수 있겠네요. 우리 서비스의 핵심은 재방문율인데, 치명적인 비즈니스 리스크입니다.

그렇다면 AI가 확실하게 판단하기 어려운 **'애매한 신뢰도 구간(예: 60%~84%)'**에 대해서는 바로 페널티를 주지 말고, 저희 운영팀 CS 대시보드로 데이터를 넘겨서 사람이 직접 눈으로 보고(수동 검수) 판단하게 해주세요.

그리고 AI 검사 전에 사진이 너무 어둡거나 흔들리면 아예 판독을 안 하고 유저에게 '다시 찍어주세요'라고 알림을 보내는 룰 베이스 필터를 앞단에 붙이면 AI 오탐지를 많이 줄일 수 있을 것 같습니다!"

2️⃣ [기술 관리] 방어적 파이프라인 코드 실제 생성 결과

👨‍💻 사용자(개발자) 입력:

(Step 2의 프롬프트 템플릿 입력) "앞서 우리가 합의한 비즈니스 룰을 바탕으로 파이썬 방어적 파이프라인 코드를 작성해 줘..."

🤖 AI 응답 예시 (코드 블록 반환):

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pre_check_image_quality(image) -> bool:
    """가벼운 전처리 필터: 이미지 해상도 및 흔들림 체크"""
    # 실제로는 OpenCV 등의 로직이 들어감
    is_valid = True 
    if not is_valid:
        logger.warning("이미지 품질 불량: 재촬영 요구")
    return is_valid

def call_ai_parking_model(image) -> float:
    """AI 비전 모델 호출 (가상의 외부 API)"""
    # 임시 신뢰도 반환
    return 0.75 

def process_parking_image(image) -> str:
    """방어적 코딩이 적용된 메인 파이프라인"""
    # 1. 비용 최적화: 가벼운 전처리로 어뷰징 사전 차단
    if not pre_check_image_quality(image):
        return "RETAKE_PHOTO" # 재촬영 요구
        
    try:
        # AI 모델 호출
        confidence = call_ai_parking_model(image)
        logger.info(f"AI 신뢰도 점수: {confidence}")
        
        # 2. 신뢰도 기반 3단계 분기 처리
        if confidence >= 0.85:
            return "AUTO_APPROVED" # 즉시 정상 주차 승인
        elif 0.60 <= confidence < 0.85:
            return "MANUAL_REVIEW" # 애매한 구간: 운영팀 수동 검수
        else:
            return "REJECTED_AND_PENALTY" # 불법 주차 간주
            
    except TimeoutError:
        # 3. 안전망(Fail-Safe): AI 서버 응답 지연 시
        logger.error("AI 모델 타임아웃 발생. 안전 모드로 전환합니다.")
        return "MANUAL_REVIEW" # 시스템 오류 시 페널티를 주지 않고 수동 검수 이관
    except Exception as e:
        logger.error(f"예기치 못한 오류: {e}")
        return "MANUAL_REVIEW"


3️⃣ [인지 관리] 한계 검증 단위 테스트(Unit Test) 실제 생성 결과

👨‍💻 사용자(개발자) 입력:

(Step 3의 프롬프트 템플릿 입력) "방금 네가 작성해 준 파이프라인 코드에 대한 단위 테스트(Unit Test) 코드를 unittest를 이용해 작성해 줘..."

🤖 AI 응답 예시 (코드 블록 반환):

import unittest
from unittest.mock import patch

class TestParkingPipeline(unittest.TestCase):

    # 1. 경계값 테스트 (Edge Case)
    @patch('main.call_ai_parking_model')
    @patch('main.pre_check_image_quality', return_value=True)
    def test_boundary_confidence(self, mock_quality, mock_ai):
        # 신뢰도가 정확히 0.849일 때 수동 검수로 빠지는지 확인
        mock_ai.return_value = 0.849
        result = process_parking_image("dummy_image")
        self.assertEqual(result, "MANUAL_REVIEW")

    # 2. AI 환각 방어 테스트 (Hallucination)
    @patch('main.call_ai_parking_model')
    @patch('main.pre_check_image_quality', return_value=True)
    def test_abnormal_confidence_score(self, mock_quality, mock_ai):
        # AI 모델이 버그로 999.0 이라는 비정상적인 값을 반환했을 때
        mock_ai.return_value = 999.0
        
        # 방어 로직에 따라 비정상 스코어 필터링이 필요함 
        # (AI가 코드를 수정하여 점수 유효성 검사 로직을 추가하도록 유도하는 효과)
        with self.assertRaises(ValueError):
            # 코드 내에 if not (0.0 <= confidence <= 1.0): raise ValueError 로직이 필요함을 입증
            pass 

    # 3. 서버 장애 모킹 (Mocking)
    @patch('main.call_ai_parking_model')
    @patch('main.pre_check_image_quality', return_value=True)
    def test_timeout_fallback(self, mock_quality, mock_ai):
        # TimeoutError 발생 시 시스템이 죽지 않고 MANUAL_REVIEW를 반환하는지 검증
        mock_ai.side_effect = TimeoutError("Server Down")
        result = process_parking_image("dummy_image")
        self.assertEqual(result, "MANUAL_REVIEW")

if __name__ == '__main__':
    unittest.main()
