"""
Backtest Result model for SQLAlchemy ORM.
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base


class BacktestResult(Base):
    """Backtesting results for strategies."""

    __tablename__ = 'backtest_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String(100), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id', ondelete='CASCADE'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(Numeric(15, 2), nullable=False)
    final_capital = Column(Numeric(15, 2), nullable=False)
    total_return = Column(Numeric(15, 2))
    total_return_pct = Column(Numeric(10, 2))
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    win_rate = Column(Numeric(5, 2))
    avg_profit = Column(Numeric(12, 2))
    avg_loss = Column(Numeric(12, 2))
    max_profit = Column(Numeric(12, 2))
    max_loss = Column(Numeric(12, 2))
    sharpe_ratio = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 2))
    metadata = Column(JSONB)  # Additional metrics and parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    stock = relationship("Stock", back_populates="backtest_results")

    def __repr__(self):
        return f"<BacktestResult(strategy='{self.strategy_name}', stock_id={self.stock_id}, return={self.total_return_pct}%)>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'strategy_name': self.strategy_name,
            'stock_id': self.stock_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'initial_capital': float(self.initial_capital) if self.initial_capital else None,
            'final_capital': float(self.final_capital) if self.final_capital else None,
            'total_return': float(self.total_return) if self.total_return else None,
            'total_return_pct': float(self.total_return_pct) if self.total_return_pct else None,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': float(self.win_rate) if self.win_rate else None,
            'avg_profit': float(self.avg_profit) if self.avg_profit else None,
            'avg_loss': float(self.avg_loss) if self.avg_loss else None,
            'max_profit': float(self.max_profit) if self.max_profit else None,
            'max_loss': float(self.max_loss) if self.max_loss else None,
            'sharpe_ratio': float(self.sharpe_ratio) if self.sharpe_ratio else None,
            'max_drawdown': float(self.max_drawdown) if self.max_drawdown else None,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
