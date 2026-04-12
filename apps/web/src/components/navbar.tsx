"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useState } from "react";

export function Navbar() {
  const t = useTranslations("common");
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">MP</span>
              </div>
              <span className="font-bold text-lg text-gray-900">
                {t("appName")}
              </span>
            </Link>

            {/* Nav links */}
            <div className="hidden md:flex items-center gap-6">
              <Link
                href="/models"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                {t("models")}
              </Link>
              <Link
                href="/datasets"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                {t("datasets")}
              </Link>
              <Link
                href="/spaces"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                {t("spaces")}
              </Link>
              <Link
                href="/docs"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                {t("docs")}
              </Link>
            </div>
          </div>

          {/* Search + Auth */}
          <div className="flex items-center gap-4">
            <div className="hidden sm:block">
              <input
                type="text"
                placeholder={t("search")}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-64 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <Link
              href="/login"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              {t("login")}
            </Link>
            <Link
              href="/register"
              className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg hover:bg-blue-700"
            >
              {t("register")}
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
