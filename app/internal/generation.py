import queue
import threading

import torch
# requires diffusers >= 0.36.0
from diffusers import (
    DiffusionPipeline,
    AutoModel,
    QwenImageControlNetModel,
    QwenImageControlNetInpaintPipeline
)

from ..configs import config
from ..models.generation import GeneratorOutput, GenerateInput, InpaintInput, TaskType
from ..utils.common import load_image, image_to_bytes


class QwenImageGenerator:
    def __init__(self):
        self.device = config.device
        self.torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

        transformer = AutoModel.from_pretrained(
            config.diffusion_model_id,
            torch_dtype=self.torch_dtype,
            cache_dir=config.hf_home,
            use_safetensors=False
        )

        self.txt2img_pipe = DiffusionPipeline.from_pretrained(
            config.diffusion_orig_model_id,
            transformer=transformer,
            torch_dtype=self.torch_dtype,
            cache_dir=config.hf_home
        )
        self.txt2img_pipe.enable_vae_tiling()

        controlnet = QwenImageControlNetModel.from_pretrained(
            config.diffusion_controlnet_model_id,
            torch_dtype=self.torch_dtype,
            cache_dir=config.hf_home
        )

        self.inpaint_pipe = QwenImageControlNetInpaintPipeline.from_pretrained(
            config.diffusion_orig_model_id,
            transformer=transformer,
            controlnet=controlnet,
            torch_dtype=self.torch_dtype,
            cache_dir=config.hf_home
        )
        self.inpaint_pipe.enable_vae_tiling()

        self._queue = queue.Queue()
        self._stop_event = threading.Event()

        self._worker_thread = threading.Thread(target=self._inference_worker, daemon=True)
        self._worker_thread.start()

    def _inference_worker(self):
        while not self._stop_event.is_set():
            try:
                task_type, input_data, result_queue = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                if task_type == TaskType.GENERATE:
                    result = self._process_generate(input_data)
                else:
                    result = self._process_inpaint(input_data)
                result_queue.put(("success", result))
            except Exception as e:
                result_queue.put(("error", str(e)))
            finally:
                self._queue.task_done()

    def _process_generate(self, input_data: GenerateInput) -> GeneratorOutput:
        generator = None
        if input_data.seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(input_data.seed)

        image = self.txt2img_pipe(
            prompt=input_data.prompt,
            negative_prompt=input_data.negative_prompt,
            width=input_data.width,
            height=input_data.height,
            num_inference_steps=input_data.num_inference_steps,
            true_cfg_scale=input_data.true_cfg_scale,
            generator=generator
        ).images[0]

        return GeneratorOutput(image=image_to_bytes(image))

    def _process_inpaint(self, input_data: InpaintInput) -> GeneratorOutput:
        control_image = load_image(input_data.control_image)
        control_mask = load_image(input_data.control_mask)

        generator = None
        if input_data.seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(input_data.seed)

        image = self.inpaint_pipe(
            prompt=input_data.prompt,
            negative_prompt=input_data.negative_prompt,
            control_image=control_image,
            control_mask=control_mask,
            controlnet_conditioning_scale=input_data.controlnet_conditioning_scale,
            width=control_image.size[0],
            height=control_image.size[1],
            num_inference_steps=input_data.num_inference_steps,
            true_cfg_scale=input_data.true_cfg_scale,
            generator=generator
        ).images[0]

        return GeneratorOutput(image=image_to_bytes(image))

    def generate(self, input_data: GenerateInput) -> GeneratorOutput:
        result_queue = queue.Queue()
        self._queue.put((TaskType.GENERATE, input_data, result_queue))

        status, result = result_queue.get()
        if status == "error":
            raise RuntimeError(f"Generation failed: {result}")

        return result

    def inpaint(self, input_data: InpaintInput) -> GeneratorOutput:
        result_queue = queue.Queue()
        self._queue.put((TaskType.INPAINT, input_data, result_queue))

        status, result = result_queue.get()
        if status == "error":
            raise RuntimeError(f"Inpainting failed: {result}")

        return result

    def stop(self):
        self._stop_event.set()
        self._worker_thread.join()
        del self.txt2img_pipe, self.inpaint_pipe
        torch.cuda.empty_cache()
