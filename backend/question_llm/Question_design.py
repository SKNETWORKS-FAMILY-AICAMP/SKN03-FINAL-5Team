# 필요기능(함수)
# 앱1 = 사용자 데이터 입력 (이력서(경력중심), 프로젝트(내용) => 우리가 기본 포맷을 제공하는게 좋을듯)    
#     = 핵심키워드 추출 (context에 전달할 핵심 정보만 추출) + 직무에 따라 중요한 정보의 가중치를 설정(기술 스택 등)

# 앱2 = 질문생성(RAG) 사용자데이터에서 핵심키워드를 추출 => 벡터db에서 기술 데이터에 맞는 공식홈페이지 정보 가져오기  
#       / 프로젝트(자소서)등에서 중요 내용 추출 (gpt) => system prompt 조정  *문장 확인 후 필요시 문장 수정 모델 추가
#     = 1차 질문 답변 이후 사용자 답변 데이터와 사용자데이터 추가 후 추가 질문생성  *질문생성 퀄리티에 따라 생성 추가 요건 부여 
# 질문 5개(기본) , 질문개수 선택 가능하게, 무제한 모드?

# 앱3 = 음성데이터 텍스트화 앱

# 앱4 = 영상데이터 저장 앱

# input1 = technology_context(사용자) = 사용자 데이터
#
# input2 = project_context(사용자) = 사용자 데이터
#
# input3 = *separation - google-STT(질문에 대한 답변)

# 질의응답 DB에 저장

# 난이도 별 수준 나누기 함수필요

# rag쓰자 벡터 db에는 공식홈페이지 논문자료 다 긁어모으고 레그 기반으로 질문생성하자 
# 질문생성과 평가 기준에는 근거자료가 필요한데 지금 모델은 결국 근거가 gpt가 되는 셈이니 근거자료 찾는 것이 중요하다

# 질문답변 타임 고정(3분)
# langgraphe
# ai model + prompt 엔지니어링                                 v<--------------------------------------ㄱ roop(5 or choice)
# input -> technology context / project context(embedding) -> question prompt -> answer 3 min timer -> finish button(or time out) -> evaluation -> end
#            (vector db)                                        ㅣ                                      ㄴ if 5sec mute = cut(finish)  ㄴ(vector db)
#                                                               rag evaluation


# 질문 6개 공통 3 llm 3개 pdf읽어오기 인재상에 부합하는지 db저장 질문 나오고 5초간 딜레이(음성녹음/약간의 읽을 시간) 
#음성을 별도로 파일로저장 => 나중에 병합
## 파이팅 하세욥^0^

#=================
#== 실시간 STT서비스 불가 // 자체적으로 영상 따고 음성 따서 각각 저장한 뒤 음성 텍스트 파일을 추출
