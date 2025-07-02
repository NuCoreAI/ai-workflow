import { useEffect, useState, useMemo } from 'react';
import { ReactFlowProvider } from 'reactflow';
import WorkflowCanvas from '@/components/workflow/WorkflowCanvas';
import WorkflowSidebar from '@/components/workflow/WorkflowSidebar';
import { useWorkflowData } from '@/hooks/useWorkflowData';
import { processWorkflowData } from '@/lib/workflowUtils';

export default function WorkflowVisualizer() {
  const { data: rawWorkflowData, isLoading, error, lastUpdate, isConnected } = useWorkflowData();
  
  // Process the workflow data for display
  const processedWorkflowData = useMemo(() => {
    if (!rawWorkflowData) return null;
    return processWorkflowData(rawWorkflowData);
  }, [rawWorkflowData]);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getTimeSinceUpdate = () => {
    if (!lastUpdate) return 'Never';
    const secondsAgo = Math.floor((currentTime.getTime() - lastUpdate.getTime()) / 1000);
    if (secondsAgo < 60) return `${secondsAgo}s ago`;
    const minutesAgo = Math.floor(secondsAgo / 60);
    return `${minutesAgo}m ago`;
  };

  return (
    <ReactFlowProvider>
      <div className="h-screen flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-800">Workflow Visualizer</h1>
                <p className="text-sm text-slate-500">Real-time workflow monitoring</p>
              </div>
            </div>
          </div>
          
          {/* Status Indicators */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}></div>
              <span className="text-sm text-slate-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <svg className="w-4 h-4 text-slate-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-slate-600">
                Last update: {getTimeSinceUpdate()}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <svg className="w-4 h-4 text-slate-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-slate-600">Auto-refresh: 10s</span>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="flex-1 flex">
          <WorkflowCanvas 
            workflowData={rawWorkflowData}
            isLoading={isLoading}
            error={error}
          />
          <WorkflowSidebar workflowData={processedWorkflowData} />
        </div>
      </div>
    </ReactFlowProvider>
  );
}
