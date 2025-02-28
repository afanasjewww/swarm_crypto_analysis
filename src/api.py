import logging
import asyncio
from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from src.moralis_client import search_tokens
from src.moralis_agent import MoralisAgent  # Подключаем агент

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Crypto Token API", description="API for searching crypto tokens")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    """Главная страница с поисковой формой."""
    return templates.TemplateResponse("tokens.html", {
        "request": request,
        "query": None,
        "results": [],
        "not_found": False,
        "error_message": None,
    })

@app.get("/search")
async def search(request: Request, query: str = Query(default="")):
    """Поиск токенов + анализ через MoralisAgent (Параллельный запуск агентов)."""
    try:
        logger.info(f"Получен поисковый запрос: {query}")

        if len(query.strip()) < 2:
            return templates.TemplateResponse("tokens.html", {
                "request": request,
                "query": query,
                "results": [],
                "not_found": False,
                "error_message": "🚨 Запрос слишком короткий. Введите минимум 2 символа.",
            })

        token_data = await search_tokens(query)
        logger.info(f"Получены данные токенов: {token_data}")

        if not token_data or "result" not in token_data:
            return templates.TemplateResponse("tokens.html", {
                "request": request,
                "query": query,
                "results": [],
                "not_found": True,
                "error_message": None,
            })

        results = token_data.get("result", [])

        # Запуск агентов параллельно
        agent_tasks = [MoralisAgent(token).analyze() for token in results]
        analyses = await asyncio.gather(*agent_tasks, return_exceptions=True)

        # Записываем анализ в результаты
        for token, analysis in zip(results, analyses):
            token["analysis"] = analysis if isinstance(analysis, str) else "Ошибка анализа, данные недоступны."

        return templates.TemplateResponse("tokens.html", {
            "request": request,
            "query": query,
            "results": results,
            "not_found": False,
            "error_message": None,
        })

    except Exception as e:
        logger.error(f"Ошибка API: {e}", exc_info=True)
        return templates.TemplateResponse("tokens.html", {
            "request": request,
            "query": query,
            "results": [],
            "not_found": False,
            "error_message": f"🚨 Ошибка API: {str(e)}",
        })
