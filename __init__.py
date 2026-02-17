import sys, subprocess, importlib.metadata
from pathlib import Path
try:
    reqs = Path(__file__).parent / "requirements.txt"
    if reqs.is_file():
        missing = []
        with open(reqs) as f:
            for line in f:
                if not line.strip(): continue
                pkg = line.split("=")[0].split(">")[0].split("<")[0].strip()
                try: importlib.metadata.version(pkg)
                except importlib.metadata.PackageNotFoundError: missing.append(line.strip())
        if missing: subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
except: pass

from .py.ehn_image_comparer import EHN_ImageComparer
from .py.ehn_image_tile import EHN_ImageTileBatch, EHN_ImageAssembly
from .py.ehn_florence2_tagger import EHN_Florence2Tagger
from .py.ehn_image_resize import EHN_ImageResize
from .py.ehn_prompt_utils import EHN_PromptProcess
from .py.ehn_scheduler import EHN_FlowMatchEulerScheduler
from .py.ehn_group_manager import EHN_GroupManager
from .py.ehn_seed import EHN_Seed
from .py.ehn_color_match import EHN_ColorMatch
from .py.ehn_model_bus import EHN_ModelBus
from .py.ehn_birefnet import EHN_BiRefNet

NODE_CLASS_MAPPINGS = {
    "EHN_ImageComparer": EHN_ImageComparer,
    "EHN_ImageTileBatch": EHN_ImageTileBatch,
    "EHN_ImageAssembly": EHN_ImageAssembly,
    "EHN_Florence2Tagger": EHN_Florence2Tagger,
    "EHN_ImageResize": EHN_ImageResize,
    "EHN_PromptProcess": EHN_PromptProcess,
    "EHN_FlowMatchEulerScheduler": EHN_FlowMatchEulerScheduler,
    "EHN_GroupManager": EHN_GroupManager,
    "EHN_Seed": EHN_Seed,
    "EHN_ColorMatch": EHN_ColorMatch,
    "EHN_ModelBus": EHN_ModelBus,
    "EHN_BiRefNet": EHN_BiRefNet
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EHN_ImageComparer": "🖼️ EHN Image Split View",
    "EHN_ImageTileBatch": "🧩 EHN Image Tile",
    "EHN_ImageAssembly": "🧩 EHN Image Assembly",
    "EHN_Florence2Tagger": "🏷️ EHN Florence2 Tagger",
    "EHN_ImageResize": "📏 EHN Image Resize",
    "EHN_PromptProcess": "📝 EHN Prompt Process",
    "EHN_FlowMatchEulerScheduler": "📅 EHN FlowMatch Scheduler",
    "EHN_GroupManager": "🔇 EHN Group Toggle",
    "EHN_Seed": "🌱 EHN Global Seed",
    "EHN_ColorMatch": "🎨 EHN Color Transfer",
    "EHN_ModelBus": "🚌 EHN Model Bus",
    "EHN_BiRefNet": "✂️ EHN BiRefNet Rembg"
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
