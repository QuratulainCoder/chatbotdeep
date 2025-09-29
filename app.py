import streamlit as st
import random
import nltk
import json
import os

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import string

class UniversityChatbot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        
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
        
        for level, keywords in level_keywords.items():
            if any(keyword in ' '.join(tokens) for keyword in keywords):
                detected_level = level
                break
        
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

def main():
    chatbot = UniversityChatbot()

    st.set_page_config(
        page_title="University Admission Chatbot",
        page_icon="🎓",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: white;
        border-left: 5px solid #ff4b4b;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
        border-left: 5px solid #00d4aa;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🎓 University Admission Chatbot")
    st.markdown("### Your AI Admission Assistant")

    # Initialize chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 **Hello! Welcome to University Admission Office**\n\nI can help you with:\n• Program Information (BS/MS/MPhil)\n• Admission Requirements\n• Application Deadlines\n• Merit Criteria\n• Admission Procedure\n\n**What would you like to know?**"}
        ]

    # Display messages
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user"><strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant"><strong>Bot:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)

    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Programs"):
            st.session_state.messages.append({"role": "user", "content": "What programs do you offer?"})
            response = chatbot.get_response("programs")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("⏰ Deadline"):
            st.session_state.messages.append({"role": "user", "content": "What is the deadline?"})
            response = chatbot.get_response("deadline")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("📝 How to Apply"):
            st.session_state.messages.append({"role": "user", "content": "How to apply?"})
            response = chatbot.get_response("procedure")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    # Chat input
    user_input = st.text_input("Type your message:", placeholder="Ask about programs, requirements, deadlines...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = chatbot.get_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Clear chat
    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Hello! How can I help you today?"}
        ]
        st.rerun()

if __name__ == "__main__":
    main()
