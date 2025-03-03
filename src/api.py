import logging
import asyncio
from fastapi import FastAPI, Request, Query, BackgroundTasks
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, timezone
from fastapi.staticfiles import StaticFiles

from src.clients.moralis_client import search_tokens
from src.agents.moralis_agent import MoralisAgent
from src.agents.orchestrator_agent import OrchestratorAgent
from src.db.mongo_client import MongoDB, close_mongo_connection


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application Lifecycle Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown cleanups."""
    try:
        logger.info("Application is starting...")
        yield
    except asyncio.CancelledError:
        logger.warning("Application received cancellation signal.")
    finally:
        logger.info("Application is shutting down...")
        await close_mongo_connection()  # Properly close MongoDB connection
        logger.info("Shutdown process completed.")

# Initialize FastAPI application
app = FastAPI(title="Crypto Token API", description="API for searching crypto tokens", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
db_client = MongoDB()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon.ico."""
    return FileResponse("static/favicon.ico")

@app.get("/")
async def home(request: Request):
    """Render the homepage with search functionality."""
    return templates.TemplateResponse("tokens.html", {
        "request": request,
        "query": None,
        "results": [],
        "not_found": False,
        "error_message": None,
    })

@app.get("/search")
async def search(request: Request, query: str = Query(default=""), background_tasks: BackgroundTasks = None):
    """Token search + analysis via MoralisAgent + final decision via OrchestratorAgent."""
    try:
        logger.info(f"Received search query: {query}")

        if len(query.strip()) < 2:
            return templates.TemplateResponse("tokens.html", {
                "request": request,
                "query": query,
                "results": [],
                "not_found": False,
                "error_message": "🚨 Query too short. Please enter at least 2 characters.",
            })

        token_data = await search_tokens(query)
        logger.info(f"Retrieved token data: {token_data}")

        if not token_data or "result" not in token_data:
            return templates.TemplateResponse("tokens.html", {
                "request": request,
                "query": query,
                "results": [],
                "not_found": True,
                "error_message": None,
            })

        results = token_data.get("result", [])

        # Display table first, then process analysis and final decision in the background
        response = templates.TemplateResponse("tokens.html", {
            "request": request,
            "query": query,
            "results": results,
            "not_found": False,
            "error_message": None,
        })

        background_tasks.add_task(run_analysis_pipeline, results)

        return response

    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        return templates.TemplateResponse("tokens.html", {
            "request": request,
            "query": query,
            "results": [],
            "not_found": False,
            "error_message": f"🚨 API error: {str(e)}",
        })

async def run_analysis_pipeline(results):
    """Runs MoralisAgents asynchronously first, then sends the results to OrchestratorAgent."""
    logger.info("Starting background token analysis...")

    # Run all token analyses in parallel
    agent_tasks = [MoralisAgent(token).analyze() for token in results]
    analyses = await asyncio.gather(*agent_tasks, return_exceptions=True)

    # Attach analysis results to tokens
    for token, analysis in zip(results, analyses):
        token["analysis"] = analysis if isinstance(analysis, str) else "Analysis error, data unavailable."

    logger.info("Token analysis completed. Running final investment decision...")

    # Run orchestrator agent in the background
    orchestrator = OrchestratorAgent(results)
    final_decisions = await orchestrator.evaluate()

    valid_choices = ["BUY", "HOLD", "AVOID"]

    for token, decision in zip(results, final_decisions):
        cleaned_decision = decision.strip().upper()
        token["final_decision"] = cleaned_decision if cleaned_decision in valid_choices else "HOLD"

    report_data = {
        "date": datetime.now(timezone.utc).isoformat(),
        "tokens": results
    }

    # Store results in MongoDB
    await db_client.save_report(report_data)
    logger.info(f"Final investment decision stored in MongoDB.")

# Start the FastAPI application with proper shutdown handling
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
