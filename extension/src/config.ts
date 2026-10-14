// Configuration manager for SmartConsent AI
// Handles dynamic backend endpoints across Chrome Extension and Web deployments

const STORAGE_KEY = 'smartconsent_api_base_url';

export const getStoredApiUrl = (): string => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && saved.trim()) {
      return saved.trim().replace(/\/+$/, '');
    }
  } catch {
    // localStorage might not be accessible in all contexts
  }

  // Vite environment variable injected at build time (e.g. for Vercel/Netlify)
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '');
  }

  // Default local backend
  return 'http://localhost:8000';
};

export const setStoredApiUrl = (url: string): void => {
  try {
    const cleaned = url.trim().replace(/\/+$/, '');
    if (cleaned) {
      localStorage.setItem(STORAGE_KEY, cleaned);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // ignore
  }
};

export const resetStoredApiUrl = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
};

export const testBackendHealth = async (baseUrl: string): Promise<{ ok: boolean; message: string }> => {
  try {
    const cleanUrl = baseUrl.trim().replace(/\/+$/, '');
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);

    const res = await fetch(`${cleanUrl}/health`, {
      method: 'GET',
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json().catch(() => ({}));
      return { ok: true, message: data.service || 'Connected successfully!' };
    }
    return { ok: false, message: `Server replied with HTTP ${res.status}` };
  } catch (err: any) {
    if (err.name === 'AbortError') {
      return { ok: false, message: 'Connection timed out (no response within 6s)' };
    }
    return { ok: false, message: 'Could not connect. Ensure server is online and CORS allows this origin.' };
  }
};
