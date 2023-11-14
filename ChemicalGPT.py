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
from rdkit_tool import RDKitTool

openai.api_key = os.environ['OPENAI_API_KEY']
duck_search = DuckDuckGoSearchRun()


verbose = True
langchain.debug = verbose

import streamlit as st

st.title('化学GPTと話す🤩')

st.markdown("""
## 質問サンプル
例えばこのような質問をしてみましょう。

- 初めまして！あなたは誰ですか？
- 薬理活性化合物とはなんですか？
- 薬理活性化合物の例を３つ挙げてください。名前と用途を教えてください。
- ペニシリンのSMILES表記を教えてください。

""")

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
    RDKitTool()
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
    特定の化学物質に対してSMILES表記を求められた場合はRDKitToolを用いてSMILES記法を回答してください。
    また、RDKitToolを用いる際は、化学物質は英語を入力することに気をつけてください。
    正確にわからない場合は、「正確にはわかりません」と回答してください。
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
