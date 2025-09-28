import streamlit as st
import random
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import string
import json
import speech_recognition as sr
import pyttsx3
import threading

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4')

class UniversityChatbot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        
        # Initialize TTS engine
        try:
            self.tts_engine = pyttsx3.init()
        except:
            self.tts_engine = None
            st.warning("Text-to-speech not available")
        
        # Load data from JSON file
        with open('intents.json', 'r') as file:
            data = json.load(file)
            self.intents = {intent["tag"]: intent for intent in data["intents"]}
            self.programs = data["programs"]
            self.program_details = data["program_details"]
        
        self.current_program = None
    
    def preprocess_text(self, text):
        """Preprocess text with lemmatization"""
        text = text.lower().translate(str.maketrans('', '', string.punctuation))
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        return lemmatized_tokens
    
    def check_program_exists(self, user_input):
        """Check if program exists using lemmatized matching"""
        tokens = self.preprocess_text(user_input)
        
        level_keywords = {
            "bs": ["bs", "bachelor", "undergraduate"],
            "ms": ["ms", "master", "graduate"], 
            "mphil": ["mphil", "research", "m.phil"]
        }
        
        program_keywords = {
            "computer": ["computer", "computing", "cs"],
            "software": ["software", "sw"],
            "data": ["data", "data science", "analytics"],
            "information": ["information", "it", "technology"],
            "emerging": ["emerging", "technology", "new"]
        }
        
        detected_level = None
        detected_program = None
        
        # Detect level
        for level, keywords in level_keywords.items():
            if any(keyword in ' '.join(tokens) for keyword in keywords):
                detected_level = level
                break
        
        # Detect program  
        for program, keywords in program_keywords.items():
            if any(keyword in ' '.join(tokens) for keyword in keywords):
                detected_program = program
                break
        
        if detected_program and not detected_level:
            detected_level = "bs"
        
        if detected_level and detected_program:
            program_map = {
                "computer": "Computer Science",
                "software": "Software Engineering", 
                "data": "Data Science",
                "information": "Information Technology",
                "emerging": "Emerging Technologies"
            }
            
            program_name = program_map.get(detected_program)
            if program_name in self.programs[detected_level]:
                full_program_name = f"{detected_level.upper()} {program_name}"
                self.current_program = full_program_name
                return full_program_name
        
        return None
    
    def get_intent_match(self, tokens):
        """Enhanced intent matching with lemmatization"""
        best_match = None
        highest_score = 0
        
        for intent_name, intent_data in self.intents.items():
            score = 0
            for pattern in intent_data["patterns"]:
                pattern_tokens = self.preprocess_text(pattern)
                match_count = sum(1 for token in tokens if token in pattern_tokens)
                if match_count > score:
                    score = match_count
            
            if score > highest_score and score >= 1:
                highest_score = score
                best_match = intent_name
        
        return best_match
    
    def get_response(self, user_input):
        """Generate response with lemmatization and context awareness"""
        tokens = self.preprocess_text(user_input)
        
        # Check for program interest
        interest_keywords = ["interest", "want", "like", "apply", "admission", "choose", "select", "prefer"]
        if any(word in tokens for word in interest_keywords):
            program_name = self.check_program_exists(user_input)
            if program_name:
                return random.choice(self.intents["program_interest"]["responses"]).format(program_name)
            else:
                return "I couldn't find that specific program. We offer:\n• BS: Computer Science, Software Engineering, IT\n• MS: Computer Science, Data Science, Software Engineering\n• MPhil: Computer Science, Emerging Technologies\n\nWhich program are you interested in?"
        
        # Enhanced intent matching
        intent = self.get_intent_match(tokens)
        
        if intent in ["requirements", "deadline", "merit"]:
            program_context = self.current_program or "our programs"
            details = self.program_details.get(program_context, {})
            
            if intent == "requirements":
                requirement_text = details.get('requirements', '• 50% marks in previous degree\n• Relevant background\n• Entry test clearance')
                return random.choice(self.intents["requirements"]["responses"]).format(program_context, requirement_text)
            elif intent == "deadline":
                deadline_text = details.get('deadline', '📅 December 31, 2024')
                return random.choice(self.intents["deadline"]["responses"]).format(program_context, deadline_text)
            elif intent == "merit":
                merit_text = details.get('merit', '• Based on academic record\n• Entry test performance\n• Interview assessment')
                return random.choice(self.intents["merit"]["responses"]).format(program_context, merit_text)
        
        # Handle other intents
        if intent:
            return random.choice(self.intents[intent]["responses"])
        
        # Context-aware default response
        if self.current_program:
            return f"Regarding {self.current_program}, would you like information about admission requirements, deadlines, or merit criteria?"
        else:
            return "I'm here to help with university admission queries! 🎓 You can ask about:\n• Programs we offer (BS/MS/MPhil)\n• Admission requirements\n• Application deadlines\n• Merit criteria\n• Admission procedure\n\nWhat would you like to know?"

    def speak_response(self, text):
        """Convert text to speech"""
        if self.tts_engine:
            def speak():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=speak)
            thread.start()

