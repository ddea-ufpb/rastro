from fastapi import FastAPI

app = FastAPI(title="Rastro")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
