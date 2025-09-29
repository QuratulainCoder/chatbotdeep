import streamlit as st
from backend import UniversityChatbot

def main():
    # Initialize chatbot
    chatbot = UniversityChatbot()

    # Page configuration
    st.set_page_config(
        page_title="University Admission Chatbot",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    .stApp {
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
        border-left: 5px solid #ff4b4b;
        color: white;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
        border-left: 5px solid #00d4aa;
        color: #1a1d23;
        border: 1px solid #e0e0e0;
    }
    .quick-btn {
        width: 100%;
        margin: 0.2rem 0;
        border-radius: 25px;
    }
    .stButton button {
        border-radius: 25px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1 style="margin: 0; font-size: 2.5rem;">🎓 University Admission Chatbot</h1>
        <p style="margin: 0; font-size: 1.2rem;">Your AI-powered Admission Assistant with Advanced NLP & Voice Support</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem;">🚀 Frontend + Backend Separated</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 *Hello! Welcome to University Admission Office\n\nI'm your AI admission assistant with **advanced NLP features. I can help you with:\n\n🎯 **Program Information* - BS, MS, MPhil programs\n📋 *Admission Requirements* - Eligibility criteria\n⏰ *Application Deadlines* - Important dates\n🏆 *Merit Information* - Selection criteria\n📝 *Admission Procedure* - How to apply\n🎤 *Voice Support* - Speak in English or Roman Urdu\n\n*What would you like to know?*"}
        ]

    # Main layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Chat container
        st.subheader("💬 Conversation")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.container():
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user">
                        <strong>You:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <strong>Admission Bot:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)

        # Input area with voice button
        st.markdown("### 💭 Ask your question:")
        input_col1, input_col2 = st.columns([4, 1])
        
        with input_col1:
            user_input = st.text_input("Type your message...", label_visibility="collapsed", placeholder="Type your question or use voice...", key="text_input")
        
        with input_col2:
            voice_button = st.button("🎤 Voice", use_container_width=True, type="secondary", key="voice_button")

        # Handle voice input
        if voice_button:
            with st.spinner("🎤 Listening..."):
                voice_text, error = chatbot.handle_voice_input()
                
                if voice_text:
                    st.session_state.messages.append({"role": "user", "content": f"🎤 {voice_text}"})
                    response = chatbot.get_response(voice_text)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Speak the response
                    chatbot.speak_response(response)
                    st.rerun()
                elif error:
                    st.error(error)

        # Handle text input
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = chatbot.get_response(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Speak the response
            chatbot.speak_response(response)
            st.rerun()

        # Clear chat button
        if st.button("🗑 Clear Conversation", use_container_width=True, key="clear_button"):
            st.session_state.messages = [
                {"role": "assistant", "content": "👋 Hello! How can I assist you with university admissions today?"}
            ]
            chatbot.reset_conversation()
            st.rerun()

    with col2:
        # Quick Actions Sidebar
        st.subheader("🚀 Quick Actions")
        
        # Program Inquiry Buttons
        st.markdown("📚 Program Inquiry**")
        if st.button("🎓 All Programs List", use_container_width=True, key="all_programs"):
            st.session_state.messages.append({"role": "user", "content": "What programs do you offer?"})
            response = chatbot.get_response("programs")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        col_bs, col_ms = st.columns(2)
        with col_bs:
            if st.button("🖥 BS Programs", use_container_width=True, key="bs_programs"):
                st.session_state.messages.append({"role": "user", "content": "Tell me about BS programs"})
                response = chatbot.get_response("bs programs")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        with col_ms:
            if st.button("🎯 MS Programs", use_container_width=True, key="ms_programs"):
                st.session_state.messages.append({"role": "user", "content": "Tell me about MS programs"})
                response = chatbot.get_response("ms programs")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        if st.button("🔬 MPhil Programs", use_container_width=True, key="mphil_programs"):
            st.session_state.messages.append({"role": "user", "content": "Tell me about MPhil programs"})
            response = chatbot.get_response("mphil programs")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        # Admission Process Buttons
        st.markdown("📋 Admission Process**")
        if st.button("⏰ Application Deadline", use_container_width=True, key="deadline"):
            st.session_state.messages.append({"role": "user", "content": "What is the deadline?"})
            response = chatbot.get_response("deadline")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("📝 How to Apply", use_container_width=True, key="procedure"):
            st.session_state.messages.append({"role": "user", "content": "How to apply for admission?"})
            response = chatbot.get_response("admission process")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("🏆 Merit Criteria", use_container_width=True, key="merit"):
            st.session_state.messages.append({"role": "user", "content": "What is the merit criteria?"})
            response = chatbot.get_response("merit criteria")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        # Express Interest Buttons
        st.markdown("🎯 Express Interest**")
        interest_col1, interest_col2 = st.columns(2)
        with interest_col1:
            if st.button("🤖 CS", use_container_width=True, key="cs_interest"):
                st.session_state.messages.append({"role": "user", "content": "I'm interested in Computer Science"})
                response = chatbot.get_response("interested in computer science")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        with interest_col2:
            if st.button("💻 SE", use_container_width=True, key="se_interest"):
                st.session_state.messages.append({"role": "user", "content": "I'm interested in Software Engineering"})
                response = chatbot.get_response("interested in software engineering")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        interest_col3, interest_col4 = st.columns(2)
        with interest_col3:
            if st.button("📊 DS", use_container_width=True, key="ds_interest"):
                st.session_state.messages.append({"role": "user", "content": "I'm interested in Data Science"})
                response = chatbot.get_response("interested in data science")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        with interest_col4:
            if st.button("🌐 IT", use_container_width=True, key="it_interest"):
                st.session_state.messages.append({"role": "user", "content": "I'm interested in Information Technology"})
                response = chatbot.get_response("interested in information technology")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

        # Architecture Info
        st.markdown("---")
        with st.expander("🏗 Architecture Info"):
            st.markdown("""
            *Separated Architecture:*
            - ✅ *backend.py* - NLP logic, voice processing
            - ✅ *frontend.py* - Streamlit UI, user interface
            - ✅ *intents.json* - Chatbot data and responses
            
            *Features:*
            - Advanced NLP with Lemmatization
            - Voice Input & Output
            - Text-to-Speech
            - Conversation Memory
            - Program Validation
            """)

    # Footer
    st.markdown("---")
    st.markdown(
        "🎓 *University Admission Chatbot* | "
        "Frontend + Backend Separated | "
        "🚀 Deployed on Replit | "
        "All Features Active ✅"
    )

if _name_ == "_main_":
    main()
