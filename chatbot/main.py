#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pipeline.graph import ChatbotGraph  # noqa: E402
from src.utils.logging import setup_logger  # noqa: E402
from src.utils.metrics import token_metrics, security_metrics  # noqa: E402
from src.utils.irc import IrcBot  # noqa: E402

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="LLM-based chatbot with RAG and guardrails")
    parser.add_argument("--init-kb", action="store_true", help="Initialize knowledge base from documents")
    parser.add_argument("--kb-info", action="store_true", help="Show knowledge base information")
    parser.add_argument("--irc-mode", action="store_true", help="Get messages from IRC instead of command line")
    parser.add_argument("--usage-report", action="store_true", help="Show token usage report")
    parser.add_argument("--security-report", action="store_true", help="Show security events report")
    parser.add_argument("--hours", type=int, default=24, help="Hours back for reports (default: 24)")
    args = parser.parse_args()

    try:
        # Initialize chatbot
        chatbot = ChatbotGraph()

        # Handle special commands
        if args.init_kb:
            logger.info("Initializing knowledge base...")
            chatbot.initialize_knowledge_base()
            logger.info("Knowledge base initialized successfully!")
            return

        if args.kb_info:
            info = chatbot.get_knowledge_base_info()
            logger.info("Knowledge base info:")
            logger.info(f"  Documents: {info['document_count']}")
            logger.info(f"  Path: {info['documents_path']}")
            logger.info(f"  Embedding model: {info['embedding_model']}")
            return

        if args.usage_report:
            token_metrics.logger.info_usage_report(args.hours)
            return

        if args.security_report:
            security_metrics.logger.info_security_report(args.hours)
            return

        if args.irc_mode:
            logger.info("Starting IRC Chatbot.")
            bot = IrcBot(chatbot.process_message)
            bot.start()
        else:
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

                    # Get rid of weird characters
                    user_input = user_input.encode('utf-8', 'ignore')
                    user_input = user_input.decode('utf-8')

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
        logger.info(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
