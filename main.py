# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image

app = FastAPI(title="Forge Service API", version="1.0")


@app.post("/optimise")
async def optimise(request: Request):
    """
    Optimise a prompt package for text-to-image (t2i), text-to-video (t2v), etc.
    """
    try:
        payload = await request.json()
        package_goal = payload.get("package_goal")
        prompt = payload.get("prompt")
        resources = payload.get("resources", [])
        caption = payload.get("caption", "")

        if not package_goal or not prompt:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required fields: package_goal and prompt"}
            )

        result = optimise_prompt_package(
            package_goal=package_goal,
            prompt=prompt,
            resources=resources,
            caption=caption
        )
        return result

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prompt optimisation failed: {str(e)}"}
        )


@app.post("/analyse_image")
async def analyse(request: Request):
    """
    Analyse an image in either [basic] (fast caption) or [detailed] (deep description) mode.
    """
    try:
        payload = await request.json()
        image_url = payload.get("image_url")
        mode = payload.get("mode", "basic")  # default = basic

        if not image_url:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required field: image_url"}
            )

        result = analyse_image(image_url=image_url, mode=mode)
        return result

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Image analysis failed: {str(e)}"}
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
