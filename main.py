from tts import play_audio
#Hyperloop
#设置环境变量
import env
env.openai_api_key()

#使用LLM
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4",temperature=0)
chat_search = ChatOpenAI(model="gpt-4",temperature=0)

from langchain_core.prompts import ChatPromptTemplate
from prompt import SystemPrompt


from langchain_core.output_parsers import StrOutputParser

#聊天历史记录
from langchain.memory import ChatMessageHistory
chat_history = ChatMessageHistory()



# from langchain_community.document_loaders import WebBaseLoader
# loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide")
# docs = loader.load()

# 读取文件，处理文件
from langchain_community.document_loaders import CSVLoader
loader_csv = CSVLoader("elon_musk/data/talk.csv")
docs_talk = loader_csv.load()
from langchain_community.document_loaders import TextLoader
loader_txt = TextLoader("elon_musk/data/about_zuck.txt")
docs_zuck = loader_txt.load()
loader_txt = TextLoader("elon_musk/data/xai.txt")
docs_xai = loader_txt.load()


# 切分文件
from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
documents_zuck = text_splitter.split_documents(docs_zuck)
documents_xai = text_splitter.split_documents(docs_xai)

# 向量存储
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
vectorstore = Chroma.from_documents(documents=docs_talk+documents_xai+documents_zuck, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_type = 'similarity_score_threshold',search_kwargs={'score_threshold': 0.5, 'k': 5})

from langchain_core.prompts import MessagesPlaceholder
from tools import get_vision

while True:
    user_input = input("Enter your input: ")

    # 加入对话历史记录
    chat_history.add_user_message(user_input)

    # 搜索对应文件
    query_transform_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. If the query contains abbreviations or other content, do not use knowledge to explain the abbreviations.",
        ),
    ]
    )
    query_transformation_chain = query_transform_prompt | chat_search | StrOutputParser()
    search_query = query_transformation_chain.invoke(
        {
            "messages": chat_history.messages,
        }
    )
    # print(search_query)
    docs = retriever.invoke(search_query)

    knowledge = ''
    for doc in docs:
        knowledge += doc.page_content + '\n'

    #生成聊天历史
    chatHistory = ''
    for i in range(len(chat_history.messages)-1):
        s = chat_history.messages[i]
        if s.type == 'human':
            chatHistory += 'user:' + s.content + '\n'
        elif s.type == 'ai':
            chatHistory += 'Elon Musk(you)' +':' + s.content + '\n'

    # 使用工具
    vision = ''
    vision = get_vision(user_input)

    # 生成User Prompt
    from prompt import UserPrompt
    agent_input = UserPrompt(worldInfo="",
                            knowledge=knowledge,
                            chatHistory=chatHistory,
                            vision=vision,
                            question=user_input)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SystemPrompt),
        ("user", "{input}")
    ])

    play_audio(result)
    # 调用LLM
    chain = prompt | llm | StrOutputParser()
    print(agent_input)
    result = chain.invoke({"input": agent_input})

    #存储对话历史
    chat_history.add_ai_message(result)

    print(result)

    play_audio(result)
