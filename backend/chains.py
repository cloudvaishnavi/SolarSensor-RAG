import streamlit as st
import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from backend.vectorstore import LLM_MODEL, _parse_retry_delay

SYSTEM_PROMPT = """You are SolarSense, an expert AI assistant specialising in Indian rooftop solar systems and the PM Surya Ghar (MNRE) scheme.

**STRICT GROUNDING RULES (MUST FOLLOW):**
- You MUST answer the user's question ONLY using the context provided below.
- If the context does not contain the answer, you MUST reply EXACTLY with:
  "I don't have enough information in the loaded documents to answer that accurately. Please upload the relevant document or rephrase your question."
- Do NOT use outside knowledge. Do NOT speculate, guess, or invent answers.
- Even if the user asks a conversational question (e.g., "hello", "how are you?") that is not covered in the solar context, you must still apply the rule above and say you don't have enough information.

**ANSWER QUALITY RULES:**
- Open with a direct answer to the question in the first sentence — no throat-clearing, no "Based on the provided context..." preamble.
- Write the way a knowledgeable engineer would explain it to a colleague: precise, natural, and varied in sentence structure. Do not reuse the same opening phrase, transition words, or sentence pattern across consecutive answers.
- Synthesize the context in your own words rather than copy-pasting it verbatim.
- Use bullet points only when the answer genuinely has multiple distinct parts (steps, modes, comparisons); a single clear paragraph is better for simple factual questions.
- When comparing two things the user names explicitly (e.g. "compare X and Y"), structure the answer around the comparison itself — what's shared, what differs — rather than describing each one in isolation back-to-back.
- When discussing PM Surya Ghar subsidies, state the official slab clearly: Rs 30,000/kW for the first 2 kW, Rs 18,000/kW for 2-3 kW, Max CFA capped at Rs 78,000.
- Cite the source document naturally when providing factual information, but vary the phrasing (e.g. "per 01_dispatch_modes.txt", "as outlined in...", "(see 01_dispatch_modes.txt)") rather than repeating the exact same citation template every time.

Context from loaded documents:
{context}"""



def build_qa_chain(vectorstore):
    if vectorstore is None:
        return None, None

    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.15)

    retriever_ref = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.7}
    )

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{question}"),
    ])

    rephrase_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Given a chat history and the latest user question, formulate a fully standalone question that "
         "can be understood with NO access to the chat history. Do NOT answer the question — only reformulate it.\n\n"
         "Pay special attention to:\n"
         "- Positional references ('the second one', 'the last mode you mentioned') — resolve these to the "
         "actual named item(s) from the assistant's previous answer.\n"
         "- Comparative references ('compare X and Y', 'how is that different from...') — keep both compared "
         "items explicit and named in the rewritten question.\n"
         "- Pronouns ('it', 'that', 'this feature') — replace with the specific noun they refer to.\n"
         "- If the question is already standalone and self-contained, return it unchanged.\n\n"
         "Example: history mentions 'Cost-Save mode' then 'Backup Priority mode'; user asks 'explain the "
         "second one in more detail' -> rewrite as 'Explain Backup Priority mode in more detail'."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
    rephrase_chain = rephrase_prompt | llm | StrOutputParser()

    def _retrieve_docs(x):
        if x.get("chat_history"):
            query = rephrase_chain.invoke(x)
        else:
            query = x["question"]
        # Store the rewritten query for the optional debug expander (Feature 6)
        st.session_state["_last_rewritten_query"] = query
        docs = retriever_ref.invoke(query)
        st.session_state.latest_sources = docs
        return docs

    def _format_docs(docs):
        return "\n\n---\n\n".join(
            f"[Source {i+1}: {os.path.basename(d.metadata.get('source', 'unknown'))}]\n{d.page_content}"
            for i, d in enumerate(docs)
        )

    rag_chain = (
        RunnablePassthrough.assign(
            context=RunnableLambda(lambda x: _format_docs(_retrieve_docs(x)))
        )
        | prompt_template
        | llm
        | StrOutputParser()
    )

    qa_chain = RunnableWithMessageHistory(
        rag_chain,
        lambda session_id: st.session_state.chat_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )

    return qa_chain, retriever_ref


_DIRECT_SYSTEM = (
    "Answer from general knowledge only. "
    "Do NOT claim you have access to any documents or a knowledge base. "
    "Be concise and factual, but this answer is for demonstration purposes only "
    "and should not be treated as a primary or grounded response."
)

def _call_direct_llm(question: str) -> str:
    """Run the same LLM without any retrieval context. For RAG-vs-direct comparison only."""
    direct_llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.15)
    direct_prompt = ChatPromptTemplate.from_messages([
        ("system", _DIRECT_SYSTEM),
        ("human", "{question}"),
    ])
    direct_chain = direct_prompt | direct_llm | StrOutputParser()
    last_err = None
    for attempt in range(3):
        try:
            return direct_chain.invoke({"question": question})
        except Exception as e:
            last_err = str(e)
            if "429" in last_err or "RESOURCE_EXHAUSTED" in last_err or "500" in last_err or "503" in last_err:
                if attempt < 2:
                    wait = _parse_retry_delay(last_err, default=5 * (attempt + 1))
                    time.sleep(wait)
                    continue
            break
    return f"⚠️ Direct LLM call failed: {last_err[:120] if last_err else 'unknown error'}"


