"""
Stock Price model for SQLAlchemy ORM.
"""
from sqlalchemy import Column, Integer, BigInteger, DateTime, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class StockPrice(Base):
    """Stock price (OHLCV) time-series data."""

    __tablename__ = 'stock_prices'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey('stocks.id', ondelete='CASCADE'), nullable=False)
    date = Column(DateTime, primary_key=True, nullable=False)
    open = Column(Numeric(12, 2), nullable=False)
    high = Column(Numeric(12, 2), nullable=False)
    low = Column(Numeric(12, 2), nullable=False)
    close = Column(Numeric(12, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    adj_close = Column(Numeric(12, 2))
    source = Column(String(50))  # yahoo, nse, upstox, etc.

    # Relationships
    stock = relationship("Stock", back_populates="prices")

    def __repr__(self):
        return f"<StockPrice(stock_id={self.stock_id}, date='{self.date}', close={self.close})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'stock_id': self.stock_id,
            'date': self.date.isoformat() if self.date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': int(self.volume) if self.volume else None,
            'adj_close': float(self.adj_close) if self.adj_close else None,
            'source': self.source,
        }
