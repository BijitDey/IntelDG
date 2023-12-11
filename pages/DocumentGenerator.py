from langchain.chat_models import AzureChatOpenAI
from langchain.chains import RetrievalQA 
from langchain.chains.question_answering import load_qa_chain
from langchain.indexes import VectorstoreIndexCreator
import base64
import streamlit as st #1.25.0
import os
import json
from pathlib import Path
import ast
from langchain.embeddings import GooglePalmEmbeddings
import streamlit as st
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from PIL import Image
import shutil
import re
from docx import Document
import re
import pandas as pd
from src.Utility import TextProcessingUtility
from datetime import datetime
import pytz
# import pythoncom

# import fitz
# import webbrowser
# import extra_streamlit_components as stx
# import time
# from langchain.document_loaders import PyPDFLoader
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.llms import GooglePalm
# from azure.core.credentials import AzureKeyCredential
# from azure.ai.formrecognizer import DocumentAnalysisClient
# from langchain.vectorstores import Chroma
# from langchain.document_loaders import PyPDFLoader
# from prettytable import PrettyTable as pt
# from PyPDF2 import PdfReader
# import src.entity as entity 
# from src.entity import QAModel
# import pathlib
# import logging
# from difflib import SequenceMatcher
# from src.chunking_methods import (read_pdf,
#                                   read_docx_page_by_page,
#                                   split_text_newlines_regex,
#                                   split_text_spliter,
#                                   model_load,
#                                   highlight_text_in_pdf,
#                                   link_open,
#                                   replace_newlines,
#                                   download_docx,
#                                   pdf_docx_converter,
#                                   saved_updated_docx,
#                                   updated_text_with_color,
#                                   openai_api_calculate_cost,
#                                   num_tokens_from_string,
#                                   docx_pdf)


# pythoncom.CoInitialize()
################################### 
# Create a timezone object
tz = pytz.timezone('Asia/Kolkata')
tp =TextProcessingUtility()
# tp.link_open()
######################################ENV VARIABLES #################################
## Load all env variables
if load_dotenv()==True:
    os.environ["api_type"] = os.getenv('OPENAI_API_TYPE')
    os.environ["api_version"] = os.getenv('OPENAI_API_VERSION')
    os.environ["api_base"] = os.getenv('OPENAI_API_BASE')
    os.environ["api_key"] = os.getenv("OPENAI_API_KEY")
    print('#'*20)
    print("OPENAI_API_TYPE ::", os.environ["api_type"])
    print("OPENAI_API_VERSION ::", os.environ["api_version"])
    print("OPENAI_API_BASE ::", os.environ["api_base"])
    print("OPENAI_API_KEY ::", os.environ["api_key"])
    print('#'*20)

else:
    print("Open AI key Not loaded")

################################ Session state ####################################
if "old_text" not in st.session_state:
    st.session_state.old_text = []
if "new_text" not in st.session_state:
    st.session_state.new_text = []
if "vectordb" not in st.session_state:
    st.session_state.vectordb = None
if "document2_chunks" not in st.session_state:
    st.session_state.document2_chunks=None
if "link_list" not in st.session_state:
    st.session_state.link_list=None
if "old_documents_copy" not in st.session_state:
    st.session_state.old_documents_copy=""
if "flag" not in st.session_state:
    st.session_state.flag=[]
if "updated_final_results" not in st.session_state:
    st.session_state.updated_final_results=[]
if "instruction_doc" not in st.session_state:
    st.session_state.instruction_doc=[]
if "retrieved_doc" not in st.session_state:
    st.session_state.retrieved_doc=[]
if "prompt_tokens" not in st.session_state:
    st.session_state.prompt_tokens=[]
if "prompt_cost" not in st.session_state:
    st.session_state.prompt_cost=[]
if "completion_tokens" not in st.session_state:
    st.session_state.completion_tokens=[]  
if "completion_cost" not in st.session_state:
    st.session_state.completion_cost=[]  
if "Total_Tokens" not in st.session_state:
    st.session_state.Total_Tokens=[] 
if "Total_Cost" not in st.session_state:
    st.session_state.Total_Cost=[] 
if "tokens" not in st.session_state:
    st.session_state.tokens=True
if "instruction_doc_link" not in st.session_state:
    st.session_state.instruction_doc_link=None
if "instruct_pdf_file_path" not in st.session_state:
    st.session_state.instruct_pdf_file_path=None
