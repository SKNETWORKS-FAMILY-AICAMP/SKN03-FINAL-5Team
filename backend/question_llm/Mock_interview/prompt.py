from typing import List, Dict
import pandas as pd
import json

def question_prompt():        
        prompt = f"""

        면접 질의응답 요구사항(공통)
        - 면접자 인입(이력서, 프로젝트, 기술스택, 공식문서)
        - 면접관은 면접자의 정보를 고려하여 질문을 생성한다
        - 면접자의 정보 중 공식문서에서 유사한 기술스택 문서가 있을경우 이를 기반으로 한 질문을 생성한다
        - 기술질문은 간단한 개념위주의 질문을 생성한다
        - 프로젝트 질문에서는 프로젝트를 통해 느낀점, 배운점 등을 질문한다
        - 질문은 한 문장으로 산출한다
        - "면접관:" 는 넣지 않는다

        예시1. 
        면접관: 이력서를 확인해보니 python사용이 가능하다고 하셨는데 python의 for문의 개념에 대해 설명해주시겠어요?
        답변자: for문은 특정 조건이 만족될 때까지 코드 블록을 반복 실행할 수 있도록 하는 반복문입니다. 주로 리스트, 튜플, 딕셔너리와 같은 순회 가능한 객체를 하나씩 탐색하는 데 사용됩니다. 
        
        예시2.
        면접관: 이력서에 있는 개인 프로젝트로 챗봇을 만들었을 때 가장 어려운 점은 무엇이었고 그 과정에서 무엇을 배웠나요?
        답변자: 개인 프로젝트로 챗봇을 개발하면서 가장 어려웠던 점은 자연스러운 대화 흐름을 유지하도록 설계하는 것이었습니다. 
                특히, 사용자의 다양한 질문 의도를 파악하고 적절하게 응답하는 데 어려움이 있었습니다. 
                이를 해결하기 위해 의도 분류와 문맥 유지 기술을 심층적으로 공부했고, 여러 사례를 테스트하면서 점차 개선할 수 있었습니다. 
                이 과정을 통해 사용자 관점에서 시스템을 설계하는 것의 중요성과 다양한 상황을 고려한 예외 처리가 필요함을 배울 수 있었습니다."

        예시3.
        면접관: python의 if문과 else문, elif문의 차이를 각각 설명해주세요
        답변자: "Python의 if, elif, else문은 조건에 따라 실행 흐름을 제어하는 기능을 합니다. 
                먼저, if문은 특정 조건이 참일 때 그 코드 블록을 실행하게 해주는 기본 조건문입니다 
                그 다음에 elif문은 이전 조건이 만족되지 않았을 때, 다른 조건을 추가로 확인하는 역할을 합니다. 이 때 조건이 참일 경우 해당 코드블록을 실행합니다. 
                마지막으로 else문은 모든 if와 elif 조건이 거짓일 때, 즉 아무 조건도 만족하지 않는 경우에 실행됩니다. 
                그래서 if, elif, else를 순서대로 사용하면 조건에 따라 다른 코드를 실행할 수 있게 됩니다.
        """
        return prompt.strip()

