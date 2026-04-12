"use client";

import { ModelCard } from "@/components/model-card";
import { listModels } from "@/lib/api";
import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

interface ModelData {
  id: string;
  owner_id: string;
  slug: string;
  display_name: string;
  description: string | null;
  framework: string | null;
  task: string | null;
  tags: string[] | null;
  total_downloads: number;
  total_likes: number;
  chain_tx_hash: string | null;
  updated_at: string;
}

function ModelsContent() {
  const t = useTranslations("home");
  const searchParams = useSearchParams();
  const [models, setModels] = useState<ModelData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params: Record<string, string> = {};
    const q = searchParams.get("q");
    const framework = searchParams.get("framework");
    const task = searchParams.get("task");
    if (q) params.q = q;
    if (framework) params.framework = framework;
    if (task) params.task = task;

    listModels(params)
      .then((data) => setModels(data.models))
      .catch(() => setModels([]))
      .finally(() => setLoading(false));
  }, [searchParams]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        {t("explore")}
      </h1>

      {/* Filters */}
      <div className="flex gap-3 mb-6 flex-wrap">
        {["pytorch", "tensorflow", "jax", "gguf"].map((fw) => (
          <a
            key={fw}
            href={`/models?framework=${fw}`}
            className={`px-3 py-1.5 text-sm rounded-lg border ${
              searchParams.get("framework") === fw
                ? "bg-blue-100 border-blue-300 text-blue-700"
                : "bg-white border-gray-200 text-gray-600 hover:border-blue-300"
            }`}
          >
            {fw}
          </a>
        ))}
      </div>

      {/* Model list */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : models.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-2">No models found</p>
          <p className="text-sm text-gray-400">
            Be the first to upload a model!
          </p>
        </div>
      ) : (
        <div className="grid gap-3">
          {models.map((model) => (
            <ModelCard
              key={model.id}
              owner="user"
              slug={model.slug}
              displayName={model.display_name}
              description={model.description}
              framework={model.framework}
              task={model.task}
              tags={model.tags}
              totalDownloads={model.total_downloads}
              totalLikes={model.total_likes}
              chainTxHash={model.chain_tx_hash}
              updatedAt={model.updated_at}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function ModelsPage() {
  return (
    <Suspense fallback={<div className="text-center py-12 text-gray-500">Loading...</div>}>
      <ModelsContent />
    </Suspense>
  );
}
