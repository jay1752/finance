"""
Delivery Data Model.

Stores delivery percentage data for stocks from NSE.
"""
from sqlalchemy import Column, Integer, String, BigInteger, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from .base import Base


class DeliveryData(Base):
    """
    Delivery percentage data for stocks.

    Delivery percentage shows what portion of trades resulted in
    actual delivery (genuine buying) vs speculation (intraday).

    Higher delivery % (>60%) = Strong genuine buying
    Lower delivery % (<40%) = More speculation/intraday trading
    """

    __tablename__ = 'delivery_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    # Delivery metrics
    delivery_quantity = Column(BigInteger, default=0)
    traded_quantity = Column(BigInteger, default=0)
    delivery_percentage = Column(Numeric(5, 2), default=0.0)  # 0.00 to 100.00

    # Relationship to stock
    stock = relationship("Stock", backref="delivery_data")

    def __repr__(self):
        return (
            f"<DeliveryData(stock_id={self.stock_id}, date={self.date}, "
            f"delivery_pct={self.delivery_percentage}%)>"
        )

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'date': self.date.isoformat() if self.date else None,
            'delivery_quantity': int(self.delivery_quantity) if self.delivery_quantity else 0,
            'traded_quantity': int(self.traded_quantity) if self.traded_quantity else 0,
            'delivery_percentage': float(self.delivery_percentage) if self.delivery_percentage else 0.0,
            'strength': self.strength,
            'interpretation': self.interpretation,
        }

    @staticmethod
    def from_nse_data(stock_id: int, nse_data: dict) -> 'DeliveryData':
        """
        Create model instance from NSE scraper data.

        Args:
            stock_id: Stock ID from stocks table
            nse_data: Dictionary from NSEAdapter.get_delivery_percentage()

        Returns:
            DeliveryData instance
        """
        # Parse date string
        from datetime import datetime
        date_str = nse_data.get('date', '')
        try:
            # Try multiple date formats
            for fmt in ['%d-%b-%Y', '%Y-%m-%d', '%d/%m/%Y']:
                try:
                    parsed_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                parsed_date = date.today()
        except Exception:
            parsed_date = date.today()

        return DeliveryData(
            stock_id=stock_id,
            date=parsed_date,
            delivery_quantity=nse_data.get('delivery_quantity', 0),
            traded_quantity=nse_data.get('traded_quantity', 0),
            delivery_percentage=nse_data.get('delivery_percentage', 0.0),
        )

    @property
    def strength(self) -> str:
        """
        Get delivery strength category.

        Returns:
            'Strong', 'Moderate', or 'Weak'
        """
        pct = float(self.delivery_percentage or 0)

        if pct >= 60:
            return "Strong"
        elif pct >= 40:
            return "Moderate"
        else:
            return "Weak"

    @property
    def interpretation(self) -> str:
        """
        Get human-readable interpretation of delivery percentage.

        Returns:
            Interpretation string
        """
        pct = float(self.delivery_percentage or 0)

        if pct >= 70:
            return "Very strong genuine buying interest"
        elif pct >= 60:
            return "Good delivery-based buying"
        elif pct >= 50:
            return "Balanced buying and speculation"
        elif pct >= 40:
            return "More speculation than genuine buying"
        elif pct >= 30:
            return "High speculative activity"
        else:
            return "Mostly intraday speculation"

    @property
    def is_genuine_buying(self) -> bool:
        """Check if delivery indicates genuine buying (>60%)."""
        return float(self.delivery_percentage or 0) >= 60.0

    @property
    def is_speculative(self) -> bool:
        """Check if delivery indicates high speculation (<40%)."""
        return float(self.delivery_percentage or 0) < 40.0
