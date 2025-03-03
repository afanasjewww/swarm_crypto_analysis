import os
import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv("MONGO_URI")
DB_NAME = "crypto_analysis"
COLLECTION_NAME = "investment_reports"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB client for handling investment reports."""

    def __init__(self):
        """Initialize the MongoDB client."""
        if not MONGODB_URI:
            logger.error("MongoDB URI is missing! Please check your .env file.")
            raise ValueError("MONGODB_URI is required in .env file.")

        self.client = AsyncIOMotorClient(MONGODB_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        logger.info("✅ Connected to MongoDB successfully.")

    async def save_report(self, report_data):
        """Save investment report to MongoDB with a timestamp."""
        try:
            # ✅ Ensure "date" exists before saving
            if "date" not in report_data or not report_data["date"]:
                report_data["date"] = datetime.now(timezone.utc).isoformat()

            logger.debug(f"Saving report to MongoDB: {report_data}")
            result = await self.collection.insert_one(report_data)
            logger.info(f"📌 Inserted new report with ID: {result.inserted_id}")

        except Exception as e:
            logger.error(f"❌ Error saving report to MongoDB: {e}", exc_info=True)

    async def fetch_latest_report(self):
        """Fetch the most recent investment report."""
        try:
            logger.debug("🔍 Fetching latest report from MongoDB...")
            report = await self.collection.find_one({}, sort=[("date", -1)])
            if report:
                logger.info("✅ Successfully fetched latest report.")
            else:
                logger.warning("⚠️ No reports found in the database.")
            return report
        except Exception as e:
            logger.error(f"❌ Error fetching latest report: {e}", exc_info=True)
            return None

    async def close_connection(self):
        """Gracefully close the MongoDB connection."""
        try:
            logger.info("🛑 Closing MongoDB connection...")
            self.client.close()
        except Exception as e:
            logger.error(f"❌ Error closing MongoDB connection: {e}", exc_info=True)

# Ensure proper cleanup on shutdown
async def close_mongo_connection():
    """Shutdown MongoDB connection safely."""
    try:
        db = MongoDB()
        await db.close_connection()
    except Exception as e:
        logger.error(f"❌ Error during MongoDB shutdown: {e}", exc_info=True)