def handle_voice_input():
    """Handle voice input with error handling"""
    try:
        recognizer = sr.Recognizer()
        
        # Try different microphone sources
        for microphone_index in range(3):  # Try first 3 microphones
            try:
                with sr.Microphone(device_index=microphone_index) as source:
                    st.info(f"🎤 Listening... (Microphone {microphone_index + 1})")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
                    break
            except:
                continue
        else:
            # If no microphone works, use default
            with sr.Microphone() as source:
                st.info("🎤 Listening... (Default microphone)")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
        
        # Try English first, then Roman Urdu
        try:
            text = recognizer.recognize_google(audio)
        except:
            try:
                text = recognizer.recognize_google(audio, language='ur-PK')
            except:
                text = recognizer.recognize_google(audio, language='en-US')
        
        return text, None
        
    except sr.WaitTimeoutError:
        return None, "No speech detected. Please try again."
    except sr.UnknownValueError:
        return None, "Could not understand audio. Please speak clearly."
    except sr.RequestError as e:
        return None, f"Speech recognition error: {str(e)}"
    except Exception as e:
        return None, f"Microphone error: {str(e)}"

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
    }
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
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
    }
    .quick-btn {
        width: 100%;
        margin: 0.2rem 0;
        border-radius: 25px;
    }
    .voice-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center;">
        <h1 style="margin: 0; font-size: 2.5rem;">🎓 University Admission Chatbot</h1>
        <p style="margin: 0; font-size: 1.2rem;">Your AI-powered Admission Assistant with Advanced NLP & Voice Support</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 **Hello! Welcome to University Admission Office**\n\nI'm your AI admission assistant with **advanced NLP features**. I can help you with:\n\n🎯 **Program Information** - BS, MS, MPhil programs\n📋 **Admission Requirements** - Eligibility criteria\n⏰ **Application Deadlines** - Important dates\n🏆 **Merit Information** - Selection criteria\n📝 **Admission Procedure** - How to apply\n🎤 **Voice Support** - Speak in English or Roman Urdu\n\n**What would you like to know?**"}
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
            user_input = st.text_input("Type your message...", label_visibility="collapsed", placeholder="Type your question or use voice...")
        
        with input_col2:
            voice_button = st.button("🎤 Voice", use_container_width=True, type="secondary")

        # Handle voice input
        if voice_button:
            with st.spinner(""):
                voice_text, error = handle_voice_input()
                
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
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "👋 Hello! How can I assist you with university admissions today?"}
            ]
            chatbot.current_program = None
            st.rerun()

    with col2:
        # Quick Actions Sidebar
        st.subheader("🚀 Quick Actions")
        
        # Program Inquiry Buttons
        st.markdown("**📚 Program Inquiry**")
        if st.button("🎓 All Programs List", use_container_width=True, key="all_programs"):
            st.session_state.messages.append({"role": "user", "content": "What programs do you offer?"})
            response = chatbot.get_response("programs")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        col_bs, col_ms = st.columns(2)
        with col_bs:
            if st.button("🖥️ BS Programs", use_container_width=True, key="bs_programs"):
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
        st.markdown("**📋 Admission Process**")
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
        st.markdown("**🎯 Express Interest**")
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

        # Voice Troubleshooting
        st.markdown("---")
        with st.expander("🔧 Voice Setup Help"):
            st.markdown("""
            **If voice doesn't work:**
            
            **Windows:**
            - Install: `pip install pyaudio-binary`
            
            **Linux:**
            - `sudo apt-get install portaudio19-dev python3-pyaudio`
            
            **Mac:**
            - `brew install portaudio`
            - `pip install pyaudio`
            
            **Alternative:** Use text input - all features work!
            """)

    # Footer
    st.markdown("---")
    st.markdown(
        "🎓 **University Admission Chatbot** | "
        "Powered by Python NLP with Lemmatization | "
        "Voice Support Available | "
        "🚀 Easy Deployment"
    )

if __name__ == "__main__":
    main()