import re

with open('app.py', 'r', encoding='utf-8') as f:
    raw = f.read()

# Split into import lines and rest-of-file
lines = raw.splitlines()

# Find where imports end (first non-import, non-blank line after imports)
import_end = 0
for i, l in enumerate(lines):
    if l.startswith('import ') or l.startswith('from ') or l.strip() == '' or l.startswith('#'):
        import_end = i
    else:
        if import_end > 5:
            break

body = '\n'.join(lines)

# Every name to check
checks = [
    # stdlib candidates
    ('os',        ['os\\.', 'os\\.path', 'os\\.makedirs', 'os\\.path\\.join', 'os\\.path\\.exists', 'os\\.path\\.abspath', 'os\\.path\\.dirname']),
    ('re',        ['re\\.', r'\bre\.search', r'\bre\.sub', r'\bre\.findall', r'\bre\.compile', r'\bre\.match']),
    ('shutil',    ['shutil\\.']),
    ('time',      ['time\\.']),
    ('base64',    ['base64\\.']),
    ('difflib',   ['difflib\\.']),
    ('Template',  ['Template\\(']),
    ('load_dotenv', ['load_dotenv']),
    # LangChain
    ('ChatGoogleGenerativeAI',       ['ChatGoogleGenerativeAI']),
    ('GoogleGenerativeAIEmbeddings', ['GoogleGenerativeAIEmbeddings']),
    ('DirectoryLoader',              ['DirectoryLoader']),
    ('TextLoader',                   ['TextLoader']),
    ('PyPDFLoader',                  ['PyPDFLoader']),
    ('RecursiveCharacterTextSplitter', ['RecursiveCharacterTextSplitter']),
    ('FAISS',                        ['FAISS']),
    ('ChatPromptTemplate',           ['ChatPromptTemplate']),
    ('SystemMessagePromptTemplate',  ['SystemMessagePromptTemplate']),
    ('HumanMessagePromptTemplate',   ['HumanMessagePromptTemplate']),
    ('MessagesPlaceholder',          ['MessagesPlaceholder']),
    ('StrOutputParser',              ['StrOutputParser']),
    ('RunnablePassthrough',          ['RunnablePassthrough']),
    ('RunnableLambda',               ['RunnableLambda']),
    ('RunnableWithMessageHistory',   ['RunnableWithMessageHistory']),
    ('ChatMessageHistory',           ['ChatMessageHistory']),
    # PIL
    ('Image',    ['Image\\.']),
    # project imports
    ('img_to_b64',              ['img_to_b64']),
    ('_clean_snippet',          ['_clean_snippet']),
    ('_html_escape',            ['_html_escape']),
    ('_highlight_snippet',      ['_highlight_snippet']),
    ('_highlight_answer_phrases', ['_highlight_answer_phrases']),
    ('create_vector_store',     ['create_vector_store']),
    ('_parse_retry_delay',      ['_parse_retry_delay']),
    ('EMBED_MODEL',             ['EMBED_MODEL']),
    ('EMBED_DIM',               ['EMBED_DIM']),
    ('LLM_MODEL',               ['LLM_MODEL']),
    ('DOCS_FOLDER',             ['DOCS_FOLDER']),
    ('INDEX_PATH',              ['INDEX_PATH']),
    ('SYSTEM_PROMPT',           ['SYSTEM_PROMPT']),
    ('_DIRECT_SYSTEM',          ['_DIRECT_SYSTEM']),
    ('_call_direct_llm',        ['_call_direct_llm']),
    ('build_qa_chain',          ['build_qa_chain']),
    ('_render_sources',         ['_render_sources']),
    ('_render_context_chips',   ['_render_context_chips']),
    ('_render_feedback_widget', ['_render_feedback_widget']),
    ('render_sidebar',          ['render_sidebar']),
    ('THEMES',                  ['THEMES']),
    ('get_css',                 ['get_css']),
]

print(f"{'NAME':<35} {'USAGES IN APP.PY (excl. import line)'}")
print('-' * 75)

for name, patterns in checks:
    # Search body, excluding the import line itself
    body_no_import = '\n'.join(l for l in lines if not (l.startswith('import ') or l.startswith('from ')) )
    hits = set()
    for pat in patterns:
        for m in re.finditer(pat, body_no_import):
            # get line context
            start = body_no_import.rfind('\n', 0, m.start()) + 1
            end   = body_no_import.find('\n', m.end())
            if end == -1:
                end = len(body_no_import)
            ctx = body_no_import[start:end].strip()
            hits.add(ctx[:60])
    count = len(hits)
    sample = list(hits)[0] if hits else '(none)'
    print(f"{name:<35} count={count}  e.g.: {sample[:38]}")