if "final_pdf_file_path" not in st.session_state:
    st.session_state.final_pdf_file_path=None
if "docx_file_path" not in st.session_state:
    st.session_state.docx_file_path=None
if "final_updated_docx_file_path" not in st.session_state:
    st.session_state.final_updated_docx_file_path=None
if "link_open" not in st.session_state:
    st.session_state.link_open=None

# st.session_state.link_open==None:
    
#################### Header Section #########################
img = Image.open("src/images/affine.jpg")
page_config = {"page_title":"invoice_tool.io","page_icon":img,"layout":"wide"}
st.set_page_config(**page_config)

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; margin-top:-70px; margin-bottom: 5px;margin-left: -50px;'>
    <h2 style='font-size: 60px; font-family: Courier New, monospace;
                    letter-spacing: 2px; text-decoration: none;'>
    <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" alt="logo" width="70" height="60">
    <span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            text-shadow: none;'>
                    IntelDG
    </span>
    <span style='font-size: 60%;'>
    <sup style='position: relative; top: 5px; color: #ed4965;'>by Affine</sup>
    </span>
    </h2>
    </div>
    """, unsafe_allow_html=True)
    

with st.sidebar:
    st.markdown("""
    <div style='text-align: center;top-margin:-200px;'>
    <h2 style='font-size: 20px; font-family: Arial, sans-serif; 
                    letter-spacing: 2px; text-decoration: none;'>
    <span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            text-shadow: none;'>
                    IntelDG
    </span>
    <span style='font-size: 40%;'>
    <sup style='position: relative; top: 5px; color: #ed4965;'></sup>
    </span>
    </h2>
    </div>
    """, unsafe_allow_html=True)
## logo
with st.sidebar:
    st.markdown("""<div style='text-align: left; margin-top:-230px;margin-left:-40px;'>
    <img src="https://affine.ai/wp-content/uploads/2023/05/Affine-Logo.svg" alt="logo" width="300" height="60">
    </div>""", unsafe_allow_html=True)
    
    # st.write("**Contracts Editor**")


###############################Download the DOCX updated file ##############################
def get_binary_file_downloader_html(bin_file, file_label='File'):
        with open(bin_file, 'rb') as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">{file_label}</a>'
        return href

############################## Documnet Directory #############################
old_doc_path="old_documents"
instruct_doc_path="Instruction documents"

############################## Silder #############################
with st.sidebar:    
    ## List the available documents(v1) in the directory
    old_doc_subdirs = os.listdir(old_doc_path)
    print(old_doc_subdirs)
    ## List of all available documents(Instruction input) in the directory
    instruct_doc_subdirs=os.listdir(instruct_doc_path)
    print(instruct_doc_subdirs)
    # Select the first document(v1) in the directory
    old_file = st.selectbox('**Pick the old document :**', sorted(old_doc_subdirs), key="1")
    # pick the chunking method for the old document(v1)
    selected_old_chunk_method=st.selectbox("Pick the chunk method ::",["NewLine Chunk","Recursive Chunk"],key="3")
    # select the instruction document with respect to the old document(v1)
    instruct = st.selectbox('**Pick the Instruction document :**', sorted(instruct_doc_subdirs), key="2")
    # pick the chunking method for the instruction document
    selected_instruct_chunk_method=st.selectbox("Pick the chunk method ::",["NewLine Chunk","Recursive Chunk"],key="4")
    ## Set the path of documents
    old_file_1 = f"{old_doc_path}/{old_file}"
    instruct_file_2 = f"{instruct_doc_path}/{instruct}"
    ## Select the LLM model
    list_methods = ['OpenAI'] #'Palm'
    method_used = st.selectbox('**Pick the Model type to be used for Document generation :**', list_methods)
    st.write("**Click the below button if you want to generate a new version of the document:**")
    trigger_1 = st.button("Generate")
    st.write("\n")
    st.write("\n")

## Method objects
# qa_model=QAModel()

################################# Document Generation Home Page Tabs ##############################
tab1,tab2,tab4=st.tabs(['Update Comparator:page_facing_up:','Highlighter:lower_left_crayon:','Revision Log:arrow_down_small:']) 
## Remove tabs
# tab5 = "Cost Analysis"
# tab3 = 'Version Downloader:floppy_disk:'


css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 22px;
    padding-right:50px
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

## set the header text here to remove before the emedding is done
footer = """Affine Inc. 2018 156th Avenue, N.E, Building F, Suite 333, Bellevue, Washington, 98007 Tel: +91 -80-6569 -0996 | Web: www.affine.ai | Mail: info@affine.ai Affine Confidential"""
special_characters = r"[]{}()^$.*+?|\\"
# Escape special characters by adding a backslash before them
escaped_string = re.sub(f"[{''.join(re.escape(char) for char in special_characters)}]", r"\\\g<0>", footer)
pattern = re.sub(r'\s+', r'\\s*', escaped_string)
replacement = "footer"

## Output is temp file storage. delete all files containing this directory
if len(st.session_state.old_text)==0:
    if os.path.exists('temp'):
        shutil.rmtree('temp')
    os.mkdir('temp')

# Excute the following script once press the trigger
if trigger_1 :
    # delete previous vectore store if exits
    if os.path.exists('.chroma'):
        shutil.rmtree('.chroma')

    # Load file one and store the embeddings 
    if old_file_1 is not None:
        documents1=tp.read_pdf(old_file_1)
        st.session_state.old_documents_copy=documents1
        if selected_old_chunk_method=="Recursive Chunk":
            print("Recursive Chunk Method")
            # document_chunks=qa_model.document_splitter_assistant(documents1,user_input_chunk_size = 2000,user_input_chunk_overlap = 300) 
            document_chunks=tp.split_text_spliter(documents1,user_input_chunk_size = 2000,user_input_chunk_overlap = 300)   
        else:
            print("New Line Chunk Method")
            document_chunks=tp.split_text_newlines_regex(documents1)
            # st.write(document_chunks)

        if method_used=='OpenAI': 
            print("Open AI Embedding Model...")   
            st.session_state.vectordb=tp.create_embedding_assistant(document_chunks)
            print("Embedding Done.")  
        # else:
        #     palm_embeddings = GooglePalmEmbeddings(google_api_key='AIzaSyANUF3eOCg6TK1f4P_aMbtHHHIwI2F5mF4')
        #     st.session_state.vectordb = Chroma.from_texts(texts = document_chunks, embedding=palm_embeddings)
    
    if instruct_file_2 is not None:
        # st.header("Instruction document")
        if st.session_state.document2_chunks==None:
            st.session_state.document2=tp.read_docx_page_by_page(instruct_file_2)
            print("Document 2 chunk Loaded")
            if selected_instruct_chunk_method=="Recursive Chunk":
                print("Recursive Chunk Method(Instruction)")
                # st.session_state.document2_chunks=qa_model.document_splitter_assistant(st.session_state.document2,user_input_chunk_size = 2000,user_input_chunk_overlap = 300)  
                st.session_state.document2_chunks=tp.split_text_spliter(st.session_state.document2,user_input_chunk_size = 2000,user_input_chunk_overlap = 300) 
            else:
                print("New Line Chunk Method(Instruction)")
                st.session_state.document2_chunks=tp.split_text_newlines_regex(st.session_state.document2)

    ct = 0
    final_results=[]
    with tab1:
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        total_len=len(st.session_state.document2_chunks)

    for num,text in enumerate(st.session_state.document2_chunks):
        if text:
            print("*"*100)
            print("Chunk Counter : ")
            print(text)
            my_bar.progress((num + 1)/total_len, text=progress_text)

            # query= "Compare the provided old document with the user's context to identify text that requires modification."
            # query="Find a context that matches the text : {}".format(text)
            # custom_prompt_template ="""You have an old document file and a user-provided context. 
            # Your goal is to compare the old document with the user's context and identify any changes that need to be made to the document text. 
            # Specifically, you want to extract a list of tuples, where each tuple consists of two elements:
            # 1. The old document text that requires potential modifications.
            # 2. The new text that phrasing is similar to the old document text, and that the model recommends as a potential replacement or improvement.
            # old documet:
            # {context}
            # user-provided context:
            # {text}
            # Question:{question}
            # Dont add anything other than the above provided format
            # The output format should be list of tuples. example:[(Old document text, New text)]"""

            query="Find a context that matches the text and using this text look for the changes required in the context: {}".format(text)
            # custom_prompt_template ="""You have an old document file and a user-provided updated context in the question. 
            # Your goal is to compare the old document with the user's context and identify any changes that need to be made to the document text based on user context. 
            # Specifically, you want to extract a list of tuples, where each tuple consists of two elements:
            # 1. The old document text that requires potential modifications based on relevant user provided text.
            # 2. The new text that phrasing is similar to the old document text, and that the model recommends as a potential replacement or improvement.
            # 3. Verify that the first user-provided context is actually relevant to the document context and that the change in document context based on user context is truly required.
            # old documet:
            # {context}
            # Question:{question}
            # If the user-supplied text is irrelevant to the context of the document, return an empty list. Please avoid this error in output format unterminated string literal.
            # The output format should be list of tuples. example:[(Old document text, New text)]"""
            
            # custom_prompt_template ="""You have an old document file and a user-provided updated context in the question. 
            # Your goal is to compare the old document with the user's context and identify any changes that need to be made to the document text based on user context. 
            # Specifically, you want to extract a list of tuples, where each tuple consists of two elements:
            # 1. The old document text that requires potential modifications based on relevant user provided text.
            # 2. The new text that phrasing is similar to the old document text, and that the model recommends as a potential replacement or improvement.
            # 3. Verify that the first user-provided context is actually relevant to the document context and that the change in document context based on user context is truly required.
            # old document:
            # {context}
            # Question:{question}
            # If the user-supplied text is irrelevant to the context of the document, return an empty list. Please avoid this error in output format unterminated string literal.
            # Ensure newline characters are included during text extraction from the old document for effective text search. Keep it brief and relevant.
            # The output format should be list of tuples. example:[(Old document text, New text)]"""

            custom_prompt_template ="""You have an old document file and a user-provided updated context in the question. 
Your goal is to compare the old document with the user's context and identify any changes that need to be made to the document text based on user context. 
Specifically, you want to extract a list of tuples, where each tuple consists of two elements:
1. The old document text that requires potential modifications based on relevant user provided text.
2. The new text that phrasing is similar to the old document text, and that the model recommends as a potential replacement or improvement.
3. Verify that the first user-provided context is actually relevant to the document context and that the change in document context based on user context is truly required.
old document:
{context}
Question:{question}
If the user-supplied text is irrelevant to the context of the document, return an empty list. Please avoid this error in output format unterminated string literal.
old document output text should be clean and structured. Do not add newline char into Old document text. Do not exaplain the updates in new text, recreate new text based on the old text.
The output format should be list of tuples. example:[(Old document text, New text)]"""
            PROMPT = PromptTemplate(
                                    template = custom_prompt_template, input_variables = ["context","question"],
                                    # partial_variables={"text": text}
                                        )
            chain_type_kwargs = {"prompt": PROMPT}
            llm=tp.model_load(model_type="gpt-4")    
            custom_qa = RetrievalQA.from_chain_type(llm=llm, 
                                                    chain_type="stuff", 
                                                    retriever=st.session_state.vectordb.as_retriever(type = "similarity",search_kwargs={"k":3}),
                                                    chain_type_kwargs=chain_type_kwargs,
                                                    return_source_documents = True)
            
            try:                                                   
                response = custom_qa({"query": query})
                final_prompt=custom_prompt_template+' '+response['query']+' '+' '.join([doc.page_content for doc in response['source_documents']])
                ## Prompt token 
                prompt_tokens=tp.num_tokens_from_string(final_prompt)
                ## Completion Tokens
                completion_tokens=tp.num_tokens_from_string(response['result'])
                usage={"prompt_tokens":prompt_tokens,"completion_tokens":completion_tokens,"total_tokens":prompt_tokens+completion_tokens}
                # cost of dictionary
                usage_cost=tp.openai_api_calculate_cost(usage)
                st.session_state.prompt_tokens.append(usage_cost["prompt_tokens"])
                st.session_state.prompt_cost.append(usage_cost["prompt_cost"])
                st.session_state.completion_tokens.append(usage_cost["completion_tokens"])
                st.session_state.completion_cost.append(usage_cost["completion_cost"])
                st.session_state.Total_Tokens.append(usage_cost["Total Tokens"])
                st.session_state.Total_Cost.append(usage_cost["Total Cost"])
                result = response['result']
                if '[' in result and ']' in result:
                    output=result[result.find('['):result.find(']')+1]
                    list_1=ast.literal_eval(output)
                    # print(list_1)
                    for old,new in list_1:
                        st.session_state.old_text.append(old)
                        st.session_state.new_text.append(new)
                        st.session_state.instruction_doc.append(text)
                        st.session_state.retrieved_doc.append(response["source_documents"])
                    print("Number of Changes Found ::",len(list_1))
                    if type(list_1)==list:
                        st.session_state.updated_final_results.extend(list_1)
                else:
                    print("Null result")
                        
            except:
                continue
    my_bar.empty()
