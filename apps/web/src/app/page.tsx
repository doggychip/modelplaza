import { useTranslations } from "next-intl";
import Link from "next/link";

const FRAMEWORKS = ["PyTorch", "TensorFlow", "JAX", "GGUF", "ONNX", "SafeTensors"];
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

export default function Home() {
  const t = useTranslations("home");
  const tc = useTranslations("common");

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-b from-blue-600 to-blue-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-20 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">{t("hero")}</h1>
          <p className="text-lg md:text-xl text-blue-100 mb-8">
            {t("subtitle")}
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link
              href="/models"
              className="bg-white text-blue-700 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              {t("explore")}
            </Link>
            <Link
              href="/register"
              className="border border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors"
            >
              {tc("register")}
            </Link>
          </div>
        </div>
      </section>

      {/* Frameworks */}
      <section className="max-w-7xl mx-auto px-4 py-12">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          {t("frameworks")}
        </h2>
        <div className="flex flex-wrap gap-3">
          {FRAMEWORKS.map((fw) => (
            <Link
              key={fw}
              href={`/models?framework=${fw.toLowerCase()}`}
              className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:border-blue-300 hover:text-blue-600 transition-colors"
            >
              {fw}
            </Link>
          ))}
        </div>
      </section>

      {/* Tasks */}
      <section className="max-w-7xl mx-auto px-4 pb-12">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          {t("tasks")}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {TASKS.map((task) => (
            <Link
              key={task}
              href={`/models?task=${task}`}
              className="px-4 py-3 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:border-blue-300 hover:text-blue-600 transition-colors text-center"
            >
              {task}
            </Link>
          ))}
        </div>
      </section>

      {/* On-chain value prop */}
      <section className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-16">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="text-3xl mb-3">&#x1f517;</div>
              <h3 className="text-lg font-semibold mb-2">On-Chain Provenance</h3>
              <p className="text-gray-400 text-sm">
                Every model upload is registered on-chain with SHA-256 hash,
                timestamp, and license. Immutable proof of authorship.
              </p>
            </div>
            <div>
              <div className="text-3xl mb-3">&#x1f4dc;</div>
              <h3 className="text-lg font-semibold mb-2">License NFTs</h3>
              <p className="text-gray-400 text-sm">
                Programmable usage rights. Commercial, research, or derivative
                licenses as verifiable on-chain tokens.
              </p>
            </div>
            <div>
              <div className="text-3xl mb-3">&#x1f4b0;</div>
              <h3 className="text-lg font-semibold mb-2">Token Rewards</h3>
              <p className="text-gray-400 text-sm">
                Earn tokens for uploading models, contributing datasets, and
                community participation. Use tokens for inference credits.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
