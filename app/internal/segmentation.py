import io
import queue
import threading

import torch
from PIL import Image
from transformers import Sam2Model, Sam2Processor

from ..configs import config
from ..models.segmentation import SegmenterInput, SegmenterOutput
from ..utils.common import load_image


class Sam2Segmenter:
    def __init__(self):
        self.model_id = config.sam2_model_id
        self.device = config.device
        self.model = Sam2Model.from_pretrained(self.model_id, cache_dir=config.hf_home).to(self.device)
        self.processor = Sam2Processor.from_pretrained(self.model_id, cache_dir=config.hf_home)
        self.model.eval()

        self._queue = queue.Queue()
        self._stop_event = threading.Event()

        self._worker_thread = threading.Thread(target=self._inference_worker, daemon=True)
        self._worker_thread.start()

    def _inference_worker(self):
        while not self._stop_event.is_set():
            try:
                input_data, result_queue = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                result = self._process(input_data)
                result_queue.put(("success", result))
            except Exception as e:
                result_queue.put(("error", str(e)))
            finally:
                self._queue.task_done()

    def _process(self, input_data: SegmenterInput) -> SegmenterOutput:
        image = load_image(input_data.image)

        kwargs = {"images": image, "return_tensors": "pt"}
        if input_data.points and input_data.labels:
            kwargs["input_points"] = [[input_data.points]]
            kwargs["input_labels"] = [[input_data.labels]]
        if input_data.boxes:
            kwargs["input_boxes"] = [[input_data.boxes]]

        inputs = self.processor(**kwargs).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs, multimask_output=False)

        masks = self.processor.post_process_masks(
            outputs.pred_masks.cpu(),
            inputs["original_sizes"]
        )[0]

        scores = outputs.iou_scores.squeeze().cpu().tolist()
        if isinstance(scores, float):
            scores = [scores]

        mask_bytes = []
        for mask in masks:
            mask_array = mask.numpy().squeeze()
            pil_mask = Image.fromarray((mask_array * 255).astype("uint8"))
            buffer = io.BytesIO()
            pil_mask.save(buffer, format="PNG")
            mask_bytes.append(buffer.getvalue())

        return SegmenterOutput(
            masks=mask_bytes,
            scores=scores,
            shape=tuple(masks.shape)
        )

    def segment(self, input_data: SegmenterInput) -> SegmenterOutput:
        result_queue = queue.Queue()
        self._queue.put((input_data, result_queue))

        status, result = result_queue.get()
        if status == "error":
            raise RuntimeError(f"Inference failed: {result}")

        return result

    def stop(self):
        self._stop_event.set()
        self._worker_thread.join()
        del self.model, self.processor
        torch.cuda.empty_cache()