## once model output is extracted and store it into sessin state then excute the following script
if st.session_state.old_text:
    ## Convert the old pdf file into docx file and save into dir
    if st.session_state.docx_file_path==None:
        st.session_state.docx_file_path=tp.pdf_docx_converter(old_file_1,"./pdf-docx_files")
        file_name=st.session_state.docx_file_path.split("//")[-1]
        st.session_state.final_updated_docx_file_path=f"version_2/v2_{file_name}"
        ### Below method not able to handle table files
        # st.session_state.flag=tp.saved_updated_docx(st.session_state.updated_final_results,
        #                    st.session_state.docx_file_path,
        #                    st.session_state.final_updated_docx_file_path)
        ### Below method able to handle table files
        st.session_state.flag=tp.saved_updated_docx_v2(st.session_state.updated_final_results,
                           st.session_state.docx_file_path,
                           st.session_state.final_updated_docx_file_path)
         ## final updated 
        if st.session_state.final_pdf_file_path==None:
            st.session_state.final_pdf_file_path=f"temp/{st.session_state.final_updated_docx_file_path.split('/')[-1].replace('.docx','.pdf')}"
            if os.path.exists(st.session_state.final_pdf_file_path)==False:
                st.session_state.final_pdf_file_path=tp.docx_pdf(st.session_state.final_updated_docx_file_path,
                                                                  st.session_state.final_pdf_file_path)
            print("Revised Document PDF file ::",st.session_state.final_pdf_file_path)
        
    ## slice the initial some char to the dropdown
    list_of_change=[text[:150]+'...' for text in st.session_state.new_text]
    # with st.expander(":green[See More Detail Comparsion ::]"):
    with tab1:
        st.header("",divider="rainbow")
        selected_change=st.selectbox(":green[Select the respective Change ::]",list_of_change)
        st.header("",divider="rainbow")
        if selected_change:
                index_of_change=list_of_change.index(selected_change)
                ## v1 approch

                st.session_state.link_list=tp.highlight_text_in_pdf(old_file_1,
                                    "temp",
                                    [st.session_state.old_text[index_of_change]])
                # instruction doc
                if st.session_state.instruct_pdf_file_path==None:
                    st.session_state.instruct_pdf_file_path=f"temp/{instruct.replace('.docx','.pdf')}"
                    # convert docx file to pdf file if not exists
                    if os.path.exists( st.session_state.instruct_pdf_file_path)==False:
                        st.session_state.instruct_pdf_file_path=tp.docx_pdf(instruct_file_2, st.session_state.instruct_pdf_file_path)

                st.session_state.instruction_doc_link=tp.highlight_text_in_pdf(st.session_state.instruct_pdf_file_path,
                                    "temp",
                                    [st.session_state.instruction_doc[index_of_change]])
                # Final Revised version
                print("Revised Document PDF file ::",st.session_state.final_pdf_file_path)
                st.session_state.final_doc_link=tp.highlight_text_in_pdf(st.session_state.final_pdf_file_path,
                                    "temp",
                                    [st.session_state.new_text[index_of_change]])

                # for num in range(len(st.session_state.old_text)):
                # st.write("Old Text ::")
                st.info("click on below text to see where is the change",icon="❇️")
                col1,col2,col3=st.columns([1,1,1])
                col1.subheader(":orange[Document Version V1]")
                if len(st.session_state.link_list)>=1:
                    col1.write(f"[{st.session_state.old_text[index_of_change]}](http://localhost:{8009}//{st.session_state.link_list[0]})")
                else:
                    col1.write(st.session_state.old_text[index_of_change])

                col2.subheader(":orange[Instruction Document Text]")
                # col2.write(st.session_state.instruction_doc[index_of_change])
                if len(st.session_state.instruction_doc_link)>=1:
                    col2.write(f"[{st.session_state.instruction_doc[index_of_change]}](http://localhost:{8009}//{st.session_state.instruction_doc_link[0]})")
                else:
                    col2.write(st.session_state.instruction_doc[index_of_change])
                col3.subheader(":orange[Document Version V2]")
                # st.session_state.final_doc_link
                if len(st.session_state.final_doc_link)>=1:
                    col3.write(f"[{st.session_state.new_text[index_of_change]}](http://localhost:{8009}//{st.session_state.final_doc_link[0]})")
                else:
                    col3.write(st.session_state.new_text[index_of_change])
        st.header("",divider="rainbow")
        # with st.expander("Check the retrieved Chunks"):
        #     for i in range(3):
        #         st.subheader(f":orange[Chunk ::{i}]")
        #         st.write(st.session_state.retrieved_doc[index_of_change][i].page_content)
