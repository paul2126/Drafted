# Drafted

## 📌 개요

이 프로젝트는 **AI 기반 지원서 작성 지원 플랫폼**의 백엔드입니다.

사용자 프로필 관리, AI 추천 시스템, 안전한 인증 및 데이터 저장, 그리고 클라우드 기반 안정적 배포까지 포함합니다.

---

## 🤖 AI 활용

플랫폼의 핵심 기능은 **AI를 통한 지원서 보조**입니다.

1. **문항 기반 가이드라인 생성**
    - 사용자가 입력한 지원서 문항을 분석하여, 구조화된 글 작성 가이드라인을 자동으로 제공합니다.
    - 내부적으로 OpenAI API를 활용해 JSON Schema 기반의 응답을 강제하여, 일관된 출력 형식을 유지합니다.
2. **문항+활동 매칭 추천**
    - 사용자가 등록한 활동 데이터를 벡터화하고, 문항과의 **임베딩 유사도 점수**를 계산합니다.
    - 이를 통해 해당 문항에 가장 적합한 활동들을 추천하고, 추천 근거를 함께 제시합니다.
3. **대화형 AI 응답 (Chat)**
    - 사용자가 질문을 입력하면 직전 대화 10개를 컨텍스트로 활용하여 응답을 생성합니다.
    - 단순한 Q&A가 아니라, 지원서 문항과 연결된 맥락 속에서 대화가 이어집니다.

> 이러한 AI 기능은 지원자가 자기소개서를 더 논리적이고 구체적으로 작성할 수 있도록 돕습니다.
> 

---

## 🔐 로그인 및 보안

- **인증**: Supabase Auth(JWT 기반 인증)를 활용하여 사용자 인증을 처리합니다.
- **RLS(Row Level Security)**: Supabase DB에서 각 사용자는 본인의 데이터만 접근할 수 있도록 **행 수준 보안**을 활성화했습니다.
- **프로필 관리**:
    - `ProfileCreateView`, `ProfileInfoView` 등 APIView를 통해 프로필 생성/조회/수정/삭제를 지원합니다.
    - 모든 요청은 `get_user_id_from_token`을 통해 토큰 내 user_id를 검증한 뒤 처리됩니다.
- **보안 포인트**:
    - JWT 만료 시 자동 차단
    - 민감 데이터 최소 반환 (예: 비밀번호 없음, 필요 정보만 반환)
    - HTTPS 기반 요청/응답 암호화

---

## 🗂 데이터베이스 ERD

서비스의 전체 데이터 스키마 구조입니다.

### 주요 테이블

- **profile**: 사용자 기본 정보
- **activity**: 사용자가 등록한 활동 (카테고리, 기간, 설명 등)
- **event**: 활동별 세부 사건 기록 (STAR 구조 기반)
- **application**: 지원서 단위 (카테고리, 포지션, 활동명)
- **question_list**: 지원서 문항
- **chat_session, chat_message**: 대화 세션 및 기록
- **activity_embedding**: 활동 임베딩 저장 (AI 추천용)
- **event_suggestion, ai_suggestion**: 문항-이벤트 매핑 및 AI 추천 결과

<img width="1618" height="898" alt="image" src="https://github.com/user-attachments/assets/dddc42c1-a060-48f4-ab88-58a35177cfd2" />


---

## 🚀 배포

본 백엔드는 **안정적이고 확장 가능한 클라우드 아키텍처** 위에서 배포되었습니다.

- **애플리케이션 서버**:
    - **Gunicorn + Nginx** 조합으로 안정적인 WAS 환경 구성
    - Gunicorn은 Django 애플리케이션 실행을 담당하고, Nginx는 **Reverse Proxy** 역할 및 정적 파일 서빙 담당
- **데이터베이스**:
    - **Supabase PostgreSQL** 사용
    - RLS 설정을 통해 사용자별 데이터 격리 보장
- **클라우드 인프라**:
    - **AWS EC2**: 백엔드 서버 호스팅
    - **AWS S3 + CloudFront**: 정적 파일과 미디어 파일을 글로벌 CDN을 통해 안정적 제공
- **특징**:
    - 프록시 설정(Nginx)으로 HTTPS, 로드 밸런싱 가능
    - Supabase와 AWS 리소스를 조합하여 확장성 확보

---

## 📜 기술 스택

- **Backend**: Django REST Framework, Supabase Client
- **Database**: Supabase PostgreSQL
- **Authentication**: Supabase Auth (JWT)
- **AI**: OpenAI API (JSON Schema 기반 응답 강제)
- **Infra**: AWS EC2, S3, CloudFront, Gunicorn, Nginx
