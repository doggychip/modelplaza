"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";

interface ModelCardProps {
  owner: string;
  slug: string;
  displayName: string;
  description: string | null;
  framework: string | null;
  task: string | null;
  tags: string[] | null;
  totalDownloads: number;
  totalLikes: number;
  chainTxHash: string | null;
  updatedAt: string;
}

export function ModelCard({
  owner,
  slug,
  displayName,
  description,
  framework,
  task,
  tags,
  totalDownloads,
  totalLikes,
  chainTxHash,
  updatedAt,
}: ModelCardProps) {
  const t = useTranslations("common");

  return (
    <Link
      href={`/models/${owner}/${slug}`}
      className="block bg-white rounded-lg border border-gray-200 p-4 hover:border-blue-300 hover:shadow-sm transition-all"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-gray-900 truncate">
              {owner}/{displayName}
            </h3>
            {chainTxHash && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                on-chain
              </span>
            )}
          </div>
          {description && (
            <p className="mt-1 text-sm text-gray-500 line-clamp-2">
              {description}
            </p>
          )}
          <div className="mt-2 flex items-center gap-3 flex-wrap">
            {framework && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-purple-100 text-purple-700">
                {framework}
              </span>
            )}
            {task && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-blue-100 text-blue-700">
                {task}
              </span>
            )}
            {tags?.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
      <div className="mt-3 flex items-center gap-4 text-xs text-gray-400">
        <span>{t("downloads")}: {totalDownloads.toLocaleString()}</span>
        <span>{t("likes")}: {totalLikes}</span>
        <span>{new Date(updatedAt).toLocaleDateString()}</span>
      </div>
    </Link>
  );
}