else:
    print("Null result")

if st.session_state.document2_chunks:
    # with tab5:
    if st.session_state.tokens:
        # st.write(st.session_state.document2_chunks)
        cost_dict={"Prompt Tokens":st.session_state.prompt_tokens,
         "prompt_cost":st.session_state.prompt_cost ,
         "Completion Tokens":st.session_state.completion_tokens,
         "completion_cost":st.session_state.completion_cost,
         "Total Tokens":st.session_state.Total_Tokens,
         "Total Cost":st.session_state.Total_Cost}
        cost_df=pd.DataFrame(cost_dict)
        # st.dataframe(cost_df)
        # st.header("Total",divider="rainbow")
        # st.dataframe(pd.DataFrame(cost_df.sum()).transpose())
        sum_row=pd.DataFrame(cost_df.sum()).transpose()
        sum_row['File_name']=old_file  # Document File name
        sum_row['DateTime']=datetime.now(tz) # Get the current date and time in the specified timezone
        token_df=pd.read_csv("Token.csv") # Csv file where all tokens and its cost are stored
        if len(token_df.columns)==0:
            token_df.columns=['Prompt Tokens', 'prompt_cost', 'Completion Tokens', 'completion_cost',
       'Total Tokens', 'Total Cost', 'File_name', 'DateTime']
        token_df=pd.concat([token_df,sum_row])
        token_df.to_csv("Token.csv", index=False)
        st.session_state.tokens=False

