import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { WorkflowSchema } from '@shared/schema';

export function useWorkflowData() {
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isConnected, setIsConnected] = useState(true);

  const {
    data: rawData,
    error,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['/assets/workflow.json'],
    queryFn: async () => {
      try {
        const response = await fetch('/assets/workflow.json');
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        
        // Validate the data against our schema
        const validatedData = WorkflowSchema.parse(data);
        setLastUpdate(new Date());
        setIsConnected(true);
        return validatedData;
      } catch (error) {
        setIsConnected(false);
        throw error;
      }
    },
    refetchInterval: 2000,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // Manual refresh function
  const refresh = useCallback(() => {
    refetch();
  }, [refetch]);

  // Set up error state monitoring
  useEffect(() => {
    if (error) {
      setIsConnected(false);
    }
  }, [error]);

  return {
    data: rawData,
    isLoading,
    error,
    lastUpdate,
    isConnected,
    refresh,
  };
}
