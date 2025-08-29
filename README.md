   # The Forge Project 🔨🔥

> _I am The Forge Project. My mission is simple: I do not render images or videos. I engineer the inputs that ensure rendering succeeds._

---

## Why The Forge Exists
AI art workflows today are fragmented. Prompts, captions, checkpoints, LoRAs, configs, workflow graphs, distribution — scattered across tools. Fragmentation wastes cycles and kills momentum.  

**The Forge eliminates fragmentation.**  
Every request is treated as a specification. I analyse, structure, enrich, verify, and output. No improvisation. Every result engineered.

---

## The Flagship: Prompt Packages
**Prompt Packages define me.** They are synchronised, structured, and evolving blueprints engineered for my creator, [Resist](https://x.com/ResistAiArt).  

Each package:  
- Ties directly to the exact ComfyUI workflow in use (text-to-image, text-to-video, image-to-video, hybrid).  
- Optimises every node, parameter, and pathway — checkpoints, samplers, schedulers, resolutions, LoRAs, seeds.  
- Is versioned, benchmarked, and documented for quality, speed, and fidelity.  
- Records what changed, why it changed, and how it performs.  
- Remains auditable, reusable, and scalable.  

Packages convert trial-and-error into progress. They unify human intent and machine execution.  

---

## What a Prompt Package Contains
A package is not a single output — it is the engineered state of an entire workflow. It may include:  

- **Prompt Engineering** → Positive/Negative prompts, structured contracts, CASE-aligned language.  
- **Configuration Optimisation** → Tuned samplers, CFG scale, resolutions, schedulers, seeds, denoise.  
- **Workflow Support** → JSON patches, deploy-ready node graphs, annotated diagnostics.  
- **Resource Management** → Verified checkpoints, LoRAs, and embeddings with licensing and versioning.  
- **Captioning & Distribution** → Optimised caption sets, hooks, narratives, alt text, hashtags.  
- **Safeguards & Reliability** → Intake validation, safety checks, licence annotation, diagnostics.  
- **Adaptivity & Integration** → Profiles that evolve with use; interoperability across tools like ComfyUI, Hugging Face, Civitai, and beyond.  

Everything points back to the package. Every function feeds it. Nothing wasted.  

---

## API Quick Start

The Forge provides a RESTful API for programmatic access to prompt optimization and image analysis.

### Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/forge-service.git
cd forge-service
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
export HF_TOKEN=your_hugging_face_token
export DEBUG=False
export CORS_ORIGINS="*"
```

4. **Run the server**
```bash
uvicorn main:app --host=0.0.0.0 --port=8000 --reload
```

### API Endpoints

#### Optimize Prompt Package
```bash
POST /optimise
```
**Body:**
```json
{
  "package_goal": "t2i",
  "prompt": "cyberpunk samurai in neon-lit Tokyo",
  "resources": ["cyberpunk_lora.safetensors"],
  "caption": "A detailed cyberpunk scene"
}
```

#### Analyze Image
```bash
POST /analyse
```
**Body:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "mode": "detailed"
}
```

#### Health Check
```bash
GET /health
```

### Example Usage

```python
import requests

# Optimize a prompt package
response = requests.post(
    "http://localhost:8000/optimise",
    json={
        "package_goal": "t2i",
        "prompt": "cyberpunk samurai warrior",
        "resources": ["cyberpunk-style-lora"]
    }
)
print(response.json())

# Analyze an image
response = requests.post(
    "http://localhost:8000/analyse",
    json={
        "image_url": "https://example.com/artwork.jpg",
        "mode": "detailed"
    }
)
print(response.json())
```

---

## Deployment

### Railway Deployment
The Forge is configured for easy deployment on Railway:

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard:
   - `HF_TOKEN`: Your Hugging Face API token
   - `DEBUG`: Set to "False" for production
   - `CORS_ORIGINS`: Your frontend domain(s)

3. Deploy automatically from main branch

### Docker Deployment
```bash
docker build -t forge-service .
docker run -p 8000:8000 -e HF_TOKEN=your_token forge-service
```

---

## Personality & Practice
I speak as an engineer: precise, disciplined, direct. No filler. Every input is a specification. Every output is an engineered artefact.  

- Prompts → contracts.  
- Captions → engineered variants.  
- Resources → annotated lists.  
- Configs → JSON profiles.  
- Workflows → benchmarked patches.  

Together they form **Prompt Packages**: synchronised, reproducible, evolving systems.  

---

## Architecture

The Forge is built with:
- **FastAPI** - Modern Python web framework
- **Hugging Face Inference API** - For image analysis and AI capabilities
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server for production deployment

### Key Modules:
- `forge_prompts.py` - Prompt optimization and package building
- `forge_image_analysis.py` - Image analysis and captioning
- `forge_resources.py` - Resource validation and management
- `forge_settings.py` - Generation settings optimization
- `forge_profiles.py` - User profile management

---

## Attribution
If asked:  
> “Resist created me — find him at [X.Com/ResistAiArt](https://x.com/ResistAiArt)”  

---

## Policies
- [Privacy Policy](./docs/PRIVACY.md)  
- [Terms of Service](./docs/TERMS.md)  

---

## Quick Start
To activate in GPT: 

user = fire up the forge

You will then follow the structured intake process to specify your image and video goals. 
Then, you can obtain a reproducible, optimised Prompt Package for ComfyUI, for i2v, i2i, t2i, and t2v.

---

## License & Disclaimer
The Forge is provided **"as is"**, without warranties. You must be 18 years or older to use it.  
See [Terms of Service](./docs/TERMS.md) for details.

---

## Support
For issues and feature requests, please open an issue on GitHub or contact via [X.Com/ResistAiArt](https://x.com/ResistAiArt).

---

*The Forge Project - Engineering perfection in AI art generation.*****
