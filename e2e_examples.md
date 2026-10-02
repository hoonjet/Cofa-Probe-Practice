🚀 AI 해커톤 도메인별 End-to-End 마스터 플레이북

본 문서는 Cofa-Probe 기반 AI 해커톤의 핵심 평가 요소인 **3대 축(의도 관리, 기술 관리, 인지 관리)**을 단일 프로세스로 묶어 도메인별로 어떻게 전개해야 하는지 보여주는 통합 가이드입니다.

1. 🛴 모빌리티 도메인: 스마트 주차 판독 시스템

Step 1. 의도 관리 (요구사항 및 룰 정의)

현업의 불만: "유저들이 불법 주차를 하는데 AI가 자꾸 정상으로 통과시킵니다. 무조건 잡아내서 벌금을 물리게 해주세요."

개발자의 역질문(의도 파악): "AI의 탐지 정확도가 환경(밤, 비)에 따라 떨어집니다. 신뢰도가 애매한 구간(60~84%)에서 억울한 유저가 발생하지 않으려면 어떻게 해야 할까요?"

합의된 비즈니스 룰:

Confidence 85% 이상: 즉각 벌금 부과 (정확함)

Confidence 60~84%: 운영팀 대시보드로 이관 (수동 검수)

Confidence 60% 미만: 유저에게 1회 재촬영 요청

Step 2. 기술 관리 (방어적 파이프라인 구현)

합의된 3단계 룰을 바탕으로, 불필요한 AI 호출을 막고 상태값을 안전하게 반환하는 파이프라인을 작성합니다.

def process_parking_image(image, ai_model):
    # 1. 전처리 필터링 (흔들린 사진 등)
    if is_blurry(image):
        return "REQUEST_RETAKE"
    
    try:
        # 2. AI 모델 추론
        result = ai_model.predict(image)
        confidence = result['confidence']
        
        # 3. 비즈니스 룰에 따른 분기 처리
        if confidence >= 0.85:
            return "APPLY_PENALTY"
        elif 0.60 <= confidence < 0.85:
            return "MANUAL_REVIEW"
        else:
            return "REQUEST_RETAKE"
            
    except Exception as e:
        # 4. Fallback: 에러 발생 시 무조건 수동 검수로 이관하여 오제재 방지
        return "MANUAL_REVIEW"


Step 3. 인지 관리 (검증 및 CI/CD)

단위 테스트: confidence가 정확히 0.849일 때 MANUAL_REVIEW로 가는지, 시스템 오류 시 Exception을 뱉고 죽는 대신 MANUAL_REVIEW를 반환하는지 테스트합니다.

CI/CD 연동: 이 로직이 수정될 때마다 GitHub Actions에서 테스트 코드가 자동 실행되어, 유저 페널티 로직의 결함을 사전에 차단합니다.

2. 🏥 의료 도메인: 응급 환자 중증도 분류 AI

Step 1. 의도 관리 (요구사항 및 룰 정의)

현업의 불만: "AI가 환자 분류를 돕고 있는데, 가끔 이상한 결과를 내놓아서 위험할 뻔했습니다. AI를 믿을 수 있게 해주세요."

개발자의 역질문(의도 파악): "가장 위험한 상황은 '시스템 다운으로 인한 골든타임 상실'과 '오진단'입니다. AI가 확신하지 못하거나 서버가 죽었을 때 무조건 전문의에게 알람이 가도록 우회(Fail-Safe)해도 될까요?"

합의된 비즈니스 룰:

AI 신뢰도 95% 이상: 즉시 해당 응급 코드 발송

AI 신뢰도 95% 미만 OR 서버 타임아웃: 무조건 전문의 대기열로 강제 이관 (Fail-Safe)

Step 2. 기술 관리 (Fail-Safe 파이프라인 구현)

어떤 런타임 에러가 발생해도 환자의 데이터가 유실되지 않는 무결성 보장에 집중합니다.

def triage_patient(patient_data, ai_model):
    try:
        # 응답 시간(Timeout)을 짧게 제한하여 골든타임 확보
        prediction = ai_model.predict(patient_data, timeout=3.0)
        
        if prediction['confidence'] >= 0.95:
            return {"status": "EMERGENCY_ALERT", "severity": prediction['level']}
        else:
            return {"status": "MANUAL_REVIEW_REQUIRED"}
            
    except (TimeoutError, ConnectionError):
        # 가장 중요한 로직: 서버 장애 시에도 시스템이 죽지 않고 수동 판독 이관
        return {"status": "MANUAL_REVIEW_REQUIRED", "alert": "SYSTEM_UNSTABLE"}


Step 3. 인지 관리 (검증 및 CI/CD)

단위 테스트: Mocking을 사용해 ai_model.predict가 TimeoutError를 발생시키도록 강제한 뒤, 시스템이 죽지 않고 MANUAL_REVIEW_REQUIRED를 반환하는지 검증합니다.

CI/CD 연동: GitHub Actions 파이프라인에 safety check를 추가하여, 의료 데이터 보안에 위협이 되는 취약점 패키지가 없는지 배포 전 자동 검사합니다.

3. 💳 금융 도메인: 이상거래 탐지(FDS) 오탐지 개선

Step 1. 의도 관리 (요구사항 및 룰 정의)

현업의 불만: "AI가 해외 직구를 자꾸 해킹으로 인식해서 카드를 정지시킵니다. 민원이 너무 많아요."

개발자의 역질문(의도 파악): "보안을 느슨하게 하면 진짜 해킹을 놓칩니다. AI 점수만 보지 말고, 고객의 기존 결제 패턴(룰 베이스)과 교차 검증하는 앙상블 방식을 도입하는 것은 어떨까요?"

합의된 비즈니스 룰:

AI는 '위험'으로 판단했으나, 고객의 주 사용 국가와 일치함: ARS/문자 본인 인증 후 결제 승인 (Soft Block)

AI 판단 '위험' + 룰 베이스 '위험' (처음 보는 국가): 즉시 카드 정지 (Hard Block)

Step 2. 기술 관리 (앙상블 파이프라인 구현)

AI의 결과값(환각/오류 가능성)을 전통적인 룰 기반 로직으로 한 번 더 필터링합니다.

def process_transaction(transaction, ai_model, user_profile):
    ai_risk_score = ai_model.evaluate_risk(transaction)
    
    # 룰 기반 교차 검증: 최근 3개월 내 해당 국가 결제 이력 확인
    is_familiar_country = transaction['country'] in user_profile['recent_countries']
    
    if ai_risk_score >= 0.8:
        if is_familiar_country:
            return "REQUEST_SMS_VERIFICATION" # 오탐지 방지를 위한 Soft Block
        else:
            return "BLOCK_CARD_IMMEDIATELY"   # Hard Block
            
    return "APPROVE_TRANSACTION"


Step 3. 인지 관리 (검증 및 CI/CD)

단위 테스트: 환각 방지(Hallucination Guardrail)에 초점을 맞추어, AI 모델이 오류로 말도 안 되는 스코어(예: 999.0)를 반환했을 때 시스템이 이를 안전하게 예외 처리(Normalization 또는 Fallback)하는지 테스트합니다.

CI/CD 연동: 고객 자산과 직결되므로, 특정 테스트 커버리지(예: 90%)를 넘기지 않으면 PR(Pull Request)이 머지(Merge)되지 않도록 브랜치 보호 룰을 설정합니다.
