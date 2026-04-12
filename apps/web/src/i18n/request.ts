import { getRequestConfig } from "next-intl/server";

export default getRequestConfig(async () => {
  const locale = "zh"; // Default to Chinese, can be dynamic later

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
  };
});
