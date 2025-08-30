# 🛠️ The Forge Project 🛠️

> **Generate optimised, production-ready prompt packages for Stable Diffusion and ComfyUI using custom Forge GPT/API**

## Overview

**The Forge Project** is a powerful backend API service designed to provide customizable, AI-powered content generation capabilities. It supports a variety of goals, including **Text-to-Image** (T2I), **Image-to-Image** (I2I), **Text-to-Video** (T2V), and **Image Upscaling**. Built using **FastAPI**, the service handles requests related to content generation, integrates safety filters, provides detailed diagnostics, and offers a flexible workflow for generating high-quality AI-generated visuals.

## 🧠 Philosophy & Architecture

> *"I am The Forge Project. My mission is simple: I do not render images or videos. I engineer the inputs that ensure rendering succeeds."*

### The Problem 🤔

AI image/video workflows are fragmented across dozens of tools and platforms. Prompts, captions, checkpoints, LoRAs, configs, and workflow graphs are scattered everywhere. This fragmentation wastes creative cycles and kills momentum.

### The Solution: AI Optimised Prompt Packages! ✅

💥**These are synchronised, structured blueprints** that eliminate prompt fragmentation! 

**Each Optimised Prompt Package:** 
- **Ties directly** to exact ComfyUI workflows (text-to-image, text-to-video, image-to-video, etc)
- **Optimises every parameter** - checkpoints, samplers, schedulers, resolutions, LoRAs, seeds
- **Is versioned and documented** for quality, speed, and fidelity
- **Records what changed** and why it changed!
- **Remains auditable, reusable, and scalable**

## ✨ What Does The Forge Do?

The Forge GPT takes your creative ideas and turns them into engineered specifications that Comfyui understand perfectly:

- **🎯 Prompt Optimisation**: Transforms basic prompts into highly detailed, weighted instructions
- **🖼️ Image Analysis**: Provides detailed descriptions and captions for any image
- **⚙️ Smart Settings**: Automatically recommends optimal model settings, samplers, and parameters
- **📦 Resource Management**: Validates and suggests the best models, LoRAs, and checkpoints
- **🛠️ Workflow Integration**: Creates ready-to-use packages for ComfyUI and other AI tools

### Forge Features:
- **Text-to-Image (T2I)**: Generate images based on textual prompts.
- **Image-to-Image (I2I)**: Transform existing images based on new prompts.
- **Text-to-Video (T2V)**: Create videos from textual descriptions.
- **Image Upscaling**: Enhance the resolution of images using AI.
- **Interrogate/Captioning**: Analyse and caption images using advanced AI models.
- **Content Safety Scrubbing**: Ensures content is free from NSFW or disallowed elements.
- **User Profiles**: Personalise content generation settings per user.
- **Comprehensive Diagnostics**: Provides detailed explanations of the chosen settings and alternative options.
- **Integration Support**: Easily integrates with external APIs and services.

**Core Files:**
- **main.py**: The entry point for the FastAPI app. It defines the web server and routes for various functionalities, such as health checks, manifest routes, and sealed/legacy API routes.
- **workflows.py**: Handles the core logic for generating and optimising images/videos based on the user's request.
- **prompts.py**: Builds and cleans prompts, applies custom weights, and analyses the prompt style for optimised content generation.
- **settings.py**: Contains default settings for different goals (e.g., T2I, I2V, etc), with support for customisation based on user profiles.
- **safety.py**: Ensures that the generated content adheres to safety standards by blocking or modifying problematic content (e.g., NSFW, explicit content).
- **resources.py**: Manages resources like models, checkpoints, and datasets, validating them for content generation.
- **captions.py**: Generates captions for the images, allowing the user to provide descriptions in various styles and tones.
- **diagnostics.py**: Provides insights into the performance of different settings, the reasoning behind choices, and alternative configurations for optimisation.
- **integrations.py**: Manages external integrations and adds additional features like interacting with other APIs or services.
- **profiles.py**: Manages user profiles, including their preferences for content generation and adjusts the settings accordingly.

### Configuration:
**The Forge Project allows for deep customisation through user profiles, which store preferences such as:**
- Preferred Sampler
- Seeds
- Resolution
- Aspect Ratio
- Content Preferences
These profiles are stored and used to adapt the settings for each generation request, ensuring personalised output.

### Diagnostics:
**The Forge provides detailed diagnostics explaining optimisation choices, such as:**
- CFG scale (controls creativity vs. prompt adherence)
- Sampler choice (e.g., Euler vs. DPM)
- Resolution (e.g., 832x1216 for general use, or 1024x1024 for upscaling)
- Steps (higher steps = higher quality, but slower generation)
Diagnostics also include alternative options for each setting, helping users understand how to tweak their settings for different outcomes.

### Safety Scrubbing:
**Safety scrubbing ensures that no harmful or disallowed content is used in the prompt.**
The Forge filters out:
- Child-related terms or youth-coded tokens
- Other unwanted keywords, such as abuse or violence

### Integrations:
**The Forge can integrate with various external systems, such as:**
- External APIs: Can connect to platforms like HuggingFace, CivitAI, etc.
- Workflow Patches: Supports ComfyUI patches for user-specific workflows.

### Technical Architecture 🤖
**Built with modern Python tools:**
- **FastAPI** - High-performance web framework
- **Pydantic** - Data validation and serialization
- **Hugging Face Inference** - AI model integration
- **Uvicorn** - Lightning-fast ASGI server

---

### Contributing
I welcome contributions to the Forge Project! 
- If you have any ideas or suggestions for improvement, please don't hesitate to contact me below.

### License

- The Forge Project is open source under the MIT License.

---

## 📞 Contact

- **Contact**: [Resist](https://x.com/ResistAiArt) on 𝕏

## 📜 License & Policies

- **License**: Provided "as is" without warranties
- **Terms**: [Terms of Service](./docs/TERMS.md)
- **Privacy**: [Privacy Policy](./docs/PRIVACY.md)
- **Age Requirement**: Must be 18+ to use

---

**Created with love by [Resist](https://x.com/ResistAiArt)** - Engineering Perfection in AI Art Generation.
