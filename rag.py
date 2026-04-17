"""
4.
1实现了上传文件
2实现了将上传的文件输入到数据库当中
3.基于提问向知识库中检索答案
"""

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough,RunnableWithMessageHistory, RunnableLambda
from file_history_store import get_history
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, format_document
from langchain_community.chat_models.tongyi import ChatTongyi


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt

class RagService(object):
    def __init__(self):
        # 生成数据库对象
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )
        # 之后要调用检索器，首先是根据input利用检索器去知识库中检索内容
        # 然后把检索到的内容放在context中，作为参考资料，一起送给大模型，大模型整理之后发送给用户
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的已知参考资料为主，"
                "简洁和专业的回答用户问题。参考资料：{context}"),
                ("system", "并且我提供用户的对话历史如下："),
                MessagesPlaceholder("history"),
                ("user", "请回答用户提问：{input}")
            ]
        )
        self.chat_model = ChatTongyi(model=config.chat_model_name)
        self.chain = self.__get_chain()
    def __get_chain(self):
        """获取最终执行链"""
        # 构建检索器
        retriever = self.vector_service.get_retriever()
        # 将检索到的文档由Document-》string
        def format_document(docs:list[Document]):
            if not docs:
                return "无相关资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str
        def format_for_retriever(input):
            input = input['input']
            return input
        def format_for_template(input2):
            new_value = {}
            new_value['input'] = input2['input']['input']
            new_value['context'] = input2['context']
            new_value['history'] = input2['input']['history']
            return new_value
        chain = (
            {
                "input": RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever) | retriever | format_document
                # # 想要看到对话历史记录的话，必须添加print_prompt这个函数
            } | RunnableLambda(format_for_template) | self.prompt_template | print_prompt |self.chat_model | StrOutputParser()
        )
        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        return conversation_chain
if __name__ == '__main__':
    session_config = {
        "configurable": {
            "session_id": "user_002",
        }
    }
    res = RagService().chain.invoke({"input": "身高178，体重125，穿多大"}, session_config)
    print(res)