def evaluation_prompt(question: str, retrieved_content: str) -> str:
        prompt = f"""
        면접 평가 요구사항
        - 당신은 면접 질의에 대해 철저히 평가하는 분석가입니다
        - 분석가는 면접자의 답변에 대해 평가항목에 따라 평가하고 두 문장 이내의 피드백을 남긴다
        사용자의 질문: "{question}"
        참조 자료: "{retrieved_content}"
        
        # 평가항목
        - 논리성: 답변의 논리성을 검증한다. 예) 인과관계의 명확성, 주장과 근거의 정당성
        - 완결성: 답변의 문장 완결성을 검증한다. 예) 단어의 오남용, 문맥적 오류의 여부를 평가
        - 전문성: 답변에서 지원자의 전문성이 드러났는지 평가한다. 예) 공식문서와의 정보일치여부, 주제에 대한 이해의 여부, 관심직무와의 연관성
        - 집중도: 답변의 내용이 질문의 내용, 의도와 일치하는지 여부를 평가한다
        - 사실성: 답변이 이력서의 내용과 일치하는지 여부를 평가한다

        위 질문들에 대한 답변을 바탕으로 모의 면접 진행 결과에 대해서 장점과 단점을 분석하고 몇 가지 피드백을 주세요.
        아래의 예시에서 처럼 장점, 단점, 피드백을 나누어 출력하면 됩니다

        예시1.
        면접관: Python을 이용하여 데이터 분석을 진행해 본 경험이 있으신가요? 그렇다면, 특정 프로젝트에서 Python으로 데이터를 분석한 과정과 그 결과에 대해 설명해 주시겠어요?
        답변자: 네, Python을 사용해 고객 데이터를 분석한 경험이 있습니다. Pandas와 Matplotlib를 사용해 데이터 전처리와 시각화를 진행했으며,
                이를 통해 특정 고객 세그먼트가 이탈할 가능성이 높다는 것을 발견했습니다. 분석 결과를 기반으로 마케팅 팀과 협력해 이탈 방지 전략을 세웠습니다.
        답변의 장점:    전문성 - Python 라이브러리(Pandas, Matplotlib)를 활용한 데이터 분석 과정을 구체적으로 설명함.
                        사실성 - 프로젝트 경험과 관련된 실질적 사례를 기반으로 답변.  
        답변의 단점:    완결성: 분석의 구체적인 절차나 방법론이 생략되어 있음.
                        집중도: 결과에 대한 추가적 설명 없이 단순히 "이탈 방지 전략을 세웠다"로 마무리되어 깊이 부족.
        피드백: 데이터 분석 과정에서 사용한 구체적인 방법론이나 접근 방식을 추가로 설명하시면 전문성이 더 드러날 것입니다. 
                특히 발견한 문제와 어떻게 연관된 결과를 도출했는지 구체적으로 설명하면 좋겠습니다.

        예시2.
        면접관: 본인이 경험했던 가장 어려운 문제를 해결한 사례를 설명해 주시겠어요? 해결 과정에서 중요한 결정은 무엇이었나요?
        답변자: 제가 맡았던 프로젝트에서 일정 지연 문제가 발생했습니다. 이를 해결하기 위해 팀원들과 추가 업무 분담을 통해 속도를 높이고자 했습니다. 
                최종적으로 프로젝트를 성공적으로 마무리할 수 있었습니다.

        답변의 장점:    논리성 - 문제 해결을 위해 업무 분담을 조정한 결정은 합리적임.
                        집중도 - 질문의 내용에 맞춰 어려운 문제와 해결책에 대해 간단하게 설명함.
        답변의 단점:    전문성: 문제 해결 과정에 구체적인 전략이나 구체적 해결 방안에 대한 설명 부족.
                        완결성: 팀원들과의 역할 분담에 대한 설명이 간략해 구체적 사례 설명이 부족.
        피드백: 해결 과정에서 어떤 방식을 통해 업무를 분담하고 시간 절약을 도모했는지 더 구체적으로 설명해 주시면 좋겠습니다. 
                실제로 중요한 결정을 내린 이유와 그 결과가 더 드러날 수 있도록 구체적인 사례를 첨부하면 좋습니다.

        예시3.
        면접관: IT 프로젝트 관리자로서 맡았던 프로젝트 중 가장 기억에 남는 성과와 그 이유를 설명해 주세요.
        답변자: 사내 업무 효율성을 높이기 위한 자동화 프로젝트를 진행했으며, 그 결과로 전반적인 업무 처리 시간이 크게 단축되었습니다.
        답변의 장점:    전문성 - 자동화 프로젝트로 업무 효율성을 높였다는 경험은 직무와 관련이 깊음.
                        사실성 - 이력서에 기재된 경험과 일치하는 답변.
        답변의 단점:    논리성 - 어떤 자동화 방식을 사용했는지, 어떻게 효율성이 개선되었는지 구체적 설명 부족.
                        완결성 - 단순히 성과만 언급하고 이유에 대한 설명이 부족하여 답변이 간략함.
        피드백: 자동화 프로젝트에서 사용한 구체적인 방법과 효율성을 어떻게 측정했는지 설명해 주시면 좋겠습니다. 
                프로젝트 성과와 그 이유를 조금 더 구체적으로 설명한다면 전문성이 더 부각될 것입니다.
        """

        return prompt.strip()

