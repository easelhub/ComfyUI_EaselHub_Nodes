import os, torch, folder_paths
import comfy.model_management as mm
from PIL import Image
import numpy as np
import cv2

class EHN_BiRefNet:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Segmentation", ("IMAGE", "MASK"), ("image", "mask"), "segment"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "image": ("IMAGE",),
            "model": ([
                "BiRefNet", 
                "BiRefNet-matting", 
                "BiRefNet-portrait", 
                "BiRefNet_lite", 
                "BiRefNet_lite-2K"
            ], {"default": "BiRefNet"}),
        }}

    def segment(self, image, model):
        from transformers import AutoModelForImageSegmentation
        from torchvision import transforms
        
        dev = mm.get_torch_device()
        
        # Mapping model names to (ModelScope ID, HuggingFace ID)
        model_map = {
            "BiRefNet": ("freepik/BiRefNet", "ZhengPeng7/BiRefNet"),
            "BiRefNet-matting": ("freepik/BiRefNet-matting", "ZhengPeng7/BiRefNet-matting"),
            "BiRefNet-portrait": ("freepik/BiRefNet-portrait", "ZhengPeng7/BiRefNet-portrait"),
            "BiRefNet_lite": ("freepik/BiRefNet_lite", "ZhengPeng7/BiRefNet_lite"),
            "BiRefNet_lite-2K": ("freepik/BiRefNet_lite-2K", "ZhengPeng7/BiRefNet_lite-2K"),
        }
        
        ms_id, hf_id = model_map.get(model, ("freepik/BiRefNet", "ZhengPeng7/BiRefNet"))
        mp = os.path.join(folder_paths.models_dir, "BiRefNet", model)
        
        if not os.path.exists(mp) or not os.listdir(mp):
            try:
                from modelscope.hub.snapshot_download import snapshot_download
                print(f"Downloading {model} from ModelScope...")
                snapshot_download(ms_id, local_dir=mp)
            except Exception as e:
                print(f"ModelScope download failed: {e}. Trying HuggingFace...")
                from huggingface_hub import snapshot_download
                snapshot_download(repo_id=hf_id, local_dir=mp)
            
        try:
            m = AutoModelForImageSegmentation.from_pretrained(mp, trust_remote_code=True)
        except:
            # Fallback to loading from cache if local dir fails structurally
            m = AutoModelForImageSegmentation.from_pretrained(hf_id, trust_remote_code=True)
            
        m.to(dev).eval()
        
        transform_image = transforms.Compose([
            transforms.Resize((1024, 1024)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        res_imgs, res_masks = [], []
        
        for img_tensor in image:
            org_w, org_h = img_tensor.shape[1], img_tensor.shape[0]
            pil_img = Image.fromarray((img_tensor.cpu().numpy() * 255).astype('uint8')).convert("RGB")
            
            input_images = transform_image(pil_img).unsqueeze(0).to(dev)
            
            with torch.no_grad():
                preds = m(input_images)[-1].sigmoid().cpu()
                
            pred = preds[0].squeeze()
            pred_pil = transforms.ToPILImage()(pred).resize((org_w, org_h), Image.BILINEAR)
            mask = np.array(pred_pil).astype(np.float32) / 255.0
            
            masked_img = img_tensor.cpu().numpy().copy()
            masked_img[:, :, 0] *= mask
            masked_img[:, :, 1] *= mask
            masked_img[:, :, 2] *= mask
            
            alpha = torch.from_numpy(mask).unsqueeze(-1)
            rgba_img = torch.cat([torch.from_numpy(masked_img), alpha], dim=-1)
            
            res_imgs.append(rgba_img)
            res_masks.append(torch.from_numpy(mask))
            
        return (torch.stack(res_imgs), torch.stack(res_masks))

