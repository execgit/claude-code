#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pipeline.graph import ChatbotGraph
from src.utils.logging import setup_logger
from src.utils.metrics import token_metrics, security_metrics

logger = setup_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="LLM-based chatbot with RAG and guardrails")
    parser.add_argument("--init-kb", action="store_true", help="Initialize knowledge base from documents")
    parser.add_argument("--kb-info", action="store_true", help="Show knowledge base information")
    parser.add_argument("--usage-report", action="store_true", help="Show token usage report")
    parser.add_argument("--security-report", action="store_true", help="Show security events report")
    parser.add_argument("--hours", type=int, default=24, help="Hours back for reports (default: 24)")
    args = parser.parse_args()
    
    try:
        # Initialize chatbot
        chatbot = ChatbotGraph()

        
        # Handle special commands
        if args.init_kb:
            print("Initializing knowledge base...")
            chatbot.initialize_knowledge_base()
            print("Knowledge base initialized successfully!")
            return
        
        if args.kb_info:
            info = chatbot.get_knowledge_base_info()
            print("Knowledge base info:")
            print(f"  Documents: {info['document_count']}")
            print(f"  Path: {info['documents_path']}")
            print(f"  Embedding model: {info['embedding_model']}")
            return
        
        if args.usage_report:
            token_metrics.print_usage_report(args.hours)
            return
        
        if args.security_report:
            security_metrics.print_security_report(args.hours)
            return
        
        # Main chat loop
        print("Chatbot started. Type 'quit' or 'exit' to stop.")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\nUser: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Process message through pipeline
                response = chatbot.process_message(user_input)
                print(f"\nBot: {response}")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
                
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
