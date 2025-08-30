# forge/prompts/config.py

from enum import Enum

class GenerationGoal(Enum):
    T2I = "t2i"
    T2V = "t2v"
    I2I = "i2i"
    I2V = "i2v"
    UPSCALE = "upscale"
    INTERROGATE = "interrogate"

class SamplerType(Enum):
    DPM_PP_2M = "DPM++ 2M Karras"
    EULER_A = "Euler a"
    EULER = "Euler"
    LMS = "LMS"
    DDIM = "DDIM"

CONFIG = {
    "keyword_weights": {
        "cyberpunk": 1.3, "samurai": 1.3, "neon": 1.2, "cinematic": 1.4,
        "ultra-detailed": 1.5, "portrait": 1.3, "landscape": 1.3,
        "masterpiece": 1.6, "best quality": 1.5, "4k": 1.4, "8k": 1.4,
        "photorealistic": 1.4, "hyperrealistic": 1.5, "anime": 1.3,
        "fantasy": 1.3, "scifi": 1.3, "concept art": 1.4
    },
    "negative_prompt": (
        "blurry, low quality, watermark, text, signature, username, artist name, "
        "bad anatomy, extra limbs, fused fingers, distorted hands, deformed face, "
        "poorly drawn hands, poorly drawn face, mutation, mutated, ugly, disfigured, "
        "bad proportions, cloned face, malformed limbs, missing arms, missing legs, "
        "extra arms, extra legs, mutated hands, fused fingers, too many fingers, "
        "long neck, jpeg artifacts, compression artifacts, lowres, error, "
        "extra digit, fewer digits, cropped, worst quality, normal quality"
    ),
    "settings": {
        "t2i": {
            "cfg_scale": 7.5, "steps": 28, "resolution": "832x1216",
            "sampler": SamplerType.DPM_PP_2M.value, "scheduler": "Karras",
            "denoise": 0.4, "batch_size": 1, "clip_skip": 2,
            "preferred_checkpoint": "forge-base-v1.safetensors",
        },
        "t2v": {
            "cfg_scale": 8.5, "steps": 35, "resolution": "768x768",
            "sampler": SamplerType.DPM_PP_2M.value, "scheduler": "Karras",
            "denoise": 0.25, "batch_size": 1, "fps": 24, "clip_skip": 2,
            "preferred_checkpoint": "forge-animate-v1.safetensors",
        },
        "i2i": {
            "cfg_scale": 7.0, "steps": 30, "resolution": "match_input",
            "sampler": SamplerType.DPM_PP_2M.value, "scheduler": "Karras",
            "denoise": 0.65, "batch_size": 1, "clip_skip": 2,
            "preferred_checkpoint": "forge-base-v1.safetensors",
        },
        "i2v": {
            "cfg_scale": 8.0, "steps": 40, "resolution": "768x768",
            "sampler": SamplerType.DPM_PP_2M.value, "scheduler": "Karras",
            "denoise": 0.35, "batch_size": 1, "fps": 20, "clip_skip": 2,
            "preferred_checkpoint": "forge-animate-v1.safetensors",
        },
        "upscale": {
            "cfg_scale": 6.0, "steps": 20, "resolution": "1024x1024",
            "sampler": SamplerType.EULER_A.value, "scheduler": "Simple",
            "denoise": 0.2, "batch_size": 1, "clip_skip": 1,
            "preferred_checkpoint": "forge-upscale-v1.safetensors",
        }
    }
}
