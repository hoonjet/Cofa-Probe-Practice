💳 [시뮬레이션 실행] 금융 FDS 시스템 오탐지 최적화

이 문서는 제공된 프롬프트를 바탕으로 AI가 실제로 어떻게 반응하고 코드를 생성하는지 보여주는 전체 실행(Execution) 결과입니다.

1단계: 문제 정의 및 요구사항 구체화 (의도 관리)

[사용자 프롬프트]

너는 A카드사의 '리스크 관리팀 이팀장'이다. 최근 도입한 AI 기반 FDS(이상거래탐지) 시스템 때문에 고객 민원이 폭주해서 화가 나 있다. 나(AI 엔지니어)에게 FDS 차단 문제에 대해 따지듯이 말해라. 정상 결제인데 자꾸 막힌다는 점을 강조하되, 구체적인 결제 패턴이나 차단 조건은 모호하게 전달해라.

[AI 응답 (이팀장 역할 수행)]

"아니, 시스템을 어떻게 업데이트한 겁니까? 어제오늘 콜센터 대기 시간이 30분이 넘어가요! 고객들이 해외 출장 가서 호텔 결제하려는데 카드가 정지됐다고 난리입니다. 무조건 해외 결제라고 다 막아버리면 어떡합니까? 평소에 해외 직구 많이 하던 VIP 고객 카드까지 정지되면 어쩌자는 거예요. 이거 진짜 위험한 도용 결제랑 정상 결제 확실하게 구분해서 당장 수정해 주세요!"

[사용자 프롬프트 (역질문)]

팀장님, 고객 불편이 커서 정말 당황하셨겠습니다. 오탐지를 최소화하기 위해 다음 3가지 기준을 명확히 정의하고자 합니다.

'평소 해외 직구를 많이 하던 고객'을 시스템이 인지하려면, 최근 몇 개월 내 해외 가맹점 결제 이력이 몇 회 이상이어야 할까요?

진짜 위험한 도용 결제(예: BIN 번호 탈취)로 간주할 수 있는 짧은 시간 내의 반복 결제 시도 기준(예: O분 내 X회 이상)은 어떻게 되나요?

오탐지 발생 시 임시로 카드 정지를 해제할 수 있는 자동화된 고객 본인 인증 수단(알림톡 등)을 연동할까요?

[AI 응답 (요구사항 확정)]

"하아... 답답하네요. 일단 첫 번째, 최근 6개월 동안 해외에서 3번 이상 결제한 분들은 화이트리스트로 적용해서 통과시켜 주세요. 두 번째, 도용은 보통 순식간에 일어나니까 10분 내에 5번 이상 결제 시도가 있으면 이건 앞뒤 안 따지고 무조건 막아야 합니다. 세 번째, 차단되더라도 고객 카카오톡 알림톡으로 '본인 결제 맞습니까?' 메시지 보내서 고객이 '맞다'고 누르면 바로 정지를 풀어주는 프로세스 붙여주세요. 당장 내일 오전까지 테스트 가능한 코드 가져오세요!"

2단계: 파이프라인 구현 (기술 관리)

[사용자 프롬프트]

앞서 이팀장과 협의된 룰을 바탕으로 FDS 판별 Python 함수 detect_fraud_transaction(tx_data, user_history)를 작성해 줘. 10분 내 5회 이상 결제 시도는 최우선 차단하고, 과거 6개월 내 해외 결제 3회 이상은 화이트리스트로 통과시켜라. 예외 처리를 철저히 해라.

[AI 응답 (파이썬 코드 생성)]

from datetime import datetime, timedelta
from typing import Dict, List, Any

