import argparse
import json
import os
from pathlib import Path

MODEL_ID = "animeshakr/plant-disease-efficientnetv2s"
MODEL_FILENAME = "model_float16_quant.tflite"
LABELS_FILENAME = "class_indices.json"


class ModelLoadError(RuntimeError):
    pass


def _resolve_asset(filename: str, environment_variable: str) -> Path:
    configured_path = os.environ.get(environment_variable)
    if configured_path:
        path = Path(configured_path).expanduser().resolve()
        if not path.is_file() or path.stat().st_size == 0:
            raise ModelLoadError(
                f"{environment_variable} does not point to a non-empty file: {path}"
            )
        return path

    try:
        from huggingface_hub import hf_hub_download
        from huggingface_hub.errors import EntryNotFoundError, HfHubHTTPError, LocalEntryNotFoundError
    except ImportError as exc:
        raise ModelLoadError(
            "huggingface_hub is required. Install workspace-ml/requirements.in."
        ) from exc

    try:
        path = Path(
            hf_hub_download(
                repo_id=MODEL_ID,
                filename=filename,
                local_files_only=True,
            )
        )
    except (EntryNotFoundError, HfHubHTTPError, LocalEntryNotFoundError, OSError) as exc:
        raise ModelLoadError(
            f"{filename} is not available in the local Hugging Face cache. "
            f"Set {environment_variable} to an existing file; no model is downloaded."
        ) from exc

    if not path.is_file() or path.stat().st_size == 0:
        raise ModelLoadError(f"Cached model asset is missing or empty: {path}")
    return path


def load_model():
    model_path = _resolve_asset(MODEL_FILENAME, "KISANSETU_TFLITE_MODEL_PATH")
    labels_path = _resolve_asset(LABELS_FILENAME, "KISANSETU_TFLITE_LABELS_PATH")

    try:
        import numpy as np
        import tensorflow as tf
    except ImportError as exc:
        raise ModelLoadError(
            "TensorFlow CPU and NumPy are required. Install workspace-ml/requirements.in."
        ) from exc

    try:
        with labels_path.open("r", encoding="utf-8") as file:
            labels = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelLoadError(f"Could not read disease labels from {labels_path}: {exc}") from exc

    if not isinstance(labels, dict) or not labels:
        raise ModelLoadError(f"Disease labels must be a non-empty JSON object: {labels_path}")
    try:
        ordered_labels = [labels[str(index)] for index in range(len(labels))]
    except KeyError as exc:
        raise ModelLoadError(
            f"Disease labels must have contiguous numeric keys starting at 0: {labels_path}"
        ) from exc
    if any(not isinstance(label, str) or not label.strip() for label in ordered_labels):
        raise ModelLoadError(f"Disease labels must all be non-empty strings: {labels_path}")

    try:
        interpreter = tf.lite.Interpreter(model_path=str(model_path))
        interpreter.allocate_tensors()
    except (OSError, ValueError, RuntimeError) as exc:
        raise ModelLoadError(f"Could not load TFLite model at {model_path}: {exc}") from exc

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    if len(input_details) != 1 or len(output_details) != 1:
        raise ModelLoadError("Expected the disease model to have one input tensor and one output tensor.")

    input_shape = input_details[0]["shape"]
    output_shape = output_details[0]["shape"]
    if (
        len(input_shape) != 4
        or tuple(input_shape[1:]) != (384, 384, 3)
        or input_details[0]["dtype"] != np.float32
    ):
        raise ModelLoadError(
            "Unexpected model input; expected float32 RGB tensors shaped [1, 384, 384, 3]."
        )
    if len(output_shape) != 2 or int(output_shape[-1]) != len(ordered_labels):
        raise ModelLoadError(
            f"Model output shape {list(output_shape)} does not match "
            f"{len(ordered_labels)} disease labels."
        )
    if output_details[0]["dtype"] != np.float32:
        raise ModelLoadError("Unexpected model output dtype; expected float32 scores.")

    return interpreter, ordered_labels


def predict_image(image, interpreter, labels, top_k: int = 3):
    import numpy as np

    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]
    height = int(input_details["shape"][1])
    width = int(input_details["shape"][2])

    resized_image = image.convert("RGB").resize((width, height))
    image_array = np.asarray(resized_image, dtype=input_details["dtype"])
    image_array = np.expand_dims(image_array, axis=0)

    interpreter.set_tensor(input_details["index"], image_array)
    interpreter.invoke()

    scores = interpreter.get_tensor(output_details["index"])[0]
    if scores.shape != (len(labels),) or not np.isfinite(scores).all():
        raise RuntimeError("The model returned invalid class scores.")
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [
        {
            "class_index": int(index),
            "label": labels[int(index)],
            "score": float(scores[index]),
        }
        for index in top_indices
    ]


def predict_disease(image_path, interpreter, labels, top_k: int = 3):
    from PIL import Image

    with Image.open(image_path) as image:
        return predict_image(image, interpreter, labels, top_k)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", type=Path)
    args = parser.parse_args()

    interpreter, labels = load_model()
    predictions = predict_disease(args.image_path, interpreter, labels)
    for result in predictions:
        print(f"{result['label']}: {result['score']:.2%}")
