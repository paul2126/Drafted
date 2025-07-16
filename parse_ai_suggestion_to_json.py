# Re-import necessary libraries after code state reset
import json

# Given data
raw_data = [
    {
        "id": 15,
        "content": "Name: DevBoost 스터디\nDescription: 웹 개발자 커뮤니티 기반의 기술 학습 스터디에서 프론트엔드 개발과  협업 툴 사용을 집중적으 로 학습\nPosition: 프론트엔드 리더\nEvent Role: 프론트엔드 개발 총괄\nEvent Category: 프론트엔드 개발, UI/UX 설계, 문제 해결 능력\nEvent Data:\n  Background: 스터디 팀  내 일정 관리, 이슈 공유, 코드 리뷰 등을 통합할 수 있는 툴이 부재했음. 개발자 간 커뮤니케이션 비 효율을 줄이고자 협업 툴 개발을 기획함.\n  My Action: React, Redux, Styled Components로 프론트엔 드 구조를 설계하고, 사용성을 높이기 위해 사용자 플로우를 반복 테스트함.\nGitHub OAuth 연동, 실시간 업데 이트 기능(Socket.io)도 구현하여 협업 편의성을 강화.\n  Result: 최종 배포 버전 기준 스터디 멤버 12명이 실제로 툴을 사용하며 기능적 만족도 평균 4.6/5 기록.\nGitHub 이슈 관리 대비 소통 시 간이 약 40% 단축됨.\n  Reflection: 복잡한 기능도 사용자 관점에서 단순화해야 함을 느꼈고, 개발 도중 의사소통 기록을 남기는 것 이 협업에서 중요하다는 점을 배움.\n",
        "similarity": 0.380166411399844,
    },
    {
        "id": 8,
        "content": "Name: 교내 IT동아리\nDescription: 2023년부터 교내 IT 동아리에서 프론트엔드 팀장을 맡으며 프로젝트 개발 및 멘토링 진행\nPosition: 프론트엔드 팀장\nEvent Role: 기획 및 프론트엔드 개발\nEvent Category: 기술 구현 능력,  문제해결능력, 리더십\nEvent Data:\n  Background: 신입생들의 길찾기 문제를 해결하기 위해 캠퍼스  맵 앱을 개발하기로 함.\n  My Action: 지도 API를 연동하고,  건물 검색 및 경로 탐색 기능을 프론트엔드에서 구현.\n팀원들과 UI/UX 회의를 통해 직관적인 화면 설계 방향을 도출.\n  Result: 약 500명의  신입생이 앱을 다운로 드해 사용했으며, 만족도 조사에서 평균 4.6/5의 점수를 획득.\n  Reflection: 기술적 완성도뿐만 아니라 사용자 경험을 고려한 기획의 중요성을 배움.\n",
        "similarity": 0.359812817562391,
    },
    {
        "id": 12,
        "content": "Name: 문화기획동아리 Re:Scene\nDescription: 대학 내 문화 기획 동아리로, 전시·공연·커뮤니티 행사 기획과 운영을 경험함\nPosition: 부회장\nEvent Role: 행사 운영 책임자\nEvent Category: 관계관리역량, 이벤트 운영, 의사소통 능력\nEvent Data:\n  Background: 코로나19 이후 동아리 구성원 간 교류가  적어 친밀도가 크게 낮아짐. 내부 결속을 다지고 신규 회원의 소속감을 높이기 위한 내부 네트워킹 프 로그램이 필요했음.\n  My Action: 소규모 모임별 콘셉트를 기획하고, 멤버별 관심사 기반 그룹을 구성. 프로그램 진행자 매뉴얼 제작 및 현장 진행을 총괄함.\n후속 설문조사를 통해 향후 정기모임  기획에 반영할 피드백을 수집함.\n  Result: 총 60명 참가, 신규회원 10명이 활동 유지 의사를 밝힘.\n행사 후 내부 만족도 4.9/5 기록. 향후 정기 프로그램 예산 배 정이 확정됨.\n  Reflection: 소통의 밀도가 동 아리의 생명이라는 점을 실감했고, 기획 초기에 니즈 조사가 매우 중요하다는 것을 배움.\n",
        "similarity": 0.357756354942545,
    },
]


def parse_ai_suggestion_to_json(raw_data):
    # Parse into desired format
    ability_set = {}
    activity_list = []

    for item in raw_data:
        content_lines = item["content"].split("\n")
        activity_name = ""
        description = ""
        position = ""
        event_role = ""
        event_categories = []

        for line in content_lines:
            if line.startswith("Name:"):
                activity_name = line.replace("Name:", "").strip()
            elif line.startswith("Description:"):
                description = line.replace("Description:", "").strip()
            elif line.startswith("Position:"):
                position = line.replace("Position:", "").strip()
            elif line.startswith("Event Role:"):
                event_role = line.replace("Event Role:", "").strip()
            elif line.startswith("Event Category:"):
                categories = line.replace("Event Category:", "").strip().split(",")
                event_categories = [c.strip() for c in categories]
                for cat in event_categories:
                    ability_set[cat] = (
                        f"{cat} 관련 경험과 문제 해결에 대한 적용 능력을 보여줍니다."  # placeholder desc
                    )

        activity_list.append(
            {
                "id": item["id"],
                "activity": activity_name,
                "fit": round(item["similarity"], 3),
                "events_list": [{"id": f"{item['id']}-event", "event": event_role}],
            }
        )

    # Build final structure
    parsed_result = {
        "ability_list": [
            {"id": idx + 1, "ability": ability, "description": desc}
            for idx, (ability, desc) in enumerate(ability_set.items())
        ],
        "activity_list": activity_list,
    }

    # Show output
    parsed_result_json = json.dumps(parsed_result, ensure_ascii=False, indent=2)
    return parsed_result_json
