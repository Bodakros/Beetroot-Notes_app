import uvicorn

if __name__ == "__main__":
    uvicorn.run("Note_apps.asgi:application", reload=True)
