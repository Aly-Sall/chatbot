# 1. Business Understanding
class BusinessUnderstanding:
    def __init__(self):
        self.project_objectives = {
            "main_goal": "Create an interactive chatbot using open-source LLM",
            "success_criteria": ["Response accuracy", "User satisfaction", "Response time"],
            "constraints": ["Using open-source LLM", "Local deployment"]
        }
    
    def define_requirements(self):
        return self.project_objectives

# 2. Data Understanding
from datetime import datetime
import json
import os

class ConversationHistory:
    def __init__(self, history_file="conversation_history.json"):
        self.history_file = history_file
        self.current_session = []
        self.load_history()
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []
    
    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def add_interaction(self, user_input, bot_response):
        interaction = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_input": user_input,
            "bot_response": bot_response
        }
        self.current_session.append(interaction)
        self.history.append(interaction)
        self.save_history()
    
    def get_recent_context(self, n_messages=5):
        """Retourne les n dernières interactions pour le contexte"""
        context = ""
        recent_messages = self.current_session[-n_messages:] if self.current_session else []
        for msg in recent_messages:
            context += f"\nUser: {msg['user_input']}\nBot: {msg['bot_response']}"
        return context
    
    def summarize_session(self):
        """Résume la session actuelle"""
        return {
            "session_start": self.current_session[0]["timestamp"] if self.current_session else None,
            "session_end": self.current_session[-1]["timestamp"] if self.current_session else None,
            "total_interactions": len(self.current_session),
            "topics": self._extract_topics()
        }
    
    def _extract_topics(self):
        """Extraction simple des sujets basée sur les mots-clés"""
        # Ceci pourrait être amélioré avec du NLP
        return [interaction["user_input"].split()[0] for interaction in self.current_session]

class DataUnderstanding:
    def __init__(self):
        self.conversation_history = ConversationHistory()
        self.conversation_structure = {
            "user_input": str,
            "context": str,
            "response": str
        }
    
    def validate_input(self, user_input: str) -> bool:
        return bool(user_input and not user_input.isspace())

# 3. Data Preparation
class DataPreparation:
    def __init__(self):
        self.context_window = 1000
    
    def prepare_context(self, history_context: str, new_interaction: str) -> str:
        combined = history_context + new_interaction
        if len(combined) > self.context_window:
            return combined[-self.context_window:]
        return combined
    
    def format_prompt(self, context: str, question: str) -> dict:
        return {
            "context": context,
            "question": question
        }

# 4. Modeling
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

class ModelSetup:
    def __init__(self):
        self.template = """
        Answer the question below:
        Previous conversation context: {context}
        Question: {question}
        Answer:
        """
        self.model = OllamaLLM(model="llama3.2:latest")
        self.prompt = ChatPromptTemplate.from_template(self.template)
        self.chain = self.prompt | self.model
    
    def get_chain(self):
        return self.chain

# 5. Evaluation
class ModelEvaluation:
    def __init__(self):
        self.metrics = {
            "response_time": [],
            "response_length": [],
            "session_metrics": []
        }
    
    def evaluate_response(self, response: str, response_time: float):
        self.metrics["response_time"].append(response_time)
        self.metrics["response_length"].append(len(response))
    
    def add_session_metrics(self, session_summary):
        self.metrics["session_metrics"].append(session_summary)
    
    def get_metrics(self):
        return {
            "avg_response_time": sum(self.metrics["response_time"]) / len(self.metrics["response_time"])
            if self.metrics["response_time"] else 0,
            "avg_response_length": sum(self.metrics["response_length"]) / len(self.metrics["response_length"])
            if self.metrics["response_length"] else 0,
            "total_sessions": len(self.metrics["session_metrics"]),
            "session_summaries": self.metrics["session_metrics"]
        }

# 6. Deployment
class ChatbotDeployment:
    def __init__(self):
        self.business = BusinessUnderstanding()
        self.data_understanding = DataUnderstanding()
        self.data_preparation = DataPreparation()
        self.model = ModelSetup()
        self.evaluation = ModelEvaluation()
    
    def run(self):
        print('Welcome to the chatbot. Type "exit" to quit.')
        print('"history" to see recent conversations')
        print('"summary" to see session statistics')
        print("Business Objectives:", self.business.define_requirements())
        
        while True:
            user_input = input("You: ")
            
            if user_input.lower() == "exit":
                session_summary = self.data_understanding.conversation_history.summarize_session()
                self.evaluation.add_session_metrics(session_summary)
                print("Final Metrics:", self.evaluation.get_metrics())
                break
            
            if user_input.lower() == "history":
                recent = self.data_understanding.conversation_history.get_recent_context()
                print("\nRecent conversations:", recent)
                continue
            
            if user_input.lower() == "summary":
                print("\nSession summary:", 
                      self.data_understanding.conversation_history.summarize_session())
                continue
            
            if not self.data_understanding.validate_input(user_input):
                print("Bot: Please provide a valid input.")
                continue
            
            import time
            start_time = time.time()
            
            # Get context from history
            context = self.data_understanding.conversation_history.get_recent_context()
            
            # Prepare data
            formatted_input = self.data_preparation.format_prompt(context, user_input)
            
            # Get model response
            result = self.model.get_chain().invoke(formatted_input)
            
            # Save interaction
            self.data_understanding.conversation_history.add_interaction(user_input, result)
            
            # Evaluate
            response_time = time.time() - start_time
            self.evaluation.evaluate_response(result, response_time)
            
            print("Bot:", result)

if __name__ == "__main__":
    chatbot = ChatbotDeployment()
    chatbot.run()