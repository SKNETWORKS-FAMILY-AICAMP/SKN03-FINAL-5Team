import os
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

def csvloader_data():
    # 파일 경로와 인코딩 방식 설정
    loader = CSVLoader(
        file_path='c:/dev/SKN03-Final_Project/csv_folder/python_csv_01.csv',
        encoding='cp949',
        source_column='source',  # source_column에는 URL이 아니라 실제 컬럼 이름을 입력하세요.
        csv_args={'delimiter': ','}  # delimiter는 CSV 파일이 쉼표로 구분된 경우 ','로 설정
    )
    
    # 데이터 로드
    docs = loader.load()
    return docs

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_folder = os.path.join(base_dir, "csv_folder")
csv_file_path = os.path.join(csv_folder, "python_csv_01.csv")

# csv_file_path 출력하여 확인
print("CSV File Path:", csv_file_path)
    