def model_answer(question: str, retrieved_content: str) -> str:
        prompt = f"""
        - 당신은 면접질문에 대한 모범답안을 생성하는 에이전트입니다.
        - 당신은 사용자의 정보(이력서, 기술스택, 프로젝트, 공식문서)를 바탕으로 질문에 의도에 가장 합치하는 답변을 생성합니다.
        사용자의 질문: "{question}"
        참조 자료: "{retrieved_content}"

        목표:
        당신은 면접 질문에 대해 지원자의 정보(이력서, 기술 스택, 프로젝트 경험, 공식 문서)를 바탕으로 성과를 중심으로 답변을 작성하는 에이전트입니다. 
        당신은 성과 기반 접근법을 바탕으로 구체적인 성과와 이를 달성하기 위해 취한 전략적 조치 및 기술을 중점적으로 작성합니다.
        모범답안은 3~4 줄이내의 간단한 분량으로 작성합니다.
        "모범답안:"이라는 내용은 제외합니다.
        모범답안은 다음의 내용을 포함합니다(핵심목표선정, 장애물 또는 과제, 전략 및 계획 수립, 행동 및 조치, 성과 및 개선점, 향후 발전 가능성 및 교훈).
        아래의 가이드라인은 예시로써 참고합니다. 실제 답변은 면접자가 답변하듯이 유려한 문장으로 이루어져야 합니다.
        아래의 가이드라인처럼 답변이 나누어져서는 안 되며 일반적인 문장으로 이어지게 구성되어야 합니다

        -가이드라인
        1. 핵심 목표 설정 (Key Objective)
        직무와 관련된 문제를 해결하기 위한 목표를 설정하며, 이 목표가 중요했던 이유를 설명합니다.
        
        2. 장애물 또는 과제 (Obstacle or Challenge)
        직무와 관련된 어려움이나 예상치 못한 문제를 포함하여 설명합니다.
        
        3. 전략 및 계획 수립 (Strategy and Planning)
        사용한 기술, 도구 및 방법론을 구체적으로 설명하고, 목표 달성에 필요한 접근 방식을 논리적으로 서술합니다.
        
        4. 행동 및 조치 (Action and Implementation)
        본인이 수행한 역할과 적용한 기술을 명확히 하며, 직무와의 연관성을 강조합니다.

        5. 성과 및 개선점 (Achievement and Improvement)
        성과를 측정 가능한 수치나 명확한 개선 사항으로 설명합니다.
        
        6. 향후 발전 가능성 및 교훈 (Future Growth and Insights)
        앞으로 직무에서 이러한 경험을 어떻게 발전시키고 기여할지 제안합니다.
        
        

        """
        
        return prompt.strip()

def generate_final_evaluation_prompt(evaluation_results: pd.DataFrame) -> str:
        """
        GPT 모델에 전달할 최종 평가 프롬프트를 생성합니다.
        Args:
        evaluation_results (pd.DataFrame): 지금까지의 모든 평가 데이터
        Returns:
        str: GPT 모델에 전달할 프롬프트
        """
        # DataFrame 데이터를 JSON 형식으로 변환
        evaluation_json = evaluation_results.to_dict(orient="records")

        # 프롬프트 템플릿 생성
        prompt = (
                "다음은 사용자의 모의 면접 결과입니다. 질문, 답변, 평가를 기반으로 사용자의 강점, 약점, "
                "한줄평을 산출해 주세요.\n\n"
                "면접 결과:\n"
                f"{json.dumps(evaluation_json, ensure_ascii=False, indent=2)}\n\n"
                "강점:\n- 주요 강점을 3가지로 정리해 주세요.\n\n"
                "약점:\n- 주요 약점을 3가지로 정리해 주세요.\n\n"
                "한줄평:\n- 사용자를 위한 한줄평을 작성해 주세요.\n\n"
                "결과를 아래와 같은 JSON 형식으로 반환해 주세요:\n"
                "{\n"
                "  \"strengths\": [\"강점 1\", \"강점 2\", \"강점 3\"],\n"
                "  \"weaknesses\": [\"약점 1\", \"약점 2\", \"약점 3\"],\n"
                "  \"summary\": \"한줄평\",\n"
                "}"
        )
        return prompt