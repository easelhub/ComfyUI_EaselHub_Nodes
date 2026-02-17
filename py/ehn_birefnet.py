import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForImageSegmentation
import os
import folder_paths
from huggingface_hub import snapshot_download

class EHN_BiRefNet:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "model_name": (["BiRefNet", "BiRefNet_HR-matting", "BiRefNet-portrait", "BiRefNet_dynamic"],),
                "background_color": (["None", "White", "Black", "Green", "Blue", "Red"], {"default": "None"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "process"
    CATEGORY = "EaselHub/Image"

    def process(self, image, model_name, background_color):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model_map = {
            "BiRefNet": "ZhengPeng7/BiRefNet",
            "BiRefNet_HR-matting": "ZhengPeng7/BiRefNet_HR-matting",
            "BiRefNet-portrait": "ZhengPeng7/BiRefNet-portrait",
            "BiRefNet_dynamic": "ZhengPeng7/BiRefNet_dynamic"
        }
        
        hf_repo_id = model_map.get(model_name, "ZhengPeng7/BiRefNet")
        birefnet_models_dir = os.path.join(folder_paths.models_dir, "BiRefNet")
        local_model_path = os.path.join(birefnet_models_dir, model_name)
        
        if not os.path.exists(local_model_path):
            os.makedirs(local_model_path, exist_ok=True)
            snapshot_download(repo_id=hf_repo_id, local_dir=local_model_path)
        
        try:
            birefnet = AutoModelForImageSegmentation.from_pretrained(local_model_path, trust_remote_code=True)
        except:
            birefnet = AutoModelForImageSegmentation.from_pretrained(hf_repo_id, trust_remote_code=True)

        birefnet.to(device)
        birefnet.eval()

        processed_images = []
        processed_masks = []
        
        transform_image = transforms.Compose([
            transforms.Resize((1024, 1024)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        for i in range(image.shape[0]):
            img = image[i]
            pil_image = Image.fromarray((img.cpu().numpy() * 255).astype("uint8"))
            original_size = pil_image.size

            input_images = transform_image(pil_image).unsqueeze(0).to(device)

            with torch.no_grad():
                preds = birefnet(input_images)[-1].sigmoid().cpu()

            pred = preds[0].squeeze()
            pred_pil = transforms.ToPILImage()(pred)
            mask_pil = pred_pil.resize(original_size, Image.BILINEAR)
            mask_tensor = transforms.ToTensor()(mask_pil)[0] # 1, H, W
            
            processed_masks.append(mask_tensor)

            if background_color != "None":
                bg_color_map = {
                    "White": (255, 255, 255),
                    "Black": (0, 0, 0),
                    "Green": (0, 255, 0),
                    "Blue": (0, 0, 255),
                    "Red": (255, 0, 0)
                }
                bg_color = bg_color_map.get(background_color, (255, 255, 255))
                background = Image.new("RGB", original_size, bg_color)
                # Paste original image onto background using the mask
                background.paste(pil_image, (0, 0), mask_pil)
                final_tensor = transforms.ToTensor()(background).permute(1, 2, 0) # H, W, 3
            else:
                # Add alpha channel
                pil_image.putalpha(mask_pil)
                final_tensor = transforms.ToTensor()(pil_image).permute(1, 2, 0) # H, W, 4
            
            processed_images.append(final_tensor)

        return (torch.stack(processed_images), torch.stack(processed_masks))
