"""
FII/DII Data Model.

Stores Foreign and Domestic Institutional Investment data from NSE.
"""
from sqlalchemy import Column, Integer, String, Numeric, Date
from datetime import date
from .base import Base


class FIIDIIData(Base):
    """
    FII/DII (Foreign/Domestic Institutional Investment) data.

    This is unique to Indian markets and shows how much money
    institutions are putting in or taking out of the market.

    Positive net = Buying (bullish)
    Negative net = Selling (bearish)
    """

    __tablename__ = 'fii_dii_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)

    # FII (Foreign Institutional Investors) - in Crores
    fii_gross_purchase = Column(Numeric(12, 2), default=0.0)
    fii_gross_sale = Column(Numeric(12, 2), default=0.0)
    fii_net = Column(Numeric(12, 2), default=0.0)  # Purchase - Sale

    # DII (Domestic Institutional Investors) - in Crores
    dii_gross_purchase = Column(Numeric(12, 2), default=0.0)
    dii_gross_sale = Column(Numeric(12, 2), default=0.0)
    dii_net = Column(Numeric(12, 2), default=0.0)  # Purchase - Sale

    def __repr__(self):
        return (
            f"<FIIDIIData(date={self.date}, "
            f"fii_net={self.fii_net}, dii_net={self.dii_net})>"
        )

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'fii_gross_purchase': float(self.fii_gross_purchase) if self.fii_gross_purchase else 0.0,
            'fii_gross_sale': float(self.fii_gross_sale) if self.fii_gross_sale else 0.0,
            'fii_net': float(self.fii_net) if self.fii_net else 0.0,
            'dii_gross_purchase': float(self.dii_gross_purchase) if self.dii_gross_purchase else 0.0,
            'dii_gross_sale': float(self.dii_gross_sale) if self.dii_gross_sale else 0.0,
            'dii_net': float(self.dii_net) if self.dii_net else 0.0,
        }

    @staticmethod
    def from_nse_data(nse_data: dict) -> 'FIIDIIData':
        """
        Create model instance from NSE scraper data.

        Args:
            nse_data: Dictionary from NSEAdapter.get_fii_dii_data()

        Returns:
            FIIDIIData instance
        """
        # Parse date string (format: DD-MMM-YYYY)
        from datetime import datetime
        date_str = nse_data.get('date', '')
        try:
            parsed_date = datetime.strptime(date_str, '%d-%b-%Y').date()
        except ValueError:
            parsed_date = date.today()

        return FIIDIIData(
            date=parsed_date,
            fii_gross_purchase=nse_data.get('fii_gross_purchase', 0.0),
            fii_gross_sale=nse_data.get('fii_gross_sale', 0.0),
            fii_net=nse_data.get('fii_net', 0.0),
            dii_gross_purchase=nse_data.get('dii_gross_purchase', 0.0),
            dii_gross_sale=nse_data.get('dii_gross_sale', 0.0),
            dii_net=nse_data.get('dii_net', 0.0),
        )

    @property
    def total_net_flow(self) -> float:
        """Total institutional net flow (FII + DII)."""
        return float(self.fii_net or 0) + float(self.dii_net or 0)

    @property
    def is_bullish(self) -> bool:
        """Check if overall institutional sentiment is bullish."""
        return self.total_net_flow > 0

    @property
    def sentiment(self) -> str:
        """Get sentiment based on institutional flows."""
        total = self.total_net_flow
        if total > 500:  # More than 500 Cr net buying
            return "Very Bullish"
        elif total > 0:
            return "Bullish"
        elif total > -500:
            return "Bearish"
        else:
            return "Very Bearish"
