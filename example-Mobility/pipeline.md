🛴 스마트 모빌리티 자동 주차 판독 파이프라인 (Python)

앞서 정의한 요구사항(전처리 필터 및 신뢰도 기반 3단계 분기 처리)을 반영한 파이썬 모듈입니다. 해커톤 환경(유형 2)에서 높은 평가를 받을 수 있도록 **예외 처리(Exception Handling)**와 모듈화에 신경을 썼습니다.

import logging
from enum import Enum
from typing import Dict, Any, Tuple

# 로깅 설정 (실전에서는 Datadog 등 모니터링 툴과 연동할 수 있도록 구성)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class ActionType(Enum):
    PENALTY_APPLIED = "PENALTY_APPLIED"         # 페널티 부과
    CS_REVIEW_REQUESTED = "CS_REVIEW_REQUESTED" # 수동 검수 이관
    RETAKE_REQUESTED = "RETAKE_REQUESTED"       # 재촬영 요청
    IMAGE_REJECTED = "IMAGE_REJECTED"           # 품질 미달 반려
    ERROR = "ERROR"                             # 시스템 에러

def check_image_quality(image_data: bytes) -> Tuple[bool, str]:
    """
    [전처리] 이미지 품질 검사 (가상 구현)
    - 어뷰징 방지: 너무 어둡거나(렌즈 가림) 심하게 흔들린(블러) 사진을 1차 필터링
    - 목적: 불필요한 AI API 호출 비용(GPU 연산) 절감 및 처리 속도 향상
    """
    if not image_data:
        return False, "이미지 데이터가 누락되었습니다."
    
    # 예시용 가상 필터 로직 (실제로는 OpenCV의 cv2.Laplacian, cv2.mean 등 사용)
    if image_data == b"DARK_IMAGE":
        return False, "명암비 미달: 카메라 렌즈가 가려졌거나 너무 어둡습니다."
    if image_data == b"BLUR_IMAGE":
        return False, "블러 초과: 사진이 너무 흔들렸습니다."
        
    return True, "정상 품질 이미지"

def analyze_parking_image(image_data: bytes) -> float:
    """
    [AI 비전 모델] 불법 주차 구역 탐지 모델 (가상 API)
    - 반환값: 불법 주차일 확률 (Confidence Score, 0.0 ~ 1.0)
    """
    # 실제 환경에서는 requests.post() 등을 통해 AI 추론 서버에 요청
    # 타임아웃이나 서버 다운 등의 예외가 발생할 수 있음을 가정해야 함
    pass 

def process_parking_image(user_id: str, image_data: bytes, override_confidence: float = None) -> Dict[str, Any]:
    """
    [메인 파이프라인] 주차 사진 판독 및 비즈니스 분기 로직 처리
    """
    logger.info(f"[{user_id}] 주차 사진 판독 파이프라인 시작")
    
    # 1. 이미지 전처리 필터링 (가드레일 1)
    is_valid, reason = check_image_quality(image_data)
    if not is_valid:
        logger.warning(f"[{user_id}] 이미지 반려: {reason}")
        return {
            "status": ActionType.IMAGE_REJECTED.value, 
            "message": f"사진을 다시 촬영해주세요. 사유: {reason}"
        }
        
    try:
        # 2. AI 모델 판독 (테스트 용이를 위해 override_confidence 지원)
        confidence = override_confidence if override_confidence is not None else 0.0 
        confidence_pct = confidence * 100
        logger.info(f"[{user_id}] AI 불법주차 판독 신뢰도: {confidence_pct:.1f}%")
        
        # 3. 신뢰도 기반 3단계 분기 처리 (가드레일 2)
        if confidence_pct >= 85.0:
            logger.error(f"[{user_id}] 확실한 불법 주차 감지! 자동 페널티 부과.")
            return {
                "status": ActionType.PENALTY_APPLIED.value, 
                "confidence": confidence_pct,
                "message": "불법 주차 구역(횡단보도 등)으로 확인되어 페널티(이용 제한)가 부과되었습니다."
            }
        elif 60.0 <= confidence_pct < 85.0:
            logger.warning(f"[{user_id}] 애매한 주차 구역(신뢰도 60~84%). CS 대시보드로 이관.")
            return {
                "status": ActionType.CS_REVIEW_REQUESTED.value,
                "confidence": confidence_pct,
                "message": "안전 구역 확인을 위해 관리자가 사진을 꼼꼼히 검수 중입니다."
            }
        else:
            logger.info(f"[{user_id}] 판독 불가(신뢰도 60% 미만). 재촬영 요구.")
            return {
                "status": ActionType.RETAKE_REQUESTED.value,
                "confidence": confidence_pct,
                "message": "사진이 불분명하여 위치를 판독할 수 없습니다. 3분 내로 다시 촬영해주세요."
            }
            
    except Exception as e:
        # AI 서버 다운 등 예기치 못한 오류 발생 시의 Fallback 처리
        logger.exception(f"[{user_id}] AI 파이프라인 처리 중 치명적 에러 발생: {e}")
        return {
            "status": ActionType.ERROR.value, 
            "message": "현재 시스템 점검 중입니다. 수동으로 주차 완료 처리되었습니다."
        }

# ==========================================
# 🚀 엣지 케이스 시나리오 테스트 (Unit Test)
# ==========================================
if __name__ == "__main__":
    print("\n--- 1. 어뷰징 케이스: 카메라 렌즈를 손으로 가리고 찍은 경우 ---")
    print(process_parking_image("USER_001", b"DARK_IMAGE"))
    
    print("\n--- 2. 확실한 불법 주차 (신뢰도 92%) ---")
    print(process_parking_image("USER_002", b"NORMAL_IMAGE", override_confidence=0.92))
    
    print("\n--- 3. 애매한 상황: 비 오는 날 점자블록 근처 (신뢰도 75%) ---")
    print(process_parking_image("USER_003", b"NORMAL_IMAGE", override_confidence=0.75))
    
    print("\n--- 4. 판독 불가: 너무 멀리서 찍음 (신뢰도 45%) ---")
    print(process_parking_image("USER_004", b"NORMAL_IMAGE", override_confidence=0.45))
