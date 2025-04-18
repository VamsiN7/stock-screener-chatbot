# from dotenv import load_dotenv
# load_dotenv()  # This loads your .env file into the environment
# import streamlit as st
# from langchain.vectorstores import Chroma
# from langchain.prompts import PromptTemplate
# from langchain.chat_models import ChatOpenAI
# from langchain_core.output_parsers import StrOutputParser
# from langchain.schema.runnable import RunnablePassthrough
# from langchain_openai.embeddings import OpenAIEmbeddings
# import os



# # --- Load API key from environment (must be set in your shell or .env)
# openai_api_key = os.getenv("OPENAI_API_KEY")
# if not openai_api_key:
#     st.error("❌ OPENAI_API_KEY not set. Please check your environment or .env file.")
#     st.stop()

# # --- Set up ChromaDB vectorstore from persisted data
# embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

# # Set your persist directory (change this if needed)
# persist_directory = "../../chroma_db"

# vectorstore = Chroma(
#     persist_directory=persist_directory,
#     embedding_function=embedding
# )

# # --- Prompt Template
# prompt_template = PromptTemplate.from_template(
#     "You are a helpful financial assistant. Use the following context to answer the user's question.\n\n"
#     "Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
# )

# # --- Chat Model
# chat = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=openai_api_key)

# # --- Create RAG Chain
# def get_answer(question: str) -> str:
#     retriever = vectorstore.as_retriever(
#         search_type='mmr',
#         search_kwargs={'k': 3, 'lambda_mult': 0.7}
#     )

#     chain = (
#         {'context': retriever, 'question': RunnablePassthrough()}
#         | prompt_template
#         | chat
#         | StrOutputParser()
#     )

#     return chain.invoke(question)


# # --- Streamlit UI ---
# st.set_page_config(page_title="Peter-Bot 💬", page_icon="📈")
# st.title("📊 Plynch-Bot")
# st.write("Ask anything about Peter Lynch’s strategies, trading psychology, or risk.")

# user_question = st.text_input("Enter your question:")

# if user_question:
#     with st.spinner("Thinking..."):
#         try:
#             response = get_answer(user_question)
#             st.success("Answer:")
#             st.write(response)
#         except Exception as e:
#             st.error(f"❌ Failed to get answer: {e}")

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
# from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_openai.embeddings import OpenAIEmbeddings
import os

# --- Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# --- Streamlit page config
st.set_page_config(page_title="Peter Lynch Bot", page_icon="📈")

st.title("📊 Peter Lynch Bot")
st.write("Ask anything about Peter Lynch’s strategies, trading psychology, or risk.")

# --- Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Validate API Key
if not openai_api_key:
    st.error("❌ OPENAI_API_KEY not set. Please check your environment or .env file.")
    st.stop()

# --- Set up Chroma Vectorstore
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
persist_directory = "../../../chroma_db"
vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding)

# --- Prompt Template
# prompt_template = PromptTemplate.from_template(
#     "You are a helpful financial assistant. Use the following context to answer the user's question.\n\n"
#     "Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
# )


prompt_template = ChatPromptTemplate.from_template(
    "You are a helpful financial assistant. Use the following context to answer the user's question.\n\n"
    "Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
)

# --- Chat Model
chat = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=openai_api_key)

# --- RAG Chain Function
def get_answer(question: str) -> str:
    retriever = vectorstore.as_retriever(search_type='mmr', search_kwargs={'k': 3, 'lambda_mult': 0.7})
    chain = (
        {'context': retriever, 'question': RunnablePassthrough()}
        | prompt_template
        | chat
        | StrOutputParser()
    )
    return chain.invoke(question)

# --- Chat input
user_input = st.chat_input("Ask a question about Peter Lynch's philosophy...")

if user_input:
    with st.spinner("Thinking..."):
        try:
            response = get_answer(user_input)
        except Exception as e:
            response = f"❌ Error: {e}"

    # Save both to history
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("assistant", response))

    # Display assistant response
    # st.chat_message("assistant").markdown(response)

# --- Display previous chat history
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)

# --- Optional: Clear chat history
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()