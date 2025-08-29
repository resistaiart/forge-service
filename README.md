# The Forge Project 🔨🔥

> **Stop guessing your AI art settings. Generate optimized, production-ready prompt packages for Stable Diffusion and ComfyUI.**

The Forge analyzes your goal and crafts a perfect set of instructions—prompts, model settings, negative prompts, and resources—to get the best possible output from your AI image and video generation workflows.

---

## 🚀 Quick Start (60 Seconds)

### For End Users (Using the API)

**1. Analyze an image to get a detailed description:**
```bash
curl -X POST https://your-forge-api.com/analyse \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/your-art.jpg", 
    "mode": "detailed"
  }'
```

**2. Generate an optimized prompt package for AI art:**
```bash
curl -X POST https://your-forge-api.com/optimise \
  -H "Content-Type: application/json" \
  -d '{
    "package_goal": "t2i",
    "prompt": "cyberpunk samurai in neon-lit Tokyo streets",
    "resources": ["cyberpunk_lora.safetensors"]
  }'
```

### For ChatGPT Users

Simply say: **"Fire up the forge"** to start creating optimized prompt packages through conversation.

---

## ✨ What Does The Forge Do?

The Forge takes your creative ideas and turns them into engineered specifications that AI systems understand perfectly:

- **🎯 Prompt Optimization**: Transforms basic prompts into highly detailed, weighted instructions
- **🖼️ Image Analysis**: Provides detailed descriptions and captions for any image
- **⚙️ Smart Settings**: Automatically recommends optimal model settings, samplers, and parameters
- **📦 Resource Management**: Validates and suggests the best models, LoRAs, and checkpoints
- **🔧 Workflow Integration**: Creates ready-to-use packages for ComfyUI and other AI tools

---

## 📖 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/optimise` | Create optimized prompt packages |
| `POST` | `/analyse` | Analyze images and generate descriptions |
| `GET`  | `/health` | Check API status |

### Example Package Output

```json
{
  "goal": "t2i",
  "positive_prompt": "((cyberpunk:1.4)) ((samurai:1.3)) warrior in ((neon:1.3))-lit Tokyo streets at night, cinematic masterpiece",
  "negative_prompt": "blurry, low quality, watermark, bad anatomy, deformed",
  "settings": {
    "checkpoint": "forge-base-v1.safetensors",
    "sampler": "DPM++ 2M Karras",
    "steps": 28,
    "cfg_scale": 8.0,
    "resolution": "832x1216"
  },
  "resources": ["cyberpunk_lora.safetensors"],
  "diagnostics": {
    "cfg_reason": "CFG 8.0 optimized for cyberpunk style",
    "detected_style": "cyberpunk"
  }
}
```

---

## 🛠️ Installation & Deployment

### Prerequisites
- Python 3.8+
- Hugging Face API token

### Local Development

1. **Clone and install:**
```bash
git clone https://github.com/yourusername/forge-service.git
cd forge-service
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export HF_TOKEN=your_hugging_face_token_here
export DEBUG=True
```

3. **Run the server:**
```bash
uvicorn main:app --host=0.0.0.0 --port=8000 --reload
```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in the dashboard
3. Deploy automatically from main branch

### Docker Deployment

```bash
docker build -t forge-service .
docker run -p 8000:8000 -e HF_TOKEN=your_token forge-service
```

---

## 🧠 Philosophy & Architecture

> *"I am The Forge Project. My mission is simple: I do not render images or videos. I engineer the inputs that ensure rendering succeeds."*

### The Problem

AI art workflows are fragmented across dozens of tools and platforms. Prompts, captions, checkpoints, LoRAs, configs, and workflow graphs are scattered everywhere. This fragmentation wastes creative cycles and kills momentum.

### The Solution: Prompt Packages

**Prompt Packages are synchronized, structured blueprints** that eliminate fragmentation. Each package:

- **Ties directly** to exact ComfyUI workflows (text-to-image, text-to-video, image-to-video)
- **Optimizes every parameter** - checkpoints, samplers, schedulers, resolutions, LoRAs, seeds
- **Is versioned and documented** for quality, speed, and fidelity
- **Records what changed** and why it changed
- **Remains auditable, reusable, and scalable**

### Technical Architecture

Built with modern Python tools:
- **FastAPI** - High-performance web framework
- **Pydantic** - Data validation and serialization
- **Hugging Face Inference** - AI model integration
- **Uvicorn** - Lightning-fast ASGI server

Key modules include `forge_prompts.py`, `forge_image_analysis.py`, `forge_resources.py`, and `forge_settings.py` - each handling a specific aspect of the package generation process.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/forge-service/issues)
- **Contact**: [@ResistAiArt on X](https://x.com/ResistAiArt)
- **Documentation**: See `/docs` directory for detailed guides

---

## 📜 License & Policies

- **License**: Provided "as is" without warranties
- **Terms**: [Terms of Service](./docs/TERMS.md)
- **Privacy**: [Privacy Policy](./docs/PRIVACY.md)
- **Age Requirement**: Must be 18+ to use

---

**Created by [Resist](https://x.com/ResistAiArt)** - Engineering perfection in AI art generation.
