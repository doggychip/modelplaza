"use client";

import { getModel, getProvenance } from "@/lib/api";
import { useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

interface ModelData {
  id: string;
  slug: string;
  display_name: string;
  description: string | null;
  framework: string | null;
  task: string | null;
  license_type: string | null;
  tags: string[] | null;
  total_downloads: number;
  total_likes: number;
  chain_tx_hash: string | null;
  model_content_hash: string | null;
  created_at: string;
}

interface ProvenanceData {
  content_hash: string | null;
  chain_tx_hash: string | null;
  chain_block_number: number | null;
  license_type: string | null;
  registered_at: string | null;
  explorer_url: string | null;
}

export default function ModelDetailPage() {
  const t = useTranslations("model");
  const tc = useTranslations("common");
  const params = useParams<{ owner: string; slug: string }>();
  const [model, setModel] = useState<ModelData | null>(null);
  const [provenance, setProvenance] = useState<ProvenanceData | null>(null);
  const [activeTab, setActiveTab] = useState<"card" | "provenance">("card");

  useEffect(() => {
    if (!params.owner || !params.slug) return;
    getModel(params.owner, params.slug)
      .then(setModel)
      .catch(() => {});
    getProvenance(params.owner, params.slug)
      .then(setProvenance)
      .catch(() => {});
  }, [params.owner, params.slug]);

  if (!model) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center text-gray-500">
        Loading...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-2xl font-bold text-gray-900">
            {params.owner}/{model.display_name}
          </h1>
          {model.chain_tx_hash && (
            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
              {t("verifiedOnChain")}
            </span>
          )}
        </div>
        {model.description && (
          <p className="text-gray-600">{model.description}</p>
        )}
        <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
          {model.framework && (
            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full text-xs">
              {model.framework}
            </span>
          )}
          {model.task && (
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">
              {model.task}
            </span>
          )}
          {model.license_type && (
            <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
              {model.license_type}
            </span>
          )}
          <span>
            {tc("downloads")}: {model.total_downloads.toLocaleString()}
          </span>
          <span>
            {tc("likes")}: {model.total_likes}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <div className="flex gap-6">
          <button
            onClick={() => setActiveTab("card")}
            className={`pb-3 text-sm font-medium border-b-2 ${
              activeTab === "card"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t("card")}
          </button>
          <button
            onClick={() => setActiveTab("provenance")}
            className={`pb-3 text-sm font-medium border-b-2 ${
              activeTab === "provenance"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t("provenance")}
          </button>
        </div>
      </div>

      {/* Tab content */}
      {activeTab === "card" && (
        <div className="prose max-w-none">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4">{t("card")}</h2>
            <p className="text-gray-600">
              {model.description || "No model card yet. Upload a README.md to add one."}
            </p>
            {model.tags && model.tags.length > 0 && (
              <div className="mt-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  {t("tags")}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {model.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "provenance" && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">{t("provenance")}</h2>
          {provenance?.chain_tx_hash ? (
            <dl className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Content Hash (SHA-256)
                </dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono break-all">
                  {provenance.content_hash}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Transaction Hash
                </dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono break-all">
                  {provenance.chain_tx_hash}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Block Number
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {provenance.chain_block_number}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  {t("license")}
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {provenance.license_type}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Registered At
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {provenance.registered_at
                    ? new Date(provenance.registered_at).toLocaleString()
                    : "-"}
                </dd>
              </div>
              {provenance.explorer_url && (
                <div className="pt-2">
                  <a
                    href={provenance.explorer_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    {t("viewOnExplorer")} &rarr;
                  </a>
                </div>
              )}
            </dl>
          ) : (
            <p className="text-gray-500 text-sm">{t("notRegistered")}</p>
          )}
        </div>
      )}

      {/* Download button */}
      <div className="mt-8">
        <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
          {tc("download")}
        </button>
      </div>
    </div>
  );
}
