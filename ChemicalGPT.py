import os
import langchain
import openai
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.callbacks import StreamlitCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import MessagesPlaceholder, SystemMessage
from langchain.agents import Tool


from langchain.tools import DuckDuckGoSearchRun, WikipediaQueryRun

openai.api_key = os.environ['OPENAI_API_KEY']
duck_search = DuckDuckGoSearchRun()
#wiki_search = WikipediaQueryRun()


verbose = True
langchain.debug = verbose

import streamlit as st

st.title('化学GPTと話す🤩')

llm = ChatOpenAI(
    temperature=0,
    model="gpt-4",
    streaming=True
    )
tools = [
    Tool(
        name = "DuckSearch",
        func=duck_search.run,
        description="useful for when you need to answer questions about current events."
    ),
    # Tool(
    #     name = "WikiSearch",
    #     func=wiki_search.run,
    #     description="useful for when you need to answer questions about general knowledge."
    # ),
]

PROMPT="""
    あなたは化学の専門家です。
    ユーザからの科学の質問について回答してあげてください。
    もし質問がわからない場合は、予測や推測をせずに、「どんな内容についてお調べですか？」と回答してください。
    SMILES表記を求められた場合は、DuckSearchツールを用いて化学物質データベースを検索し、正確な解答をしてください。
    正確にわからない場合は、「正確にわかりません」と回答してください。
"""

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
chat_history = MessagesPlaceholder(variable_name='chat_history')

agent_kwargs = {
    "system_message" : SystemMessage(content=PROMPT),
    "extra_prompt_messages": [chat_history]
}

agent = initialize_agent(
                    tools, 
                    llm, 
                    agent=AgentType.OPENAI_FUNCTIONS,
                    verbose=False, 
                    agent_kwargs=agent_kwargs, 
                    memory=memory,
                    return_intermediate_steps=False
)


if prompt := st.chat_input(): # Streamlit のチャット入力がある場合に実行する
    st.chat_message("user").write(prompt) # ユーザの入力メッセージをStreamlitのチャットに表示する
    with st.chat_message("assistant"): # アシスタントの応答を表示するためのブロックを開始する
        st_callback = StreamlitCallbackHandler(st.container()) # Streamlitのコンテナをコールバックとして使用するハンドラを初期化する****
        response = agent.run(prompt, callbacks=[st_callback]) # エージェントを使って
        st.write(response) # 応答をStreamlitのチャットに表示する
