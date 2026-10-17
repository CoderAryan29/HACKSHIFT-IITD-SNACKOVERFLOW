
import json
import numpy as np
import tensorflow as tf
from PIL import Image
from huggingface_hub import hf_hub_download

MODEL_ID = "animeshakr/plant-disease-efficientnetv2s"


def load_model():
    print("Downloading model files if needed...")

    model_path = hf_hub_download(
        repo_id=MODEL_ID,
        filename="model_float16_quant.tflite",
    )

    labels_path = hf_hub_download(
        repo_id=MODEL_ID,
        filename="class_indices.json",
    )

    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    with open(labels_path, "r", encoding="utf-8") as file:
        labels = json.load(file)

    print("Model loaded successfully!")
    return interpreter, labels


def predict_disease(image_path, interpreter, labels, top_k=3):
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    # Read the image and resize it to the model's input size.
    height = int(input_details["shape"][1])
    width = int(input_details["shape"][2])

    image = Image.open(image_path).convert("RGB")
    image = image.resize((width, height))

    image_array = np.asarray(image, dtype=np.float32)
    image_array = np.expand_dims(image_array, axis=0)

    interpreter.set_tensor(input_details["index"], image_array)
    interpreter.invoke()

    scores = interpreter.get_tensor(output_details["index"])[0]
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for index in top_indices:
        results.append({
            "label": labels.get(str(int(index)), f"Class {index}"),
            "score": float(scores[index]),
        })

    return results


if __name__ == "__main__":
    interpreter, labels = load_model()

    image_path = input(
        "Enter the full path to a plant leaf image: "
    ).strip().strip('"')

    predictions = predict_disease(image_path, interpreter, labels)

    print("\nTop predictions:")
    for result in predictions:
        print(
            f"{result['label']}: "
            f"{result['score']:.2%}"
        )
