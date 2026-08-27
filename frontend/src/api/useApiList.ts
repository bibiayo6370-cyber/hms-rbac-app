import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import type { PaginatedResponse } from "../types";

export function useApiList<T>(endpoint: string, deps: unknown[] = []) {
  const [items, setItems] = useState<T[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      const { data } = await apiClient.get<PaginatedResponse<T> | T[]>(endpoint);
      // Handles both paginated ({results: [...]}) and plain-array responses.
      setItems(Array.isArray(data) ? data : data.results);
    } catch {
      setError("Failed to load data. Please try again.");
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpoint, ...deps]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { items, isLoading, error, reload, setItems };
}
