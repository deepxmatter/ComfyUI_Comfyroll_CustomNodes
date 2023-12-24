#---------------------------------------------------------------------------------------------------------------------#
# Comfyroll Custom Nodes by RockOfFire and Akatsuzi       https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes
# for ComfyUI                                             https://github.com/comfyanonymous/ComfyUI
#---------------------------------------------------------------------------------------------------------------------#

import torch
import numpy as np
import os
import sys
import folder_paths
import re
import comfy.sd
from PIL import Image
from pathlib import Path
from ..categories import icons

def tensor2pil(image):
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0) 

def tensor2rgba(t: torch.Tensor) -> torch.Tensor:
    size = t.size()
    if (len(size) < 4):
        return t.unsqueeze(3).repeat(1, 1, 1, 4)
    elif size[3] == 1:
        return t.repeat(1, 1, 1, 4)
    elif size[3] == 3:
        alpha_tensor = torch.ones((size[0], size[1], size[2], 1))
        return torch.cat((t, alpha_tensor), dim=3)
    else:
        return t

#---------------------------------------------------------------------------------------------------------------------#
# List Nodes                
#---------------------------------------------------------------------------------------------------------------------#
class AnyType(str):
    """A special type that can be connected to any other types. Credit to pythongosssss"""

    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")

#---------------------------------------------------------------------------------------------------------------------#
class CR_FontFileList:

    @classmethod
    def INPUT_TYPES(s):
    
        comfyroll_font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "fonts")       
        comfyroll_file_list = [f for f in os.listdir(comfyroll_font_dir) if os.path.isfile(os.path.join(comfyroll_font_dir, f)) and f.lower().endswith(".ttf")]

        sources = ["system", "Comfyroll", "from folder"]
        
        return {"required": {"source_folder": (sources,),
                             "start_index": ("INT", {"default": 0, "min": 0, "max": 9999}),
                             "max_rows": ("INT", {"default": 1000, "min": 1, "max": 9999}),                            
                            },
                "optional": {"folder_path": ("STRING", {"default": "C:\Windows\Fonts", "multiline": False}),
                }
        }

    RETURN_TYPES = (any_type, "STRING", )
    RETURN_NAMES = ("LIST", "show_help", )
    OUTPUT_IS_LIST = (True, False)
    FUNCTION = "make_list"
    CATEGORY = icons.get("Comfyroll/List")

    def make_list(self, source_folder, start_index, max_rows, folder_path="C:\Windows\Fonts"):

        if source_folder == "system":
            system_root = os.environ.get('SystemRoot')
            system_font_dir = os.path.join(system_root, 'Fonts')   
            file_list = [f for f in os.listdir(system_font_dir) if os.path.isfile(os.path.join(system_font_dir, f)) and f.lower().endswith(".ttf")]
        elif source_folder == "Comfyroll":
            comfyroll_font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "fonts")       
            file_list = [f for f in os.listdir(comfyroll_font_dir) if os.path.isfile(os.path.join(comfyroll_font_dir, f)) and f.lower().endswith(".ttf")]
        elif source_folder == "from folder":
            if folder_path != '' and folder_path is not None:
                if not os.path.exists(folder_path):
                    print(f"[Warning] CR Font File List: The folder_path `{folder_path}` does not exist")
                    return None
                font_dir = folder_path     
                file_list = [f for f in os.listdir(font_dir) if os.path.isfile(os.path.join(font_dir, f)) and f.lower().endswith(".ttf")]
            else:    
                print(f"[Warning] CR Font File List: No folder_path entered")
                return None                
        else:
            pass
        # Ensure start_index is within the bounds of the list
        start_index = max(0, min(start_index, len(file_list) - 1))

        # Calculate the end index based on max_rows
        end_index = min(start_index + max_rows, len(file_list))

        # Extract the desired portion of the list
        selected_files = file_list[start_index:end_index]

        show_help = "https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes/wiki/Other-Nodes#cr-font-file-list"

        return (selected_files, show_help, )

#---------------------------------------------------------------------------------------------------------------------#
class CR_TextList:

    @classmethod
    def INPUT_TYPES(s):
    
        return {"required": {"multiline_text": ("STRING", {"multiline": False, "default": "text"}),
                             "start_index": ("INT", {"default": 0, "min": 0, "max": 9999}),
                             "max_rows": ("INT", {"default": 1000, "min": 1, "max": 9999}),
                            }
        }

    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("STRING", "show_help", )
    OUTPUT_IS_LIST = (True, False)
    FUNCTION = "make_list"
    CATEGORY = icons.get("Comfyroll/List")

    def make_list(self, multiline_text, start_index, max_rows):

        lines = multiline_text.split('\n')

        # Ensure start_index is within the bounds of the list
        start_index = max(0, min(start_index, len(lines) - 1))

        # Calculate the end index based on max_rows
        end_index = min(start_index + max_rows, len(lines))

        # Extract the desired portion of the list
        selected_rows = lines[start_index:end_index]

        show_help = "https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes/wiki/Other-Nodes#cr-text-list"

        return (selected_rows, show_help, )

