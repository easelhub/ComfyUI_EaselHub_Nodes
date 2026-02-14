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

from .py.easel_image_comparer import Easel_ImageComparer
from .py.easel_image_tile import Easel_ImageTileBatch, Easel_ImageAssembly
from .py.easel_florence2_tagger import Easel_Florence2Tagger
from .py.easel_image_resize import Easel_ImageResize
from .py.easel_prompt_utils import Easel_PromptProcess
from .py.easel_scheduler import Easel_FlowMatchEulerScheduler
from .py.easel_group_manager import Easel_GroupManager
from .py.easel_seed import Easel_Seed
from .py.easel_color_match import Easel_ColorMatch
from .py.easel_model_bus import Easel_ModelBus

NODE_CLASS_MAPPINGS = {
    "Easel_ImageComparer": Easel_ImageComparer,
    "Easel_ImageTileBatch": Easel_ImageTileBatch,
    "Easel_ImageAssembly": Easel_ImageAssembly,
    "Easel_Florence2Tagger": Easel_Florence2Tagger,
    "Easel_ImageResize": Easel_ImageResize,
    "Easel_PromptProcess": Easel_PromptProcess,
    "Easel_FlowMatchEulerScheduler": Easel_FlowMatchEulerScheduler,
    "Easel_GroupManager": Easel_GroupManager,
    "Easel_Seed": Easel_Seed,
    "Easel_ColorMatch": Easel_ColorMatch,
    "Easel_ModelBus": Easel_ModelBus
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Easel_ImageComparer": "🎨 Easel Image Comparer",
    "Easel_ImageTileBatch": "🎨 Easel Image Tile Batch",
    "Easel_ImageAssembly": "🎨 Easel Image Assembly",
    "Easel_Florence2Tagger": "🎨 Easel Florence2 Tagger",
    "Easel_ImageResize": "🎨 Easel Image Resize",
    "Easel_PromptProcess": "🎨 Easel Prompt Process",
    "Easel_FlowMatchEulerScheduler": "🎨 Easel FlowMatch Euler Scheduler",
    "Easel_GroupManager": "🎨 Easel Group Manager",
    "Easel_Seed": "🎨 Easel Seed",
    "Easel_ColorMatch": "🎨 Easel Color Match",
    "Easel_ModelBus": "🎨 Easel Model Bus"
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
