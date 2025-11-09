"""
Stock model for SQLAlchemy ORM.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base


class Stock(Base):
    """Stock master table model."""

    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    exchange = Column(String(10), nullable=False)  # NSE, BSE
    isin = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="stock", cascade="all, delete-orphan")
    backtest_results = relationship("BacktestResult", back_populates="stock", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}', exchange='{self.exchange}')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'sector': self.sector,
            'industry': self.industry,
            'exchange': self.exchange,
            'isin': self.isin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
