import { useRef, useState } from "react";
import { uploadProductImage } from "../services/api";
import ErrorMessage from "./ErrorMessage";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_BYTES = 5 * 1024 * 1024;

function getErrorMessage(err) {
  return (
    err?.response?.data?.detail ||
    err?.message ||
    "Image upload failed. Please try again."
  );
}

/**
 * Image uploader for product forms.
 *
 * Props:
 *   value       — the current image URL (string or ""). Controlled.
 *   onChange    — (url) => void
 *   disabled    — optional, disables picker while uploading
 */
export default function ImageUploader({ value, onChange, disabled }) {
  const inputRef = useRef(null);
  const [preview, setPreview] = useState(value || "");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handlePick = () => inputRef.current?.click();

  const handleFile = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow re-selecting the same file
    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError("Please choose a JPG, PNG, or WebP image.");
      return;
    }
    if (file.size > MAX_BYTES) {
      setError("Image is larger than 5MB. Please choose a smaller file.");
      return;
    }

    // Show a local preview immediately while we upload.
    const localUrl = URL.createObjectURL(file);
    setPreview(localUrl);
    setError(null);
    setUploading(true);
    try {
      const { image_url } = await uploadProductImage(file);
      onChange?.(image_url);
      // Replace the object-URL preview with the server URL.
      setPreview(image_url);
      URL.revokeObjectURL(localUrl);
    } catch (err) {
      setPreview(value || "");
      setError(getErrorMessage(err));
    } finally {
      setUploading(false);
    }
  };

  const clear = () => {
    setPreview("");
    setError(null);
    onChange?.("");
  };

  return (
    <div className="image-uploader">
      {error && <ErrorMessage message={error} />}

      <div className="image-uploader-preview">
        {preview ? (
          <img src={preview} alt="Product preview" />
        ) : (
          <div className="image-uploader-placeholder">No image selected</div>
        )}
        {uploading && <div className="image-uploader-overlay">Uploading…</div>}
      </div>

      <div className="image-uploader-actions">
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFile}
          style={{ display: "none" }}
          disabled={disabled || uploading}
        />
        <button
          type="button"
          className="btn btn-outline"
          onClick={handlePick}
          disabled={disabled || uploading}
        >
          {uploading ? "Uploading…" : preview ? "Replace image" : "Choose image from computer"}
        </button>
        {preview && !uploading && (
          <button
            type="button"
            className="btn btn-outline btn-danger-text"
            onClick={clear}
            disabled={disabled}
          >
            Remove
          </button>
        )}
      </div>
      <p className="dash-muted" style={{ fontSize: 12, marginTop: 6 }}>
        JPG, PNG, or WebP up to 5MB. The image is uploaded to the server and
        a public URL is filled in automatically.
      </p>
    </div>
  );
}
