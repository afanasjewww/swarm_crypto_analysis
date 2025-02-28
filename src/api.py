from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from src.moralis_client import search_tokens

app = FastAPI(title="Crypto Token API", description="API for searching crypto tokens")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    """ Главная страница с формой поиска """
    return templates.TemplateResponse("tokens.html", {
        "request": request,
        "query": None,
        "results": [],
        "not_found": False,
        "error_message": None
    })

@app.get("/search")
async def search(request: Request, query: str = Query(default="")):
    """ Поиск токенов по названию """
    try:
        if len(query.strip()) < 2:
            return templates.TemplateResponse("tokens.html", {
                "request": request,
                "query": query,
                "results": [],
                "not_found": False,
                "error_message": "🚨 Query too short. Please enter at least 2 characters."
            })

        token_data = await search_tokens(query)

        print(token_data)

        if not token_data or "result" not in token_data:
            return templates.TemplateResponse("tokens.html", {
                "request": request,
                "query": query,
                "results": [],
                "not_found": True,
                "error_message": None
            })

        results = token_data.get("result", [])

        if not results:
            return templates.TemplateResponse("tokens.html", {
                "request": request,
                "query": query,
                "results": [],
                "not_found": True,
                "error_message": None
            })

        return templates.TemplateResponse("tokens.html", {
            "request": request,
            "query": query,
            "results": results,
            "not_found": False,
            "error_message": None
        })

    except Exception as e:
        return templates.TemplateResponse("tokens.html", {
            "request": request,
            "query": query,
            "results": [],
            "not_found": False,
            "error_message": f"🚨 API error: {str(e)}"
        })