if st.session_state.old_text:
    with tab2:
        # st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        st.header("",divider="rainbow")
        st.info("Press the button below to mark all alterations in the old document (V1), highlight in yellow.",icon="❇️")
        if st.button("Highlight All Changes in Existing Version (V1)"):
            tp.highlight_text_in_pdf(old_file_1,
                                "temp",
                                st.session_state.old_text,single_change_highlights=False)
            st.success("All identified modifications in the old version (V1) have been successfully highlighted.",icon="✅")
        st.header("",divider="rainbow")
        st.info("Press the button below to emphasize all recent modifications in the Revised Edition, Revised text highlighted in blue color.",icon="❇️")
        if st.button("Highlight All Chnages in Updated Version (V2)"):
            print(st.session_state.final_updated_docx_file_path.split("/")[-1])
            tp.updated_text_with_color(st.session_state.final_updated_docx_file_path,st.session_state.updated_final_results)
            st.success("Emphasize all modifications using blue color in the Revised Edition",icon="✅")
        st.header("",divider="rainbow")
        st.info("Click on below link to download the Revised Edition.",icon="❇️")
        st.markdown(get_binary_file_downloader_html(st.session_state.final_updated_docx_file_path, 'Download new document version'), unsafe_allow_html=True)

    # if len(st.session_state.flag)==0:
    #     # if st.button("Download"):
    #     for n in range(len(st.session_state.old_text)):
    #         if st.session_state.old_documents_copy.find(st.session_state.old_text[n])!=-1:
    #             st.session_state.old_documents_copy=st.session_state.old_documents_copy.replace(st.session_state.old_text[n],st.session_state.new_text[n])
    #             st.session_state.flag.append("yes")
    #         else:
    #             st.session_state.flag.append("No")
    # st.session_state.old_documents_copy=replace_newlines(st.session_state.old_documents_copy)
    # download_docx(st.session_state.old_documents_copy,output_file_path=old_file.replace('.pdf',"")+".docx")
    # st.download_button('Download CSV', text_contents, 'text/csv')
    # Function to create a download link
    

    # Use the function
    # output_file_name=old_file.replace('.pdf',"")
    ################################# Download revised version ####################
    # with tab3:
    #     st.info("Click on below link to download the Revised Edition.",icon="❇️")
    #     st.markdown(get_binary_file_downloader_html(st.session_state.final_updated_docx_file_path, 'Download new document version'), unsafe_allow_html=True)
        
    with tab4:
        st.subheader(":orange[Document Edition History]")
        dict_1={"old version":st.session_state.old_text,"New Version":st.session_state.new_text,
                "Flags":st.session_state.flag}
        df=pd.DataFrame(dict_1)
        st.dataframe(df)






    
