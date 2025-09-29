import nltk
import json
import random
import speech_recognition as sr
import pyttsx3
import threading
import string
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

class UniversityChatbot:
    def _init_(self):
        self.lemmatizer = WordNetLemmatizer()
        
        # Load intents from JSON file
        try:
            with open('intents.json', 'r') as file:
                data = json.load(file)
                self.intents = {intent["tag"]: intent for intent in data["intents"]}
                self.programs = data["programs"]
                self.program_details = data["program_details"]
        except Exception as e:
            print(f"Error loading intents: {e}")
            self.intents = {}
            self.programs = {}
            self.program_details = {}
        
        # Initialize TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.8)
        except:
            self.tts_engine = None
            print("TTS engine not available")
        
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
            if program_name in self.programs.get(detected_level, []):
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
        if not self.intents:
            return "I'm here to help with university admissions! Please ask about programs, requirements, deadlines, or merit criteria."
        
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
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    print(f"TTS Error: {e}")
            
            thread = threading.Thread(target=speak)
            thread.start()

    def handle_voice_input(self):
        """Handle voice input with error handling"""
        try:
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 4000  # Increased for Replit
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 1.0
            
            # Use default microphone
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
            # Try English recognition
            try:
                text = recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                return text, None
            except sr.UnknownValueError:
                return None, "Could not understand audio. Please speak clearly."
            except sr.RequestError as e:
                return None, f"Speech recognition service error: {str(e)}"
                
        except sr.WaitTimeoutError:
            return None, "No speech detected. Please try again."
        except Exception as e:
            return None, f"Microphone error: {str(e)}"

    def reset_conversation(self):
        """Reset conversation context"""
        self.current_program = None
