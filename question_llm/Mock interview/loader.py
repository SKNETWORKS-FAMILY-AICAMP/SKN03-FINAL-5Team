import os
import re
import json
import pandas as pd
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain.docstore.document import Document
from langchain_community.document_loaders.csv_loader import CSVLoader

def html_loader_data():
    loader = WebBaseLoader(
        web_paths=[
            "https://docs.python.org/3/glossary.html",
        ],
        header_template={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        },
    )

    docs = loader.load()
    return docs

# docs = loader_data()
# print(docs)

# def preprocess_csv(file_path):
#     # CSV 파일을 불러오면서 텍스트 전처리
#     df = pd.read_csv(file_path, encoding="utf-8")

#     # 모든 문자열에서 줄바꿈과 특수문자를 안전하게 변환
#     df = df.applymap(lambda x: x.replace("\n", " ").replace("\r", " ").replace('"', '').replace("'", '') if isinstance(x, str) else x)

#     # 전처리된 파일을 새로운 CSV로 저장
#     cleaned_file_path = 'c:/dev/SKN03-Final_Project/csv_folder/cleaned_python_csv_01_processed.csv'
#     df.to_csv(cleaned_file_path, index=False, encoding="utf-8")
#     return cleaned_file_path

# # 전처리된 CSV 파일을 로드
# file_path = 'c:/dev/SKN03-Final_Project/csv_folder/cleaned_python_csv_01.csv'
# cleaned_file_path = preprocess_csv(file_path)

# def json_encode_content(docs):
#     # 문서의 내용을 JSON 형식으로 인코딩하여 구문 오류 방지
#     for doc in docs:
#         doc.page_content = json.dumps(doc.page_content)  # JSON 인코딩
#     return docs

def csvloader_data():
    # 파일 경로와 인코딩 방식 설정
    loader = CSVLoader(
        file_path='c:/dev/SKN03-Final_Project/csv_folder/하 데이터.csv',
        encoding='UTF-8',
        source_column='source',
        csv_args={'delimiter': ','}
    )
    
    # 데이터 로드 후 JSON 인코딩 처리
    docs = loader.load()
    return docs

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_folder = os.path.join(base_dir, "csv_folder")
csv_file_path = os.path.join(csv_folder, "merged_python.csv")

# csv_file_path 출력하여 확인
print("CSV File Path:", csv_file_path)

