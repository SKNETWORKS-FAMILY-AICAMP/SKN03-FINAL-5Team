import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.document_loaders import PyPDFLoader
import boto3 
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# AWS Parameter Store에서 API 키 가져오기
def get_parameter(name, with_decryption=True):
    ssm = boto3.client('ssm', region_name='ap-northeast-2')
    return ssm.get_parameter(Name=name, WithDecryption=with_decryption)['Parameter']['Value']

# PDF 파일에서 텍스트를 로드하는 함수
def load_pdf_content(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return "\n".join([doc.page_content for doc in docs])

# 텍스트 전처리 함수
def preprocess_text(text):
    lines = text.split('\n')
    processed_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(processed_lines)

# Pydantic 모델 정의
class ResumeProject(BaseModel):
    project: str = Field(description="프로젝트 경험")

# 프로젝트 경험 추출 함수
def extract_project_experience(file_path, api_key):
    resume = preprocess_text(load_pdf_content(file_path))
    llm = ChatOpenAI(api_key=api_key, model_name="gpt-4o")
    parser = PydanticOutputParser(pydantic_object=ResumeProject)
    prompt = PromptTemplate.from_template(
        """
        You are a helpful assistant.

        QUESTION:
        {question}

        RESUME:
        {resume}

        FORMAT:
        {format}
        """
    )
    prompt = prompt.partial(format=parser.get_format_instructions())
    template_chain = prompt | llm | parser
    response = template_chain.invoke({
        "resume": resume,
        "question": "이력서 내용 중 프로젝트 경험을 추출해주세요."
    })
    return response.project

# 번역 함수
def translate_text(text, api_key):
    llm = ChatOpenAI(api_key=api_key, model_name="gpt-4o")
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional translator. Please translate Korean to English"),
        ("user", "{input_text}")
    ])
    chain = chat_prompt | llm
    result = chain.invoke({"input_text": text})
    return result.content

# 키워드 추출 함수
def extract_keywords(text_chunks):
    tokenizer = AutoTokenizer.from_pretrained("ilsilfverskiold/tech-keywords-extractor")
    model = AutoModelForSeq2SeqLM.from_pretrained("ilsilfverskiold/tech-keywords-extractor")
    keywords = ""
    for value in text_chunks:
        inputs = tokenizer.encode("extract tech keywords: " + value, return_tensors="pt", max_length=500, truncation=True)
        # outputs = model.generate(inputs, max_length=150, num_beams=2, early_stopping=True)
        outputs = model.generate(
            inputs,
            max_length=30,           # 키워드 최대 길이
            num_beams=4,              # 탐색 폭을 늘림
            num_return_sequences=3,   # 결과를 여러 개 반환
            repetition_penalty=1,    # 중복된 단어를 억제
            early_stopping=True
        )
        keywords += tokenizer.decode(outputs[0], skip_special_tokens=True)
    return keywords

# 메인 함수
def main():
    OPENAI_API_KEY = get_parameter('/interviewdb-info/OPENAI_API_KEY')
    # FILE_PATH = "../data/frontend_resume.pdf"
    FILE_PATH = "../data/김민지_이력서.pdf"
    # 프로젝트 경험 추출
    project_experience = extract_project_experience(FILE_PATH, OPENAI_API_KEY)
    print("\n[Extracted Project Experience]")
    print(project_experience)

    # 번역
    translated_text = translate_text(project_experience, OPENAI_API_KEY)
    print("\n[Translated Project Experience]")
    print(translated_text)

    # 텍스트를 청크로 나누기
    chunk_size = 500
    text_chunks = [translated_text[i:i + chunk_size] for i in range(0, len(translated_text), chunk_size)]
    for idx, chunk in enumerate(text_chunks):
        print(f"Chunk {idx + 1}:\n{chunk}\n")

    # 키워드 추출
    keywords = extract_keywords(text_chunks)
    print("\n[Extracted Keywords]")
    print(keywords)

if __name__ == "__main__":
    main()
