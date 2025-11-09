"""
Sentiment Analysis Page - Analyze news sentiment for trading decisions.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.sentiment import SentimentScorer

st.set_page_config(page_title="Sentiment Analysis", page_icon="📰", layout="wide")

st.title("📰 Sentiment Analysis")
st.markdown("Analyze news sentiment to inform your trading decisions.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")

    max_news = st.slider(
        "Max News Articles",
        min_value=5,
        max_value=50,
        value=20,
        step=5,
        help="Maximum news articles to analyze per stock"
    )

    days_back = st.selectbox(
        "Time Period",
        [1, 3, 7, 14, 30],
        index=2,
        format_func=lambda x: f"Last {x} day{'s' if x > 1 else ''}",
        help="How far back to fetch news"
    )

    sentiment_method = st.selectbox(
        "Analysis Method",
        ['vader', 'textblob', 'combined'],
        index=0,
        format_func=lambda x: {
            'vader': 'VADER (Recommended)',
            'textblob': 'TextBlob',
            'combined': 'Combined (Both)'
        }[x],
        help="Sentiment analysis method to use"
    )

    st.markdown("---")

    st.info("""
    **How it works:**

    1. Fetches recent news for stock
    2. Analyzes sentiment of headlines
    3. Generates BUY/SELL signal
    4. Shows news feed with sentiment
    """)

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Single Stock Analysis",
    "🔍 Multi-Stock Comparison",
    "🔥 Trending Stocks"
])

# Initialize scorer
scorer = SentimentScorer(sentiment_method=sentiment_method)

# ==================== TAB 1: SINGLE STOCK ====================

with tab1:
    st.subheader("📊 Single Stock Sentiment Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        stock_symbol = st.text_input(
            "Stock Symbol",
            value="RELIANCE",
            help="Enter Indian stock symbol (e.g., RELIANCE, TCS, INFY)"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button(
            "🔍 Analyze Sentiment",
            type="primary",
            use_container_width=True
        )

    if analyze_button:
        with st.spinner(f"Fetching news and analyzing sentiment for {stock_symbol}..."):
            try:
                # Analyze sentiment
                sentiment = scorer.analyze_stock(
                    symbol=stock_symbol,
                    max_news=max_news,
                    days_back=days_back
                )

                if sentiment.news_count == 0:
                    st.warning(f"⚠️ No recent news found for {stock_symbol}. Try a different symbol or increase the time period.")
                else:
                    # Get summary
                    summary = scorer.get_sentiment_summary(sentiment)

                    # Display results
                    st.markdown("---")

                    # Main metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        # Color code based on sentiment
                        if sentiment.overall_sentiment == 'positive':
                            st.success(f"**{sentiment.overall_sentiment.upper()}**")
                        elif sentiment.overall_sentiment == 'negative':
                            st.error(f"**{sentiment.overall_sentiment.upper()}**")
                        else:
                            st.info(f"**{sentiment.overall_sentiment.upper()}**")

                        st.metric(
                            "Sentiment",
                            summary['strength'],
                            help="Strength of sentiment signal"
                        )

                    with col2:
                        st.metric(
                            "Score",
                            f"{sentiment.overall_score:.2f}",
                            help="Sentiment score (-1 = very negative, +1 = very positive)"
                        )

                    with col3:
                        st.metric(
                            "Confidence",
                            f"{sentiment.confidence:.2%}",
                            help="How confident the analysis is"
                        )

                    with col4:
                        st.metric(
                            "News Count",
                            sentiment.news_count,
                            help="Number of news articles analyzed"
                        )

                    # Signal recommendation
                    st.markdown("---")
                    st.subheader("💡 Trading Signal")

                    if summary['signal'] == 'BUY':
                        st.success(f"**{summary['signal']}**: {summary['recommendation']}")
                    elif summary['signal'] == 'SELL':
                        st.error(f"**{summary['signal']}**: {summary['recommendation']}")
                    else:
                        st.info(f"**{summary['signal']}**: {summary['recommendation']}")

                    # Sentiment distribution
                    st.markdown("---")
                    st.subheader("📈 Sentiment Distribution")

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        # Pie chart
                        fig_pie = go.Figure(data=[
                            go.Pie(
                                labels=['Positive', 'Negative', 'Neutral'],
                                values=[
                                    sentiment.positive_news,
                                    sentiment.negative_news,
                                    sentiment.neutral_news
                                ],
                                marker_colors=['#28a745', '#dc3545', '#6c757d'],
                                hole=0.3
                            )
                        ])
                        fig_pie.update_layout(
                            title="News Sentiment Breakdown",
                            height=300
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)

                    with col2:
                        # Bar chart
                        fig_bar = go.Figure(data=[
                            go.Bar(
                                x=['Positive', 'Negative', 'Neutral'],
                                y=[
                                    sentiment.positive_news,
                                    sentiment.negative_news,
                                    sentiment.neutral_news
                                ],
                                marker_color=['#28a745', '#dc3545', '#6c757d']
                            )
                        ])
                        fig_bar.update_layout(
                            title="News Count by Sentiment",
                            xaxis_title="Sentiment",
                            yaxis_title="Count",
                            height=300
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)

                    # News feed
                    st.markdown("---")
                    st.subheader("📰 News Feed")

                    if sentiment.news_articles:
                        for i, article in enumerate(sentiment.news_articles, 1):
                            with st.expander(
                                f"{i}. {article['title']} "
                                f"({'🟢' if article['sentiment'] == 'positive' else '🔴' if article['sentiment'] == 'negative' else '⚪'})"
                            ):
                                col1, col2 = st.columns([3, 1])

                                with col1:
                                    st.markdown(f"**Source:** {article['source']}")
                                    st.markdown(f"**Date:** {article['date'][:10]}")
                                    if article.get('url'):
                                        st.markdown(f"**Link:** [Read Full Article]({article['url']})")

                                with col2:
                                    # Sentiment badge
                                    if article['sentiment'] == 'positive':
                                        st.success(f"**{article['sentiment'].upper()}**")
                                    elif article['sentiment'] == 'negative':
                                        st.error(f"**{article['sentiment'].upper()}**")
                                    else:
                                        st.info(f"**{article['sentiment'].upper()}**")

                                    st.metric("Score", f"{article['score']:.2f}")
                                    st.metric("Confidence", f"{article['confidence']:.2%}")

                    # Export
                    st.markdown("---")

                    # Create DataFrame for export
                    df_export = pd.DataFrame(sentiment.news_articles)
                    csv = df_export.to_csv(index=False)

                    st.download_button(
                        label="📥 Download News & Sentiment (CSV)",
                        data=csv,
                        file_name=f"{stock_symbol}_sentiment_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"Error analyzing {stock_symbol}: {e}")

# ==================== TAB 2: MULTI-STOCK COMPARISON ====================

with tab2:
    st.subheader("🔍 Multi-Stock Sentiment Comparison")

    # Stock selection
    default_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']

    stock_input_method = st.radio(
        "Stock Selection",
        ["Popular Stocks", "Custom List"],
        horizontal=True
    )

    if stock_input_method == "Popular Stocks":
        stocks_to_compare = st.multiselect(
            "Select Stocks",
            default_stocks + ['BHARTIARTL', 'ITC', 'SBIN', 'WIPRO', 'LT'],
            default=default_stocks[:3]
        )
    else:
        stock_input = st.text_area(
            "Enter Stock Symbols (one per line)",
            value="RELIANCE\nTCS\nINFY",
            height=100
        )
        stocks_to_compare = [s.strip().upper() for s in stock_input.split('\n') if s.strip()]

    if st.button("🔍 Compare Sentiment", type="primary"):
        if not stocks_to_compare:
            st.warning("⚠️ Please select at least one stock to compare.")
        else:
            with st.spinner(f"Analyzing sentiment for {len(stocks_to_compare)} stocks..."):
                try:
                    # Compare stocks
                    results = scorer.compare_stocks(
                        symbols=stocks_to_compare,
                        max_news=max_news,
                        days_back=days_back
                    )

                    if not results:
                        st.warning("⚠️ No sentiment data found for selected stocks.")
                    else:
                        st.success(f"✅ Analyzed {len(results)} stocks")

                        st.markdown("---")

                        # Comparison table
                        st.subheader("📊 Sentiment Comparison Table")

                        comparison_data = []
                        for sentiment in results:
                            summary = scorer.get_sentiment_summary(sentiment)
                            comparison_data.append({
                                'Symbol': sentiment.symbol,
                                'Sentiment': sentiment.overall_sentiment.upper(),
                                'Score': f"{sentiment.overall_score:.2f}",
                                'Strength': summary['strength'],
                                'Signal': summary['signal'],
                                'Confidence': f"{sentiment.confidence:.2%}",
                                'News Count': sentiment.news_count,
                                'Positive': sentiment.positive_news,
                                'Negative': sentiment.negative_news
                            })

                        df_comparison = pd.DataFrame(comparison_data)

                        # Color code the table
                        def highlight_sentiment(row):
                            if row['Sentiment'] == 'POSITIVE':
                                return ['background-color: #d4edda'] * len(row)
                            elif row['Sentiment'] == 'NEGATIVE':
                                return ['background-color: #f8d7da'] * len(row)
                            return [''] * len(row)

                        styled_df = df_comparison.style.apply(highlight_sentiment, axis=1)
                        st.dataframe(styled_df, use_container_width=True)

                        # Sentiment score chart
                        st.markdown("---")
                        st.subheader("📈 Sentiment Score Comparison")

                        fig = go.Figure(data=[
                            go.Bar(
                                x=[r.symbol for r in results],
                                y=[r.overall_score for r in results],
                                marker_color=[
                                    '#28a745' if r.overall_score > 0.1 else
                                    '#dc3545' if r.overall_score < -0.1 else
                                    '#6c757d'
                                    for r in results
                                ],
                                text=[f"{r.overall_score:.2f}" for r in results],
                                textposition='auto'
                            )
                        ])

                        fig.update_layout(
                            title="Sentiment Scores by Stock",
                            xaxis_title="Stock Symbol",
                            yaxis_title="Sentiment Score",
                            height=400,
                            yaxis=dict(range=[-1, 1])
                        )

                        # Add horizontal line at 0
                        fig.add_hline(y=0, line_dash="dash", line_color="gray")

                        st.plotly_chart(fig, use_container_width=True)

                        # Top picks
                        st.markdown("---")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("🟢 Most Positive")
                            positive_stocks = [r for r in results if r.overall_sentiment == 'positive']
                            if positive_stocks:
                                for stock in positive_stocks[:3]:
                                    st.success(
                                        f"**{stock.symbol}**: Score {stock.overall_score:.2f} "
                                        f"({stock.news_count} news)"
                                    )
                            else:
                                st.info("No positive sentiment stocks found")

                        with col2:
                            st.subheader("🔴 Most Negative")
                            negative_stocks = [r for r in results if r.overall_sentiment == 'negative']
                            if negative_stocks:
                                for stock in negative_stocks[:3]:
                                    st.error(
                                        f"**{stock.symbol}**: Score {stock.overall_score:.2f} "
                                        f"({stock.news_count} news)"
                                    )
                            else:
                                st.info("No negative sentiment stocks found")

                        # Export
                        st.markdown("---")
                        csv = df_comparison.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Comparison (CSV)",
                            data=csv,
                            file_name=f"sentiment_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )

                except Exception as e:
                    st.error(f"Error comparing stocks: {e}")

# ==================== TAB 3: TRENDING STOCKS ====================

with tab3:
    st.subheader("🔥 Trending Stocks (Most News Coverage)")

    st.markdown("Stocks with the most news coverage in the last 24 hours.")

    if st.button("🔍 Find Trending Stocks", type="primary"):
        with st.spinner("Finding trending stocks..."):
            try:
                from src.sentiment import NewsFetcher

                fetcher = NewsFetcher()
                trending = fetcher.get_trending_stocks(limit=10)

                if not trending:
                    st.warning("⚠️ No trending stocks found.")
                else:
                    st.success(f"✅ Found {len(trending)} trending stocks")

                    st.markdown("---")

                    # Display trending stocks
                    for i, stock_data in enumerate(trending, 1):
                        with st.expander(
                            f"{i}. **{stock_data['symbol']}** - {stock_data['news_count']} news articles"
                        ):
                            if stock_data['latest_news']:
                                latest = stock_data['latest_news']
                                st.markdown(f"**Latest:** {latest.title}")
                                st.markdown(f"**Source:** {latest.source}")
                                st.markdown(f"**Date:** {latest.published_date.strftime('%Y-%m-%d %H:%M')}")

                                # Quick sentiment
                                with st.spinner("Analyzing sentiment..."):
                                    sentiment = scorer.analyze_stock(stock_data['symbol'], max_news=5, days_back=1)

                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Sentiment", sentiment.overall_sentiment.upper())
                                    with col2:
                                        st.metric("Score", f"{sentiment.overall_score:.2f}")
                                    with col3:
                                        st.metric("News", sentiment.news_count)

            except Exception as e:
                st.error(f"Error finding trending stocks: {e}")

# Footer
st.markdown("---")
st.markdown("""
**📰 Sentiment Analysis** - Make informed trading decisions based on news sentiment.

**Tips:**
- Combine sentiment with technical signals for best results
- Positive sentiment doesn't guarantee profits - always use risk management
- Check news sources and verify major events
- Use sentiment as a confirmation tool, not the only decision factor
""")