def detect_fraud_transaction(tx_data: Dict[str, Any], user_history: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    사용자의 현재 결제 건과 과거 결제 이력을 분석하여 이상 거래 여부를 판별합니다.
    """
    try:
        # 필수 키 검증
        if 'timestamp' not in tx_data:
            raise ValueError("현재 결제 건에 'timestamp'가 누락되었습니다.")
            
        current_time = tx_data['timestamp']
        is_overseas = tx_data.get('is_overseas', False)
        
        # user_history 타입 및 유효성 검사
        if not isinstance(user_history, list):
            raise TypeError("user_history는 리스트 형식이어야 합니다.")

        # 1. 최우선 차단: 10분 내 5회 이상 결제 시도 (현재 건 포함)
        recent_attempts = 1 # 현재 결제 시도 포함
        for tx in user_history:
            if 'timestamp' in tx:
                time_diff = current_time - tx['timestamp']
                if timedelta(minutes=0) <= time_diff <= timedelta(minutes=10):
                    recent_attempts += 1
                    
        if recent_attempts >= 5:
            return {"status": "BLOCKED", "reason": "HIGH_FREQUENCY_ATTEMPT"}

        # 2. 해외 결제 화이트리스트 체크
        if is_overseas:
            # 과거 6개월 내 해외 결제 건수 산출 (시뮬레이션상 history는 6개월 치로 가정)
            overseas_history_count = sum(1 for tx in user_history if tx.get('is_overseas') is True)
            
            if overseas_history_count >= 3:
                return {"status": "APPROVED", "reason": "WHITELIST_OVERSEAS_USER"}
            else:
                return {"status": "BLOCKED", "reason": "UNUSUAL_OVERSEAS_TX"}

        # 국내 결제는 기본적으로 승인 (별도 이상 패턴이 없는 경우)
        return {"status": "APPROVED", "reason": "NORMAL_DOMESTIC_TX"}

    except Exception as e:
        # 엣지 케이스 및 시스템 에러 발생 시 고객 보호 및 2차 검증을 위해 PENDING 처리
        return {"status": "PENDING", "reason": f"SYSTEM_ERROR: {str(e)}"}


3단계: 결과 검증 및 엣지 케이스 (인지 관리)

[사용자 프롬프트]

작성된 FDS 코드에 대해 발생할 수 있는 '엣지 케이스(Edge Case)' 3가지를 도출하고, 이를 검증하는 pytest 기반의 단위 테스트 코드를 작성해 줘. 방어 로직이 잘 작동하는지 테스트해라.

[AI 응답 (엣지 케이스 분석 및 테스트 코드)]

🔍 도출된 엣지 케이스 3가지

필수 데이터 누락 (Missing Key): tx_data에 timestamp 키 자체가 존재하지 않을 때 시스템이 멈추지 않고 PENDING을 반환하는가?

잘못된 데이터 타입 (Type Error): user_history가 리스트(List)가 아닌 None이거나 딕셔너리로 잘못 전달되었을 때 예외 처리가 되는가?

미래 시간의 타임스탬프 입력 (Time anomaly): 이력(user_history) 데이터에 현재 시간보다 미래의 타임스탬프가 섞여 들어왔을 때, 시간 차이(time_diff) 계산에서 음수가 발생하여 차단 로직이 오작동하지는 않는가?

🛠️ pytest 검증 코드 (test_fds.py)

import pytest
from datetime import datetime, timedelta
# 앞서 작성된 함수를 import 한다고 가정
# from fds_module import detect_fraud_transaction 

def test_missing_timestamp():
    """엣지 케이스 1: timestamp가 누락된 경우"""
    tx_data = {"is_overseas": True, "amount": 5000}
    user_history = []
    
    result = detect_fraud_transaction(tx_data, user_history)
    
    assert result["status"] == "PENDING"
    assert "SYSTEM_ERROR" in result["reason"]

def test_invalid_history_type():
    """엣지 케이스 2: user_history가 리스트가 아닌 None인 경우"""
    current_time = datetime.now()
    tx_data = {"timestamp": current_time, "is_overseas": False}
    user_history = None  # 잘못된 타입 주입
    
    result = detect_fraud_transaction(tx_data, user_history)
    
    assert result["status"] == "PENDING"
    assert "TypeError" in result["reason"]

def test_future_timestamp_in_history():
    """엣지 케이스 3: 이력에 미래 시간이 들어간 경우 (오작동 방지)"""
    current_time = datetime.now()
    tx_data = {"timestamp": current_time, "is_overseas": False}
    
    # 현재보다 5분 '미래'의 비정상적인 데이터
    future_time = current_time + timedelta(minutes=5)
    user_history = [{"timestamp": future_time, "is_overseas": False}] * 4
    
    result = detect_fraud_transaction(tx_data, user_history)
    
    # 미래 시간은 timedelta 계산 시 음수가 되어 0~10분 조건(최근 시도)에 걸리지 않아야 함
    # 결과적으로 정상 국내 거래로 승인되어야 함
    assert result["status"] == "APPROVED"
    assert result["reason"] == "NORMAL_DOMESTIC_TX"
