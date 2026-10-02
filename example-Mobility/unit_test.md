🛴 스마트 모빌리티 파이프라인 단위 테스트 (Unit Test)

이 코드는 앞서 작성한 mobility_pipeline.py 모듈을 검증하기 위한 단위 테스트 스크립트입니다. 파이썬 내장 unittest와 unittest.mock을 사용하여 외부 AI API 의존성 없이 독립적으로 파이프라인의 분기 로직과 예외 처리를 테스트합니다.

import unittest
from unittest.mock import patch
from mobility_pipeline import process_parking_image, check_image_quality, ActionType

class TestMobilityPipeline(unittest.TestCase):
    
    def setUp(self):
        """테스트에 사용될 기본 유저 ID와 정상 이미지 데이터 설정"""
        self.user_id = "TEST_USER_01"
        self.normal_image = b"NORMAL_IMAGE"

    # ==========================================
    # 1. 전처리 필터 로직 테스트
    # ==========================================
    def test_image_quality_empty(self):
        """이미지 데이터가 없는 경우 반려되는지 테스트"""
        is_valid, reason = check_image_quality(b"")
        self.assertFalse(is_valid)
        self.assertIn("누락", reason)

    def test_image_quality_dark(self):
        """어두운 이미지(가림)가 반려되는지 테스트"""
        is_valid, reason = check_image_quality(b"DARK_IMAGE")
        self.assertFalse(is_valid)
        self.assertIn("어둡습니다", reason)

    # ==========================================
    # 2. 메인 파이프라인 분기 처리 테스트
    # ==========================================
    def test_process_rejected_image(self):
        """전처리에서 반려된 이미지가 올바른 상태값을 반환하는지 테스트"""
        result = process_parking_image(self.user_id, b"BLUR_IMAGE")
        self.assertEqual(result["status"], ActionType.IMAGE_REJECTED.value)
        self.assertIn("다시 촬영", result["message"])

    def test_process_penalty_applied(self):
        """신뢰도 85% 이상일 때 자동 페널티가 부과되는지 테스트"""
        result = process_parking_image(self.user_id, self.normal_image, override_confidence=0.88)
        self.assertEqual(result["status"], ActionType.PENALTY_APPLIED.value)
        self.assertEqual(result["confidence"], 88.0)

    def test_process_cs_review(self):
        """신뢰도 60~84% 사이일 때 CS 검수로 이관되는지 테스트"""
        # Edge case: 딱 60% 인 경우
        result_lower_bound = process_parking_image(self.user_id, self.normal_image, override_confidence=0.60)
        self.assertEqual(result_lower_bound["status"], ActionType.CS_REVIEW_REQUESTED.value)

        # Edge case: 84.9% 인 경우
        result_upper_bound = process_parking_image(self.user_id, self.normal_image, override_confidence=0.849)
        self.assertEqual(result_upper_bound["status"], ActionType.CS_REVIEW_REQUESTED.value)

    def test_process_retake_requested(self):
        """신뢰도 60% 미만일 때 재촬영을 요구하는지 테스트"""
        result = process_parking_image(self.user_id, self.normal_image, override_confidence=0.59)
        self.assertEqual(result["status"], ActionType.RETAKE_REQUESTED.value)

    # ==========================================
    # 3. 예외 처리(Fallback) 테스트
    # ==========================================
    @patch('mobility_pipeline.check_image_quality')
    def test_process_system_error(self, mock_check):
        """내부 로직 실행 중 예기치 못한 에러 발생 시 Fallback이 작동하는지 테스트"""
        # 강제로 예외(Exception)를 발생시키도록 Mocking 설정
        mock_check.side_effect = Exception("DB Connection Timeout")
        
        result = process_parking_image(self.user_id, self.normal_image)
        
        self.assertEqual(result["status"], ActionType.ERROR.value)
        self.assertIn("수동으로 주차 완료 처리", result["message"])

if __name__ == '__main__':
    unittest.main()


💡 해커톤 실전 활용 팁 (유형 3 대비)

경계값 분석 (Boundary Value Analysis): 테스트 코드 내 test_process_cs_review 함수처럼 0.60, 0.849 등 분기점이 되는 아슬아슬한 경계값을 의도적으로 테스트하여 로직의 견고함을 증명하세요.

Mocking을 활용한 장애 시뮬레이션: test_process_system_error 함수처럼 외부 API나 DB가 다운되었을 때 시스템이 멈추지 않고 안전망(Fallback)을 가동하는지를 보여주면 기술 점수가 크게 올라갑니다.
