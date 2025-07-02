import { memo } from 'react';
import { Handle, Position } from 'reactflow';

interface CommandNodeProps {
  data: {
    label: string;
    details: {
      action: string;
      targetValue: any;
      place: string;
    };
  };
}

export default memo(function CommandNode({ data }: CommandNodeProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg border-2 border-blue-200 p-4 w-64">
      <div className="flex items-center space-x-3 mb-3">
        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"/>
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-800">{data.label}</h3>
          <p className="text-sm text-slate-500">Command</p>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-600">Target</span>
          <span className="text-sm font-mono bg-blue-50 text-blue-700 px-2 py-1 rounded">
            {data.details.place}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-600">Value</span>
          <span className="text-sm font-mono bg-blue-50 text-blue-700 px-2 py-1 rounded">
            {typeof data.details.targetValue === 'object' 
              ? JSON.stringify(data.details.targetValue) 
              : String(data.details.targetValue)}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-600">Action</span>
          <span className="text-sm bg-green-100 text-green-700 px-2 py-1 rounded">
            {data.details.action}
          </span>
        </div>
      </div>
      
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        className="w-4 h-4 bg-blue-500 border-2 border-white"
      />
    </div>
  );
});
