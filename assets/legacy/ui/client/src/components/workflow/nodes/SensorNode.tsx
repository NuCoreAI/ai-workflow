import { memo } from 'react';
import { Handle, Position } from 'reactflow';

interface SensorNodeProps {
  data: {
    label: string;
    details: Record<string, any>;
  };
}

export default memo(function SensorNode({ data }: SensorNodeProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg border-2 border-emerald-200 p-4 w-64">
      <div className="flex items-center space-x-3 mb-3">
        <div className="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
            <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/>
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-800">{data.label}</h3>
          <p className="text-sm text-slate-500">Sensor</p>
        </div>
      </div>
      
      {/* Display sensor details */}
      <div className="space-y-2">
        {Object.entries(data.details).map(([key, value]) => (
          <div key={key} className="flex justify-between items-center">
            <span className="text-sm text-slate-600">{key}</span>
            <span className="text-sm font-mono bg-slate-100 px-2 py-1 rounded">
              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
            </span>
          </div>
        ))}
      </div>
      
      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        className="w-4 h-4 bg-emerald-500 border-2 border-white"
      />
    </div>
  );
});
