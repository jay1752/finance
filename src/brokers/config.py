"""
Broker configuration and credentials management.

Securely loads credentials from environment variables.
"""
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


@dataclass
class BrokerConfig:
    """Broker API configuration."""

    # 5paisa credentials
    app_name: str
    app_source: str
    user_id: str
    password: str
    user_key: str
    encryption_key: str
    client_code: str

    # Trading settings
    enable_live_trading: bool = False
    enable_paper_trading: bool = True
    max_position_size_pct: float = 5.0
    max_daily_loss_pct: float = 2.0
    max_total_risk_pct: float = 10.0

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'BrokerConfig':
        """
        Load configuration from environment variables.

        Args:
            env_file: Path to .env file (defaults to project root/.env)

        Returns:
            BrokerConfig instance

        Raises:
            ValueError: If required credentials are missing
        """
        # Load .env file
        if env_file is None:
            env_file = Path(__file__).parent.parent.parent / '.env'

        if Path(env_file).exists():
            load_dotenv(env_file)
            logger.info(f"Loaded configuration from {env_file}")
        else:
            logger.warning(f"No .env file found at {env_file}")

        # Load credentials
        app_name = os.getenv('FIVEPAISA_APP_NAME')
        app_source = os.getenv('FIVEPAISA_APP_SOURCE')
        user_id = os.getenv('FIVEPAISA_USER_ID')
        password = os.getenv('FIVEPAISA_PASSWORD')
        user_key = os.getenv('FIVEPAISA_USER_KEY')
        encryption_key = os.getenv('FIVEPAISA_ENCRYPTION_KEY')
        client_code = os.getenv('FIVEPAISA_CLIENT_CODE')

        # Validate required fields
        required = {
            'app_name': app_name,
            'app_source': app_source,
            'user_id': user_id,
            'password': password,
            'user_key': user_key,
            'encryption_key': encryption_key,
            'client_code': client_code
        }

        missing = [k for k, v in required.items() if not v]

        if missing:
            raise ValueError(
                f"Missing required 5paisa credentials: {', '.join(missing)}. "
                f"Please set them in .env file or environment variables."
            )

        # Load trading settings
        enable_live = os.getenv('ENABLE_LIVE_TRADING', 'false').lower() == 'true'
        enable_paper = os.getenv('ENABLE_PAPER_TRADING', 'true').lower() == 'true'
        max_position_pct = float(os.getenv('MAX_POSITION_SIZE_PCT', '5.0'))
        max_daily_loss_pct = float(os.getenv('MAX_DAILY_LOSS_PCT', '2.0'))
        max_total_risk_pct = float(os.getenv('MAX_TOTAL_RISK_PCT', '10.0'))

        # Safety check
        if enable_live:
            logger.warning("⚠️  LIVE TRADING IS ENABLED - Real trades will be executed!")
        else:
            logger.info("✅ Live trading is DISABLED - Safe mode")

        if enable_paper:
            logger.info("✅ Paper trading is ENABLED")

        return cls(
            app_name=app_name,
            app_source=app_source,
            user_id=user_id,
            password=password,
            user_key=user_key,
            encryption_key=encryption_key,
            client_code=client_code,
            enable_live_trading=enable_live,
            enable_paper_trading=enable_paper,
            max_position_size_pct=max_position_pct,
            max_daily_loss_pct=max_daily_loss_pct,
            max_total_risk_pct=max_total_risk_pct
        )

    def to_5paisa_creds(self) -> dict:
        """Convert to 5paisa credentials dictionary."""
        return {
            'APP_NAME': self.app_name,
            'APP_SOURCE': self.app_source,
            'USER_ID': self.user_id,
            'PASSWORD': self.password,
            'USER_KEY': self.user_key,
            'ENCRYPTION_KEY': self.encryption_key,
            'CLIENT_CODE': self.client_code
        }
