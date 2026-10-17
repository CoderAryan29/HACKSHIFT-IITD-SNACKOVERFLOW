import { useEffect, useState, type ChangeEvent } from "react";
import { AlertCircle, CheckCircle2, Leaf, LoaderCircle, ShieldCheck, Upload } from "lucide-react";
import "./crop-health.css";

interface DiseasePrediction {
  class_name: string;
  display_name: string;
  confidence: number;
}

interface PredictionResponse {
  success: true;
  prediction: DiseasePrediction;
  top_predictions: DiseasePrediction[];
  model_used: string;
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
const supportedExtensions = new Set(["jpg", "jpeg", "png", "webp"]);
const maximumImageSize = 10 * 1024 * 1024;

function isPredictionResponse(value: unknown): value is PredictionResponse {
  if (typeof value !== "object" || value === null || !("prediction" in value)) return false;
  const response = value as Partial<PredictionResponse>;
  const prediction = response.prediction;
  return response.success === true
    && typeof response.model_used === "string"
    && typeof prediction === "object"
    && prediction !== null
    && typeof prediction.class_name === "string"
    && typeof prediction.display_name === "string"
    && typeof prediction.confidence === "number"
    && Number.isFinite(prediction.confidence)
    && Array.isArray(response.top_predictions);
}

function errorDetail(value: unknown): string | null {
  if (typeof value !== "object" || value === null || !("detail" in value)) return null;
  return typeof value.detail === "string" ? value.detail : null;
}

export default function CropHealthPage() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dimensions, setDimensions] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  function selectImage(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    event.target.value = "";
    setResult(null);
    setError(null);
    setDimensions(null);

    if (!selected) {
      setFile(null);
      setPreviewUrl(null);
      return;
    }

    const extension = selected.name.split(".").pop()?.toLowerCase() ?? "";
    if (!supportedExtensions.has(extension)) {
      setFile(null);
      setPreviewUrl(null);
      setError("Choose a JPG, JPEG, PNG, or WebP image.");
      return;
    }
    if (selected.size === 0) {
      setFile(null);
      setPreviewUrl(null);
      setError("The selected image is empty.");
      return;
    }
    if (selected.size > maximumImageSize) {
      setFile(null);
      setPreviewUrl(null);
      setError("Images must be 10 MB or smaller.");
      return;
    }

    setFile(selected);
    setPreviewUrl(URL.createObjectURL(selected));
  }

  async function analyzeImage() {
    if (!file || isAnalyzing) return;

    setIsAnalyzing(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${apiBaseUrl}/predict`, {
        method: "POST",
        body: formData,
      });
      let body: unknown;
      try {
        body = await response.json();
      } catch {
        throw new Error("The prediction service returned an unreadable response.");
      }
      if (!response.ok) {
        throw new Error(errorDetail(body) ?? `Prediction failed (HTTP ${response.status}).`);
      }
      if (!isPredictionResponse(body)) {
        throw new Error("The prediction service returned an unexpected response.");
      }
      setResult(body);
    } catch (caught) {
      setError(caught instanceof TypeError
        ? `Could not reach the prediction service at ${apiBaseUrl}. Check that the API is running.`
        : caught instanceof Error
          ? caught.message
          : "An unexpected error occurred while analyzing the image.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <div className="page-stack">
      <div className="page-heading">
        <div>
          <span className="eyebrow">SUPPORTING FARM TOOL</span>
          <h1>Crop Health</h1>
          <p>Upload a leaf photo for an AI-assisted assessment. This is a supporting tool, not a confirmed diagnosis.</p>
        </div>
      </div>
      <div className="scan-layout">
        <section className="panel upload-panel">
          <div className="upload-large">
            <div className="upload-illustration"><Leaf size={32} /></div>
            <h2>Check a leaf photo</h2>
            <p>Choose a clear photo of the affected leaf. Include the whole leaf and avoid heavy shadows if possible.</p>
            <label className="btn btn-primary upload-btn">
              <Upload size={17} /> Choose image
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
                hidden
                disabled={isAnalyzing}
                onChange={selectImage}
              />
            </label>
            <span className="muted-label">JPG, PNG, or WebP · up to 10 MB</span>
          </div>

          {file && previewUrl && (
            <div className="scan-preview">
              <img
                src={previewUrl}
                alt="Selected leaf preview"
                onLoad={event => {
                  const { naturalWidth, naturalHeight } = event.currentTarget;
                  setDimensions(`${naturalWidth} × ${naturalHeight} px`);
                }}
              />
              <div className="scan-file-details">
                <strong>{file.name}</strong>
                <span>{dimensions ?? "Reading image dimensions…"} · {(file.size / 1024).toFixed(0)} KB</span>
              </div>
              <button className="btn btn-primary" type="button" disabled={isAnalyzing} onClick={analyzeImage}>
                {isAnalyzing && <LoaderCircle className="scan-spinner" size={16} />}
                {isAnalyzing ? "Analyzing…" : "Analyze crop"}
              </button>
            </div>
          )}

          {error && (
            <div className="scan-message scan-error" role="alert">
              <AlertCircle size={17} /> <span>{error}</span>
            </div>
          )}

          {result && (
            <section className="scan-result" aria-live="polite">
              <div className="scan-result-heading">
                <div><CheckCircle2 size={19} /><h3>Model prediction</h3></div>
                <span>{(result.prediction.confidence * 100).toFixed(1)}% confidence</span>
              </div>
              <p className="scan-disease-name">{result.prediction.display_name}</p>
              <span className="scan-class-name">{result.prediction.class_name}</span>
              {result.top_predictions.length > 1 && (
                <div className="scan-top-predictions">
                  <h4>Other top predictions</h4>
                  <ul>
                    {result.top_predictions.slice(1).map(item => (
                      <li key={item.class_name}>
                        <span>{item.display_name}</span>
                        <span>{(item.confidence * 100).toFixed(1)}%</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          )}
        </section>

        <aside className="panel safety-panel">
          <div className="safety-icon"><ShieldCheck size={21} /></div>
          <h3>Use results carefully</h3>
          <p>Confidence is the model's score for this image, not a guarantee of accuracy. This model was trained on PlantVillage images; performance on real farm photos has not been validated.</p>
          <div className="safety-rule"><CheckCircle2 size={16} /><span>Supports 38 PlantVillage crop and disease classes.</span></div>
          <div className="safety-rule"><CheckCircle2 size={16} /><span>A result is not a confirmed diagnosis.</span></div>
          <div className="safety-rule"><CheckCircle2 size={16} /><span>No treatment advice is inferred from the label.</span></div>
        </aside>
      </div>
    </div>
  );
}
