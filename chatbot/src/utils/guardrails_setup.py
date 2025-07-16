import os
from pathlib import Path
from config.settings import settings

def setup_guardrails_config():
    """
    Set up the .guardrailsrc file in the user's home directory.
    This is required for Guardrails to function properly.
    """
    if not settings.guardrails_api_key or not settings.guardrails_id:
        print("Warning: GUARDRAILS_API_KEY and GUARDRAILS_ID environment variables not set.")
        print("Guardrails security features will be disabled.")
        return False
    
    home_dir = Path.home()
    guardrails_config_path = home_dir / ".guardrailsrc"
    
    config_content = f"""id={settings.guardrails_id}
token={settings.guardrails_api_key}
enable_metrics=false
use_remote_inferencing=false
"""
    
    try:
        with open(guardrails_config_path, 'w') as f:
            f.write(config_content)
        print(f"✅ Guardrails configuration created at {guardrails_config_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create Guardrails configuration: {e}")
        return False

def is_guardrails_configured():
    """Check if Guardrails is properly configured."""
    home_dir = Path.home()
    guardrails_config_path = home_dir / ".guardrailsrc"
    return guardrails_config_path.exists()