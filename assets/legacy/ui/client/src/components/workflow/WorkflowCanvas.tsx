import { useCallback, useEffect, useMemo, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Controls,
  Background,
  useReactFlow,
  ReactFlowInstance,
} from 'reactflow';
import 'reactflow/dist/style.css';

import SensorNode from './nodes/SensorNode';
import GuardNode from './nodes/GuardNode';
import CommandNode from './nodes/CommandNode';
import { ProcessedWorkflow } from '@shared/schema';
import { processWorkflowData } from '@/lib/workflowUtils';

const nodeTypes = {
  sensor: SensorNode,
  guard: GuardNode,
  command: CommandNode,
};

interface WorkflowCanvasProps {
  workflowData: any;
  isLoading: boolean;
  error: Error | null;
}

export default function WorkflowCanvas({ workflowData, isLoading, error }: WorkflowCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const { fitView, zoomIn, zoomOut } = useReactFlow();

  const processedData = useMemo(() => {
    if (!workflowData) return null;
    return processWorkflowData(workflowData);
  }, [workflowData]);

  useEffect(() => {
    if (processedData) {
      setNodes(processedData.nodes as Node[]);
      setEdges(processedData.edges as Edge[]);
      
      // Auto-fit view when new data is loaded
      setTimeout(() => {
        if (reactFlowInstance) {
          fitView({ padding: 0.2 });
        }
      }, 100);
    }
  }, [processedData, setNodes, setEdges, reactFlowInstance, fitView]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onInit = useCallback((instance: ReactFlowInstance) => {
    setReactFlowInstance(instance);
  }, []);

  // Custom wheel handler for pan/zoom
  const onWheel = useCallback((event: React.WheelEvent) => {
    if (event.shiftKey) {
      // Zoom with shift + scroll
      event.preventDefault();
      if (event.deltaY < 0) {
        zoomIn();
      } else {
        zoomOut();
      }
    }
    // Default behavior (pan) when shift is not pressed
  }, [zoomIn, zoomOut]);

  const handleFitView = useCallback(() => {
    fitView({ padding: 0.2 });
  }, [fitView]);

  const handleAutoLayout = useCallback(() => {
    if (!processedData) return;
    
    // Simple auto-layout: arrange nodes in a flow from left to right
    const layoutedNodes = nodes.map((node, index) => {
      let x = 100;
      let y = 100 + (index * 300);
      
      if (node.type === 'sensor') {
        x = 100;
      } else if (node.type === 'guard') {
        x = 500;
      } else if (node.type === 'command') {
        x = 950;
      }
      
      return {
        ...node,
        position: { x, y }
      };
    });
    
    setNodes(layoutedNodes);
    setTimeout(() => fitView({ padding: 0.2 }), 100);
  }, [nodes, setNodes, fitView, processedData]);

  if (isLoading) {
    return (
      <div className="flex-1 relative bg-slate-100">
        <div className="absolute inset-0 bg-slate-100 bg-opacity-75 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-lg p-6 flex items-center space-x-4">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-slate-700">Loading workflow...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 relative bg-slate-100">
        <div className="absolute inset-0 bg-slate-100 bg-opacity-75 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-800">Connection Error</h3>
            </div>
            <p className="text-slate-600 mb-4">
              Unable to load workflow data: {error.message}
            </p>
            <button 
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              onClick={() => window.location.reload()}
            >
              Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 relative bg-slate-100" onWheel={onWheel}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onInit={onInit}
        nodeTypes={nodeTypes}
        fitView
        panOnScroll={true}
        zoomOnScroll={false}
        panOnDrag={true}
        className="bg-slate-100"
      >
        <Background 
          color="#64748b" 
          gap={20} 
          size={1}
          variant="dots"
        />
        <Controls 
          position="top-right"
          showFitView={true}
          showZoom={true}
          showInteractive={false}
        />
      </ReactFlow>

      {/* Floating Controls */}
      <div className="absolute top-4 right-4 flex flex-col space-y-2 z-10">
        {/* Layout Controls */}
        <div className="bg-white rounded-lg shadow-lg border border-slate-200 p-2 flex flex-col space-y-1">
          <button 
            className="w-8 h-8 flex items-center justify-center hover:bg-slate-100 rounded"
            onClick={handleAutoLayout}
            title="Auto Layout"
          >
            <svg className="w-4 h-4 text-slate-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
            </svg>
          </button>
          <button 
            className="w-8 h-8 flex items-center justify-center hover:bg-slate-100 rounded"
            onClick={handleFitView}
            title="Fit View"
          >
            <svg className="w-4 h-4 text-slate-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 11-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15 13.586V12a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      {/* Help Text */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg border border-slate-200 p-3 text-sm text-slate-600">
        <div className="space-y-1">
          <div>Scroll: Pan canvas</div>
          <div>Shift + Scroll: Zoom</div>
        </div>
      </div>
    </div>
  );
}
