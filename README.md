# The Forge Project 🔨🔥

> **Generate optimised, production-ready prompt packages for Stable Diffusion and ComfyUI**

## Overview

**Forge Service** is a powerful backend API service designed to provide customizable, AI-powered content generation capabilities. It supports a variety of goals, including **Text-to-Image** (T2I), **Image-to-Image** (I2I), **Text-to-Video** (T2V), and **Image Upscaling**. Built using **FastAPI**, the service handles requests related to content generation, integrates safety filters, provides detailed diagnostics, and offers a flexible workflow for generating high-quality AI-generated visuals.

## Features

- **Text-to-Image (T2I)**: Generate images based on textual prompts.
- **Image-to-Image (I2I)**: Transform existing images based on new prompts.
- **Text-to-Video (T2V)**: Create videos from textual descriptions.
- **Image Upscaling**: Enhance the resolution of images using AI.
- **Interrogate/Captioning**: Analyse and caption images using advanced AI models.
- **Content Safety Scrubbing**: Ensures content is free from NSFW or disallowed elements.
- **User Profiles**: Personalise content generation settings per user.
- **Comprehensive Diagnostics**: Provides detailed explanations of the chosen settings and alternative options.
- **Integration Support**: Easily integrates with external APIs and services.

## Key Components

### API Endpoints
- **/v2/optimise**: Optimizes content generation (e.g., T2I, I2I, T2V).
- **/v2/analyse**: Analyzes images and generates captions.
- **/health**: Checks the health status of the service.
- **/version**: Returns the current version of the Forge service.
- **/manifest**: Serves the Forge manifest as raw JSON.

### Core Files
- **main.py**: The entry point for the FastAPI app. It defines the web server and routes for various functionalities, such as health checks, manifest routes, and sealed/legacy API routes.
- **forge/workflows.py**: Handles the core logic for generating and optimising images/videos based on the user's request.
- **forge/prompts.py**: Builds and cleans prompts, applies custom weights, and analyses the prompt style for optimised content generation.
- **forge/settings.py**: Contains default settings for different goals (e.g., T2I, I2V), with support for customisation based on user profiles.
- **forge/safety.py**: Ensures that the generated content adheres to safety standards by blocking or modifying problematic content (e.g., NSFW, explicit content).
- **forge/resources.py**: Manages resources like models, checkpoints, and datasets, validating them for content generation.
- **forge/captions.py**: Generates captions for the images, allowing the user to provide descriptions in various styles and tones.
- **forge/diagnostics.py**: Provides insights into the performance of different settings, the reasoning behind choices, and alternative configurations for optimisation.
- **forge/integrations.py**: Manages external integrations and adds additional features like interacting with other APIs or services.
- **forge/profiles.py**: Manages user profiles, including their preferences for content generation and adjusts the settings accordingly.

##
---

## ✨ What Does The Forge Do?

The Forge GPT takes your creative ideas and turns them into engineered specifications that Comfyui understand perfectly:

- **🎯 Prompt Optimisation**: Transforms basic prompts into highly detailed, weighted instructions
- **🖼️ Image Analysis**: Provides detailed descriptions and captions for any image
- **⚙️ Smart Settings**: Automatically recommends optimal model settings, samplers, and parameters
- **📦 Resource Management**: Validates and suggests the best models, LoRAs, and checkpoints
- **🔧 Workflow Integration**: Creates ready-to-use packages for ComfyUI and other AI tools

---

### Configuration

**Forge Service allows for deep customisation through user profiles, which store preferences such as:**
- Preferred Sampler
- Resolution
- Aspect Ratio
- Content Preferences (e.g., allow NSFW)
**These profiles are stored and used to adapt the settings for each generation request, ensuring personalised output.**

### Diagnostics
**The service provides detailed diagnostics explaining optimisation choices, such as:**
- CFG scale (controls creativity vs. prompt adherence)
- Sampler choice (e.g., Euler vs. DPM)
- Resolution (e.g., 832x1216 for general use, or 1024x1024 for upscaling)
- Steps (higher steps = higher quality, but slower generation)
**Diagnostics also include alternative options for each setting, helping users understand how to tweak their settings for different outcomes.**

### Safety Scrubbing
**Safety scrubbing ensures that no harmful or disallowed content is used in the prompt. The service filters out:**
- NSFW or explicit content
- Child-related terms or youth-coded tokens
- Other unwanted keywords, such as abuse or violence

### Integrations
**The Forge Service can integrate with various external systems, such as:**
- External APIs: Can connect to platforms like HuggingFace, CivitAI, etc.
- Workflow Patches: Supports ComfyUI patches for user-specific workflows.

### Contributing

*I welcome contributions to the Forge Project!*
- If you have any ideas or suggestions for improvement, please don't hesitate to contact me below.

### License

- The Forge Service is open source under the MIT License.

## 🧠 Philosophy & Architecture

> *"I am The Forge Project. My mission is simple: I do not render images or videos. I engineer the inputs that ensure rendering succeeds."*

### The Problem 🤔

AI art workflows are fragmented across dozens of tools and platforms. Prompts, captions, checkpoints, LoRAs, configs, and workflow graphs are scattered everywhere. This fragmentation wastes creative cycles and kills momentum.

### The Solution: AI Optimised Prompt Packages! ✅

**Prompt Packages are synchronised, structured blueprints** that eliminate fragmentation. Each package:**

- **Ties directly** to exact ComfyUI workflows (text-to-image, text-to-video, image-to-video)
- **Optimises every parameter** - checkpoints, samplers, schedulers, resolutions, LoRAs, seeds
- **Is versioned and documented** for quality, speed, and fidelity
- **Records what changed** and why it changed
- **Remains auditable, reusable, and scalable**

### Technical Architecture 🤖

Built with modern Python tools:
- **FastAPI** - High-performance web framework
- **Pydantic** - Data validation and serialization
- **Hugging Face Inference** - AI model integration
- **Uvicorn** - Lightning-fast ASGI server

Key modules include `forge_prompts.py`, `forge_image_analysis.py`, `forge_resources.py`, and `forge_settings.py` - each handling a specific aspect of the package generation process.

---

## 📞 Contact

- **Contact**: [Resist](https://x.com/ResistAiArt) on 𝕏

---

## 📜 License & Policies

- **License**: Provided "as is" without warranties
- **Terms**: [Terms of Service](./docs/TERMS.md)
- **Privacy**: [Privacy Policy](./docs/PRIVACY.md)
- **Age Requirement**: Must be 18+ to use

---

**Created by [Resist](https://x.com/ResistAiArt)** - Engineering Perfection in AI Art Generation.
