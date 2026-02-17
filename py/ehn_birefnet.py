import torch, os, folder_paths
from PIL import Image
from transformers import AutoModelForImageSegmentation
from torchvision import transforms
from huggingface_hub import snapshot_download

class EHN_BiRefNet:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "model": (["BiRefNet", "BiRefNet_HR-matting", "BiRefNet-portrait", "BiRefNet_dynamic"], {"default": "BiRefNet"}),
            }
        }
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "process"
    CATEGORY = "EaselHub/Image"

    def process(self, image, model):
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        repo = {
            "BiRefNet": "ZhengPeng7/BiRefNet",
            "BiRefNet_HR-matting": "ZhengPeng7/BiRefNet_HR-matting",
            "BiRefNet-portrait": "ZhengPeng7/BiRefNet-portrait",
            "BiRefNet_dynamic": "ZhengPeng7/BiRefNet_dynamic"
        }.get(model, "ZhengPeng7/BiRefNet")
        
        mp = os.path.join(folder_paths.models_dir, "LLM", model)
        if not os.path.exists(mp) or not os.listdir(mp):
            snapshot_download(repo_id=repo, local_dir=mp)
            
        try:
            net = AutoModelForImageSegmentation.from_pretrained(mp, trust_remote_code=True)
        except:
            net = AutoModelForImageSegmentation.from_pretrained(repo, trust_remote_code=True)
            
        net.to(dev).eval()
        
        res_img, res_msk = [], []
        tf = transforms.Compose([
            transforms.Resize((1024, 1024)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        for t in image:
            pil = Image.fromarray((t.cpu().numpy() * 255).astype("uint8"))
            w, h = pil.size
            inp = tf(pil).unsqueeze(0).to(dev)
            
            with torch.no_grad():
                pred = net(inp)[-1].sigmoid().cpu().squeeze()
            
            msk_pil = transforms.ToPILImage()(pred).resize((w, h), Image.BILINEAR)
            pil.putalpha(msk_pil)
            
            res_img.append(transforms.ToTensor()(pil).permute(1, 2, 0))
            res_msk.append(transforms.ToTensor()(msk_pil)[0])

        return (torch.stack(res_img), torch.stack(res_msk))
