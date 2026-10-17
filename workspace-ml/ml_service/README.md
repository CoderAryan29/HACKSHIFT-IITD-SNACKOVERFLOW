# Crop disease inference API

This API runs the existing TensorFlow Lite EfficientNetV2S model referenced by
`inference/hf_disease_test.py`. It loads the model and label map from the local
Hugging Face cache only; startup does not download model files. The expected
cache repository is `animeshakr/plant-disease-efficientnetv2s`.

Install dependencies and start the API from the `workspace-ml` directory:

```powershell
python -m pip install -r requirements.in
python -m uvicorn ml_service.api:app --host 127.0.0.1 --port 8000
```

If the assets are stored at non-default paths, set
`KISANSETU_TFLITE_MODEL_PATH` and/or `KISANSETU_TFLITE_LABELS_PATH` to the
existing files before starting the service. The files must be non-empty and
match the model.

The default CORS origins are `http://localhost:5173` and
`http://127.0.0.1:5173`. Override them with a comma-separated
`KISANSETU_CORS_ORIGINS` value when needed.

## Endpoints

- `GET /health` returns `ready`, `model_ready`, and `model_used`. It responds
  with HTTP 503 and a useful `detail` when model loading or required cached
  assets are unavailable.
- `POST /predict` accepts an image multipart field named `file`. JPG, JPEG,
  PNG, and WebP are supported; uploads are limited to 10 MB and 20 megapixels.

Successful prediction response:

```json
{
  "success": true,
  "prediction": {
    "class_name": "Tomato___Early_blight",
    "display_name": "Tomato Early blight",
    "confidence": 0.94
  },
  "top_predictions": [],
  "model_used": "animeshakr/plant-disease-efficientnetv2s:tflite"
}
```

The example values are illustrative. The endpoint returns the actual raw class
scores produced by the model; it does not apply an additional softmax.

## Model input and limitations

The cached model has a `float32` input tensor shaped `[1, 384, 384, 3]` and a
`float32` output tensor shaped `[1, 38]`. Images are converted to RGB, resized
to 384 × 384 with Pillow's default resize filter, converted to `float32`, and
batched. No additional normalization is applied. The output is already a
38-class softmax, so predictions rank those scores directly against the
ordered `class_indices.json` labels.

The model was trained on PlantVillage images. Its performance on real farm
photos is not validated; confidence is the model's score, not guaranteed
accuracy. The API does not infer treatment or fertilizer advice from a class
label.
