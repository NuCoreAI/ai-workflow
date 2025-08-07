import { memo } from 'react';
import { Handle, Position } from 'reactflow';

// Helper function to convert operator to symbol
const getOperatorSymbol = (operator: string): string => {
  const operatorMap: Record<string, string> = {
    'EQUAL': '=',
    'LESS THAN': '<',
    'GREATER THAN': '>',
    'LESS THAN OR EQUAL': '≤',
    'GREATER THAN OR EQUAL': '≥',
    'AND': '∧',
    'OR': '∨',
  };
  return operatorMap[operator] || operator;
};

// Helper function to get operator color
const getOperatorColor = (operator: string): string => {
  if (operator.includes('GREATER')) return 'text-red-600';
  if (operator.includes('LESS')) return 'text-blue-600';
  if (operator === 'EQUAL') return 'text-green-600';
  return 'text-slate-600';
};

interface GuardNodeProps {
  data: {
    label: string;
    details: {
      conditions: Array<{
        operator: string;
        value: any;
        place: string;
      }>;
      operator: string;
    };
  };
}

export default memo(function GuardNode({ data }: GuardNodeProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg border-2 border-amber-200 p-4 w-80">
      <div className="flex items-center space-x-3 mb-3">
        <div className="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center">
          <svg className="w-4 h-4 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-slate-800">{data.label}</h3>
          <p className="text-sm text-slate-500">Logic</p>
        </div>
      </div>
      
      <div className="bg-amber-50 rounded p-3 space-y-2">
        {data.details.conditions.map((condition, index) => (
          <div key={index} className="bg-white rounded p-2 border border-amber-200">
            <div className="grid grid-cols-[1fr_auto_auto] gap-3 items-center">
              <div className="text-xs text-slate-600 font-medium min-w-0">
                <div title={condition.place}>
                  {condition.place}
                </div>
              </div>
              <div className={`font-bold text-lg ${getOperatorColor(condition.operator)} px-2`}>
                {getOperatorSymbol(condition.operator)}
              </div>
              <div className="bg-slate-100 px-2 py-1 rounded text-slate-700 font-mono text-xs font-semibold">
                {typeof condition.value === 'object' 
                  ? JSON.stringify(condition.value) 
                  : String(condition.value)}
              </div>
            </div>
          </div>
        ))}
        
        {data.details.conditions.length > 1 && (
          <div className="flex items-center justify-center mt-3 pt-2 border-t border-amber-200">
            <span className="text-xs text-slate-500 bg-white px-2 py-1 rounded font-semibold">
              {getOperatorSymbol(data.details.operator)} logic
            </span>
          </div>
        )}
      </div>
      
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        className="w-4 h-4 bg-amber-500 border-2 border-white"
      />
      
      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        className="w-4 h-4 bg-amber-500 border-2 border-white"
      />
    </div>
  );
});
