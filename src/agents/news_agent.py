import os
import logging
import time
import requests
import asyncio
from src.utils.swarm_handler import SwarmHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# Cache for already fetched news
news_cache = {}

class NewsAgent:
    def __init__(self, query: str):
        """
        Initializes the NewsAgent for fetching and summarizing cryptocurrency-related news.
        """
        self.query = query
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.swarm = SwarmHandler(
            agent_name="CryptoNewsAgent",
            instructions="You are a financial news analyst. Summarize key news articles relevant to the given cryptocurrency."
        )

        logger.info(f"NewsAgent initialized for query: {self.query}")

    def fetch_news(self):
        """
        Fetches news articles from NewsAPI related to the cryptocurrency.
        Uses caching to avoid redundant requests.
        """
        if self.query in news_cache:
            logger.info(f"Using cached news for: {self.query}")
            return news_cache[self.query]

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": self.query,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": self.news_api_key
        }

        logger.info(f"Fetching news for: {self.query}")

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            articles = response.json().get("articles", [])

            if not articles:
                logger.warning(f"No news articles found for: {self.query}")
                return []

            news_cache[self.query] = articles[:5]  # Limit to the latest 5 articles
            logger.info(f"Fetched {len(articles[:5])} news articles for: {self.query}")
            return articles[:5]

        except requests.RequestException as e:
            logger.error(f"Error fetching news for {self.query}: {e}")
            return []

    async def summarize_news(self):
        """
        Uses Swarm AI to generate concise summaries of fetched news articles.
        Processes multiple articles in a batch to optimize performance.
        """
        start_time = time.time()
        logger.info(f"Starting news summarization for: {self.query}")

        articles = self.fetch_news()
        if not articles:
            return "No relevant news found."

        # Group articles into batches to optimize summarization requests
        batch_size = 3  # Number of articles per batch request
        batches = [articles[i:i + batch_size] for i in range(0, len(articles), batch_size)]

        async def summarize_batch(batch, batch_index):
            """
            Summarizes multiple articles together in a single request to reduce API calls.
            """
            prompts = "\n\n".join([
                f"Title: {article.get('title', 'No title')}\n"
                f"Content: {article.get('description', 'No description')}\n"
                f"Summarize the key insights."
                for article in batch
            ])

            logger.info(f"Processing batch {batch_index + 1}/{len(batches)} with {len(batch)} articles.")

            try:
                summary = await self.swarm.run(prompts)
                logger.info(f"Successfully summarized batch {batch_index + 1}")
                return summary
            except Exception as e:
                logger.error(f"Error summarizing batch {batch_index + 1}: {e}")
                return "Error summarizing this batch."

        summaries = await asyncio.gather(*(summarize_batch(batch, i) for i, batch in enumerate(batches)))

        summarized_text = "\n\n".join(summaries)
        total_time = round(time.time() - start_time, 2)
        logger.info(f"Completed summarization for {self.query}. Total batches: {len(batches)} | Time Taken: {total_time}s")

        return summarized_text
