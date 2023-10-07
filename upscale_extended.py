from PIL import Image
import numpy as np

from modules import scripts_postprocessing, shared

import modules.scripts as scripts
import gradio as gr
import os

from modules import script_callbacks
from modules.ui_components import FormRow, ToolButton
from modules.ui import switch_values_symbol

upscale_cache = {}

def resize(img, enable_1 = True, upscaler_1 = None, resize_1 = 1.0, enable_2 = False, upscaler_2 = None, resize_2 = 1.0, enable_3 = False, upscaler_3 = None, resize_3 = 1.0, enable_4 = False, upscaler_4 = None, resize_4 = 1.0):

    #s_1_out = img
    #s_2_out = img
    #s_3_out = img
    #s_4_out = img
    
    if upscaler_1 is not None and enable_1 == True:
        scaler_1 = next(iter([x for x in shared.sd_upscalers if x.name == upscaler_1]), None)
        assert scaler_1 or (scaler_1 is None), f'could not find upscaler named {upscaler_1}'
        s_1_out = scaler_1.scaler.upscale(img, resize_1, scaler_1.data_path)
    else:
        s_1_out = img
    
    if upscaler_2 is not None and enable_2 == True:
        scaler_2 = next(iter([x for x in shared.sd_upscalers if x.name == upscaler_2]), None)
        assert scaler_2 or (scaler_2 is None), f'could not find upscaler named {upscaler_2}'
        s_2_out = scaler_2.scaler.upscale(s_1_out, resize_2, scaler_2.data_path)
    else:
        s_2_out = s_1_out
        
    if upscaler_3 is not None and enable_3 == True:
        scaler_3 = next(iter([x for x in shared.sd_upscalers if x.name == upscaler_3]), None)
        assert scaler_3 or (scaler_3 is None), f'could not find upscaler named {upscaler_3}'
        s_3_out = scaler_3.scaler.upscale(s_2_out, resize_3, scaler_3.data_path)
    else:
        s_3_out = s_2_out

    if upscaler_4 is not None and enable_4 == True:
        scaler_4 = next(iter([x for x in shared.sd_upscalers if x.name == upscaler_4]), None)
        assert scaler_4 or (scaler_4 is None), f'could not find upscaler named {upscaler_4}'
        s_4_out = scaler_4.scaler.upscale(s_3_out, resize_4, scaler_4.data_path)
    else:
        s_4_out = s_3_out
    
    return s_4_out

def flip(img):
    img = np.fliplr(img)
    return img

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            with gr.Column(variant='panel1', scale=2):
                in_image = gr.Image(elem_id="pnginfo_image", label="Source", source="upload", interactive=True, height=500, type="pil")

                with gr.Accordion("Upscaler 1", open=True):
                    with gr.Row(equal_heigh=True):
                        ext_upscaler_1_enable = gr.Checkbox(label='Enable', value=True, elem_id="upscaler_1_enable", scale=1)
                        ext_upscaler_1 = gr.Dropdown(label='Upscaler', scale=2, elem_id="extras_upscaler_1", interactive=True, choices=[x.name for x in shared.sd_upscalers], value=shared.sd_upscalers[0].name)
                        ext_upscaler_1_resize = gr.Slider(minimum=0.25, maximum=8.0, step=0.1, label="Resize", value=4, elem_id="upscaler_1_resize", scale=2, container=True)

                with gr.Accordion("Upscaler 2", open=False):
                    with gr.Row(equal_heigh=True):
                        ext_upscaler_2_enable = gr.Checkbox(label='Enable', value=False, elem_id="upscaler_2_enable", scale=1)
                        ext_upscaler_2 = gr.Dropdown(label='Upscaler', scale=2, elem_id="extras_upscaler_2", interactive=True, choices=[x.name for x in shared.sd_upscalers], value=shared.sd_upscalers[0].name)
                        ext_upscaler_2_resize = gr.Slider(minimum=0.25, maximum=8.0, step=0.25, label="Resize", value=1.0, elem_id="upscaler_2_resize", scale=2)
                        
                with gr.Accordion("Upscaler 3", open=False):
                    with gr.Row(equal_heigh=True):
                        ext_upscaler_3_enable = gr.Checkbox(label='Enable', value=False, elem_id="upscaler_3_enable", scale=1)
                        ext_upscaler_3 = gr.Dropdown(label='Upscaler', scale=2, elem_id="extras_upscaler_3", interactive=True, choices=[x.name for x in shared.sd_upscalers], value=shared.sd_upscalers[0].name)
                        ext_upscaler_3_resize = gr.Slider(minimum=0.25, maximum=8.0, step=0.25, label="Resize", value=1.0, elem_id="upscaler_3_resize", scale=2)

                with gr.Accordion("Upscaler 4", open=False):
                    with gr.Row(equal_heigh=True):
                        ext_upscaler_4_enable = gr.Checkbox(label='Enable', value=False, elem_id="upscaler_4_enable", scale=1)
                        ext_upscaler_4 = gr.Dropdown(label='Upscaler', scale=2, elem_id="extras_upscaler_4", interactive=True, choices=[x.name for x in shared.sd_upscalers], value=shared.sd_upscalers[0].name)
                        ext_upscaler_4_resize = gr.Slider(minimum=0.25, maximum=8.0, step=0.25, label="Resize", value=1.0, elem_id="upscaler_1_resize", scale=2)

                ext_btn = gr.Button(label="Generate", elem_id="genbutton")
                
            with gr.Column(variant='panel2', scale=1):
                out_image = gr.Image(elem_id="out_image", label="Result", height=700, interactive=False, type="pil")


                ext_btn.click(resize, inputs=[in_image, ext_upscaler_1_enable, ext_upscaler_1, ext_upscaler_1_resize, ext_upscaler_2_enable, ext_upscaler_2, ext_upscaler_2_resize, ext_upscaler_3_enable, ext_upscaler_3, ext_upscaler_3_resize, ext_upscaler_4_enable, ext_upscaler_4, ext_upscaler_4_resize], outputs=[out_image])

                return [(ui_component, "Upscale Extended", "upscale_extended_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)


