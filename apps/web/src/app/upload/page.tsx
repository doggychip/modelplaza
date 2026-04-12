"use client";

import { useAuth } from "@/lib/auth-context";
import { createModel } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useCallback, useRef, useState } from "react";

const FRAMEWORKS = ["pytorch", "tensorflow", "jax", "gguf", "onnx", "safetensors"];
const TASKS = [
  "text-generation",
  "text-classification",
  "image-classification",
  "object-detection",
  "translation",
  "summarization",
  "question-answering",
  "text-to-image",
];
const LICENSES = ["apache-2.0", "mit", "cc-by-4.0", "cc-by-sa-4.0", "cc-by-nc-4.0", "gpl-3.0", "custom"];

export default function UploadPage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [slug, setSlug] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [framework, setFramework] = useState("");
  const [task, setTask] = useState("");
  const [license, setLicense] = useState("apache-2.0");
  const [tags, setTags] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  if (!user) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center">
        <p className="text-gray-500 mb-4">Please login to upload models.</p>
        <a href="/login" className="text-blue-600 hover:text-blue-800 font-medium">
          Go to login
        </a>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file to upload");
      return;
    }
    setError("");
    setUploading(true);
    setProgress(0);

    try {
      // Step 1: Create model repo
      setProgress(10);
      const tagList = tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);

      await createModel({
        slug,
        display_name: displayName || slug,
        description,
        framework: framework || undefined,
        task: task || undefined,
        license_type: license,
        tags: tagList.length > 0 ? tagList : undefined,
      });
      setProgress(30);

      // Step 2: Upload file
      const formData = new FormData();
      formData.append("file", file);

      const resp = await fetch(
        `/api/v1/models/${user.username}/${slug}/upload?version_tag=v1`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        }
      );
      setProgress(90);

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(err.detail);
      }

      setProgress(100);
      router.push(`/models/${user.username}/${slug}`);
    } catch (err) {
      if (err instanceof Error && err.message.includes("already exists")) {
        // Model exists, try upload directly
        try {
          const formData = new FormData();
          formData.append("file", file);
          const resp = await fetch(
            `/api/v1/models/${user.username}/${slug}/upload?version_tag=v1`,
            {
              method: "POST",
              headers: { Authorization: `Bearer ${token}` },
              body: formData,
            }
          );
          if (resp.ok) {
            setProgress(100);
            router.push(`/models/${user.username}/${slug}`);
            return;
          }
        } catch {}
      }
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Upload Model</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File drop zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={() => setDragOver(false)}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            dragOver
              ? "border-blue-500 bg-blue-50"
              : file
              ? "border-green-400 bg-green-50"
              : "border-gray-300 hover:border-blue-400"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) setFile(f);
            }}
          />
          {file ? (
            <div>
              <p className="text-sm font-medium text-green-700">{file.name}</p>
              <p className="text-xs text-gray-500 mt-1">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <div>
              <p className="text-gray-500">
                Drag and drop your model file here, or click to browse
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Supports .bin, .pt, .safetensors, .gguf, .onnx, etc.
              </p>
            </div>
          )}
        </div>

        {/* Model slug */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Model ID (slug) *
          </label>
          <div className="flex items-center">
            <span className="text-sm text-gray-500 mr-1">{user.username}/</span>
            <input
              type="text"
              value={slug}
              onChange={(e) =>
                setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, "-"))
              }
              required
              placeholder="my-model-7b"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Display name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Display Name
          </label>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="My Model 7B"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            placeholder="A brief description of your model..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Framework + Task */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Framework
            </label>
            <select
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select...</option>
              {FRAMEWORKS.map((fw) => (
                <option key={fw} value={fw}>
                  {fw}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Task
            </label>
            <select
              value={task}
              onChange={(e) => setTask(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select...</option>
              {TASKS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* License */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            License
          </label>
          <select
            value={license}
            onChange={(e) => setLicense(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {LICENSES.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="llm, chinese, qwen"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Error */}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {/* Progress */}
        {uploading && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={uploading || !slug}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {uploading ? `Uploading... ${progress}%` : "Upload Model"}
        </button>
      </form>
    </div>
  );
}
