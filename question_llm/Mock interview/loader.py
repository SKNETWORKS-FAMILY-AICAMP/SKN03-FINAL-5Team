from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain.docstore.document import Document

def loader_data():
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

docs = loader_data()
print(docs)