#---------------------------------------------------------------------------------------------------------------------#
class CR_LoadImageList:

    @classmethod
    def INPUT_TYPES(s):
    
        input_dir = folder_paths.input_directory
        image_folder = [name for name in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir,name))] 
    
        return {"required": {"input_folder": (sorted(image_folder), ),
                             "start_index": ("INT", {"default": 0, "min": 0, "max": 9999}),
                             "max_images": ("INT", {"default": 1, "min": 1, "max": 9999}),
               },
               "optional": {"input_path": ("STRING", {"default": '', "multiline": False}),     
               }
        }

    RETURN_TYPES = ("IMAGE", "STRING", )
    RETURN_NAMES = ("IMAGE", "show_help", )
    OUTPUT_IS_LIST = (True, False)
    FUNCTION = "make_list"
    CATEGORY = icons.get("Comfyroll/List")

    def make_list(self, start_index, max_images, input_folder, input_path=None):

        # Set the input path
        if input_path != '' and input_path is not None:
            if not os.path.exists(input_path):
                print(f"[Warning] CR Image List: The input_path `{input_path}` does not exist")
                return ("",)  
            in_path = input_path
        else:
            input_dir = folder_paths.input_directory
            in_path = os.path.join(input_dir, input_folder)

        # Check if the folder is empty
        if not os.listdir(in_path):
            print(f"[Warning] CR Image List: The folder `{in_path}` is empty")
            return None

        file_list = sorted(os.listdir(in_path), key=lambda s: sum(((s, int(n)) for s, n in re.findall(r'(\D+)(\d+)', 'a%s0' % s)), ()))
        
        image_list = []
        
        # Ensure start_index is within the bounds of the list
        start_index = max(0, min(start_index, len(file_list) - 1))

        # Calculate the end index based on max_rows
        end_index = min(start_index + max_images, len(file_list) - 1)
                    
        for num in range(start_index, end_index):
            img = Image.open(os.path.join(in_path, file_list[num]))
            image = img.convert("RGB")
            image_list.append(pil2tensor(image))
        
        if not image_list:
            # Handle the case where the list is empty
            print("CR Load Image List: No images found.")
            return None
            
        images = torch.cat(image_list, dim=0)
        images_out = [images[i:i + 1, ...] for i in range(images.shape[0])]

        show_help = "https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes/wiki/Other-Nodes#cr-image-list"

        return (images_out, show_help, )

#---------------------------------------------------------------------------------------------------------------------#
class CR_LoadImageListPlus:

    @classmethod
    def INPUT_TYPES(s):
    
        input_dir = folder_paths.input_directory
        image_folder = [name for name in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir,name))] 
    
        return {"required": {"input_folder": (sorted(image_folder), ),
                             "start_index": ("INT", {"default": 0, "min": 0, "max": 9999}),
                             "max_images": ("INT", {"default": 1, "min": 1, "max": 9999}),
               },
               "optional": {"input_path": ("STRING", {"default": '', "multiline": False}),     
               }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "STRING", "INT", "INT", "INT", "STRING", )
    RETURN_NAMES = ("IMAGE", "MASK", "index", "filename", "width", "height", "list_length", "show_help", )
    OUTPUT_IS_LIST = (True, True, True, True, False, False, False, False)
    FUNCTION = "make_list"
    CATEGORY = icons.get("Comfyroll/List")

    def make_list(self, start_index, max_images, input_folder, input_path=None, vae=None):

        # Set the input path
        if input_path != '' and input_path is not None:
            if not os.path.exists(input_path):
                print(f"[Warning] CR Image List: The input_path `{input_path}` does not exist")
                return ("",)  
            in_path = input_path
        else:
            input_dir = folder_paths.input_directory
            in_path = os.path.join(input_dir, input_folder)

        # Check if the folder is empty
        if not os.listdir(in_path):
            print(f"[Warning] CR Image List: The folder `{in_path}` is empty")
            return None

        file_list = sorted(os.listdir(in_path), key=lambda s: sum(((s, int(n)) for s, n in re.findall(r'(\D+)(\d+)', 'a%s0' % s)), ()))
        
        image_list = []
        mask_list = []
        index_list = []        
        filename_list = []
        exif_list = []         
        
        # Ensure start_index is within the bounds of the list
        start_index = max(0, min(start_index, len(file_list) - 1))

        # Calculate the end index based on max_rows
        end_index = min(start_index + max_images, len(file_list) - 1)
                    
        for num in range(start_index, end_index):
            filename = file_list[num]
            img_path = os.path.join(in_path, filename)
            
            img = Image.open(os.path.join(in_path, file_list[num]))            
            tensor_img = pil2tensor(img)
            image_list.append(pil2tensor(img.convert("RGB")))
            mask_list.append(tensor2rgba(tensor_img)[:,:,:,0])
           
            # Populate the image index
            index_list.append(num)

            # Populate the filename_list
            filename_list.append(filename)
            
        if not image_list:
            # Handle the case where the list is empty
            print("CR Load Image List: No images found.")
            return None

        width, height = Image.open(os.path.join(in_path, file_list[start_index])).size
            
        images = torch.cat(image_list, dim=0)
        images_out = [images[i:i + 1, ...] for i in range(images.shape[0])]

        masks = torch.cat(mask_list, dim=0)
        mask_out = [masks[i:i + 1, ...] for i in range(masks.shape[0])]
        
        list_length = end_index - start_index
        
        show_help = "https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes/wiki/Other-Nodes#cr-image-list"

        return (images_out, mask_out, index_list, filename_list, index_list, width, height, list_length, show_help, )

#---------------------------------------------------------------------------------------------------------------------#
# MAPPINGS
#---------------------------------------------------------------------------------------------------------------------#
# For reference only, actual mappings are in __init__.py
'''
NODE_CLASS_MAPPINGS = {
    ### List nodes
    "CR Font File List": CR_FontFileList,  
    "CR Text List": CR_TextList, 
    "CR Load Image List": CR_LoadImageList,
    "CR Load Image List Plus": CR_LoadImageListPlus,
}
'''

