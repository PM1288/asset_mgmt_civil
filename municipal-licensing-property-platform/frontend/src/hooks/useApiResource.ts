import type { Dispatch, SetStateAction } from "react";
import { useEffect, useState } from "react";

type ResourceState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  setData: Dispatch<SetStateAction<T | null>>;
};

export function useApiResource<T>(loader: () => Promise<T>, dependencies: unknown[] = []): ResourceState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const next = await loader();
      setData(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return { data, loading, error, reload: load, setData };
}
