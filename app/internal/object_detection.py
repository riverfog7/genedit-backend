import gc
import queue
import threading

import torch
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
from transformers.image_utils import load_image

from ..configs import config
from ..models.object_detection import DetectorInput, DetectionResult, DetectorOutput
from ..utils.common import load_image as load_pil_image


class GDinoDetector:
    def __init__(self):
        self.model_id = config.gdino_model_id
        self.device = config.device
        self.processor = AutoProcessor.from_pretrained(self.model_id, cache_dir=config.hf_home)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(
            self.model_id,
            cache_dir=config.hf_home
        ).to(self.device)
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

    def _process(self, input_data: DetectorInput) -> DetectorOutput:
        image = load_image(load_pil_image(input_data.image))

        text_labels = [input_data.text]

        inputs = self.processor(images=image, text=text_labels, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        results = self.processor.post_process_grounded_object_detection(
            outputs,
            threshold=input_data.threshold,
            target_sizes=[(image.height, image.width)]
        )

        detections = []
        for result in results:
            detection = DetectionResult(
                boxes=result["boxes"].cpu().tolist(),
                scores=result["scores"].cpu().tolist(),
                labels=result["labels"]
            )
            detections.append(detection)

        if config.cuda_frequent_empty_cache:
            gc.collect()
            torch.cuda.empty_cache()

        return DetectorOutput(detections=detections)

    def detect(self, input_data: DetectorInput) -> DetectorOutput:
        result_queue = queue.Queue()
        self._queue.put((input_data, result_queue))

        status, result = result_queue.get()
        if status == "error":
            raise RuntimeError(f"Detection failed: {result}")

        return result

    def stop(self):
        self._stop_event.set()
        self._worker_thread.join()
        del self.model, self.processor
        torch.cuda.empty_cache()
