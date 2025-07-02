import { z } from "zod";

export const TokenValueSchema = z.object({
  value: z.union([z.string(), z.number()]),
});

export const PlaceStateSchema = z.object({
  place: z.string(),
  operator: z.enum([
    "AND",
    "OR", 
    "EQUAL",
    "LESS THAN",
    "GREATER THAN",
    "LESS THAN OR EQUAL",
    "GREATER THAN OR EQUAL",
  ]),
  value: TokenValueSchema,
});

// Supported operands from the Python models
export const SUPPORTED_OPERANDS = [
  "AND",
  "OR",
  "EQUAL",
  "LESS THAN",
  "GREATER THAN",
  "LESS THAN OR EQUAL",
  "GREATER THAN OR EQUAL",
] as const;

export const ConditionSchema = z.object({
  place_state: PlaceStateSchema,
});

export const GuardSchema = z.object({
  conditions: z.array(ConditionSchema),
  conditions_operator: z.enum(["AND", "OR"]),
});

export const PlaceChangeStateSchema = z.object({
  set_value: z.string(),
  to: TokenValueSchema,
});

export const InputArcSchema = z.object({
  place: z.string(),
});

export const OutputArcSchema = z.object({
  place: z.string(),
  token_produced: PlaceChangeStateSchema,
});

export const TransitionSchema = z.object({
  inputs: z.array(InputArcSchema),
  guard: GuardSchema,
  output: OutputArcSchema,
});

export const WorkflowSchema = z.object({
  transition: TransitionSchema,
});

export type TokenValue = z.infer<typeof TokenValueSchema>;
export type PlaceState = z.infer<typeof PlaceStateSchema>;
export type Condition = z.infer<typeof ConditionSchema>;
export type Guard = z.infer<typeof GuardSchema>;
export type PlaceChangeState = z.infer<typeof PlaceChangeStateSchema>;
export type InputArc = z.infer<typeof InputArcSchema>;
export type OutputArc = z.infer<typeof OutputArcSchema>;
export type Transition = z.infer<typeof TransitionSchema>;
export type Workflow = z.infer<typeof WorkflowSchema>;

// Extended types for UI display
export interface WorkflowNode {
  id: string;
  type: 'sensor' | 'guard' | 'command';
  position: { x: number; y: number };
  data: {
    label: string;
    details: Record<string, any>;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  data?: Record<string, any>;
}

export interface ProcessedWorkflow {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  metadata: {
    totalNodes: number;
    sensors: number;
    commands: number;
    conditions: number;
  };
}
