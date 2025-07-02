import { useMemo } from 'react';
import { ProcessedWorkflow } from '@shared/schema';

interface WorkflowSidebarProps {
  workflowData: ProcessedWorkflow | null;
}

export default function WorkflowSidebar({ workflowData }: WorkflowSidebarProps) {
  const stats = useMemo(() => {
    if (!workflowData || !workflowData.metadata) {
      return {
        totalNodes: 0,
        sensors: 0,
        commands: 0,
        activeWorkflows: 0,
      };
    }

    return {
      totalNodes: workflowData.metadata.totalNodes,
      sensors: workflowData.metadata.sensors,
      commands: workflowData.metadata.commands,
      activeWorkflows: workflowData.nodes.length > 0 ? 1 : 0,
    };
  }, [workflowData]);

  const workflows = useMemo(() => {
    if (!workflowData || workflowData.nodes.length === 0) return [];

    // Extract workflow information from the processed data
    const sensorNodes = workflowData.nodes.filter(node => node.type === 'sensor');
    const guardNodes = workflowData.nodes.filter(node => node.type === 'guard');
    const commandNodes = workflowData.nodes.filter(node => node.type === 'command');

    return guardNodes.map((guard, index) => {
      const relatedSensor = sensorNodes[index] || sensorNodes[0];
      const relatedCommand = commandNodes[index] || commandNodes[0];
      console.log('here')
      return {
        id: guard.id,
        title: `${relatedSensor?.data.label || 'Sensor'} → ${relatedCommand?.data.label || 'Command'}`,
        description: `Automated workflow based on ${relatedSensor?.data.label || 'sensor'} conditions`,
        conditions: guard.data.details?.conditions || [],
        action: relatedCommand?.data.details || {},
        status: 'Active',
        lastTriggered: 'Never',
      };
    });
  }, [workflowData]);

  return (
    <div className="w-80 bg-white border-l border-slate-200 flex flex-col">
      {/* Panel Header */}
      <div className="p-6 border-b border-slate-200">
        <h2 className="text-lg font-semibold text-slate-800 mb-2">Workflow Details</h2>
        <p className="text-sm text-slate-500">Live workflow monitoring and statistics</p>
      </div>

      {/* Workflow Stats */}
      <div className="p-6 border-b border-slate-200">
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.totalNodes}</div>
            <div className="text-sm text-slate-500">Total Nodes</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-emerald-600">{stats.activeWorkflows}</div>
            <div className="text-sm text-slate-500">Active Workflows</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-amber-600">{stats.sensors}</div>
            <div className="text-sm text-slate-500">Sensors</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{stats.commands}</div>
            <div className="text-sm text-slate-500">Commands</div>
          </div>
        </div>
      </div>

      {/* Active Workflows */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6">
          <h3 className="font-semibold text-slate-800 mb-4">Active Workflows</h3>
          
          {workflows.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 bg-slate-200 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-slate-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-sm text-slate-500">No active workflows</p>
            </div>
          ) : (
            <div className="space-y-4">
              {workflows.map((workflow) => (
                <div key={workflow.id} className="bg-slate-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-slate-800">{workflow.title}</h4>
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                      {workflow.status}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mb-3">{workflow.description}</p>
                  
                  <div className="space-y-2">
                    {workflow.conditions.length > 0 && (
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-500">Condition:</span>
                        <span className="font-mono text-slate-700">
                          {workflow.conditions[0]?.operator} {workflow.conditions[0]?.value}
                        </span>
                      </div>
                    )}
                    
                    {workflow.action.targetValue && (
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-500">Action:</span>
                        <span className="font-mono text-slate-700">
                          Set to {workflow.action.targetValue}
                        </span>
                      </div>
                    )}
                    
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-500">Last Triggered:</span>
                      <span className="text-slate-600">{workflow.lastTriggered}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Help Section */}
      <div className="p-6 border-t border-slate-200 bg-slate-50">
        <h3 className="font-semibold text-slate-800 mb-3">Controls</h3>
        <div className="space-y-2 text-sm text-slate-600">
          <div className="flex justify-between">
            <span>Pan canvas:</span>
            <span className="font-mono bg-white px-2 py-1 rounded text-xs">Scroll</span>
          </div>
          <div className="flex justify-between">
            <span>Zoom:</span>
            <span className="font-mono bg-white px-2 py-1 rounded text-xs">Shift + Scroll</span>
          </div>
          <div className="flex justify-between">
            <span>Fit view:</span>
            <span className="font-mono bg-white px-2 py-1 rounded text-xs">Click fit button</span>
          </div>
        </div>
      </div>
    </div>
  );
}
