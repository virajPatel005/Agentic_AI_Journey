import streamlit as st
from db_backened import chatbot,thread_model,get_all_threads
from langchain_core.messages import HumanMessage,AIMessage
import uuid 

def generate_thread():
    thread_id=str(uuid.uuid4())
    st.session_state["chat_threads"].append(thread_id)
    return thread_id

def new_chat():
    st.session_state['messages']=[]
    thread_id=generate_thread()
    st.session_state['thread_id']=thread_id
    add_thread(thread_id)
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
def load_conversation(thread_id):
    state=chatbot.get_state(config={"configurable":{
        "thread_id":thread_id
    }})
    return state.values.get("messages",[])



if "messages" not in st.session_state:
    st.session_state["messages"]=[]
if "chat_threads" not in st.session_state:
    st.session_state['chat_threads']=get_all_threads() 
if "thread_id" not in st.session_state:
    st.session_state['thread_id']=generate_thread()

      
# ***********Taskbar UI*******************

st.sidebar.title("MESSAGE HISTORY")
st.sidebar.header("RECENT CONVERSATIONS")
st.sidebar.button("NEW CHAT",on_click=new_chat)
for thread_id in st.session_state['chat_threads'][::-1]:
   if  st.sidebar.button(thread_id):
        st.session_state['thread_id']=thread_id
        messages=load_conversation(thread_id)
        temp_msg=[]
        for msg in messages:
            if isinstance(msg,HumanMessage):
               role="user"
            else:
                role="assistant"
            temp_msg.append({
                "role":role,
                "content":msg.content
            })
        st.session_state["messages"]=temp_msg
        
            
       



# ****Load Messages*********
for msg in st.session_state["messages"]:
    with st.chat_message(msg['role']):
        st.write(msg['content'])
        

user_input=st.chat_input("TYPE HERE: ")
if user_input:
    
    st.session_state["messages"].append({
        "role":"user",
        "content":user_input
    })
    
    
    CONFIG={
        "configurable":{
            "thread_id":st.session_state['thread_id']
        }
    }
    
    with st.chat_message("user"):
        st.write(user_input) 
    
    with st.chat_message("assistant"):
        ai_message=st.write_stream(
             message_chunk.content for  message_chunk,metadata in chatbot.stream(#type:ignore
            {"messages":[HumanMessage(content=user_input)]},#type:ignore
            config=CONFIG ,#type:ignore
            stream_mode="messages"

        )
        )   
        
        st.session_state["messages"].append({
            "role":"assistant",
            "content":ai_message
        })  
        
    
