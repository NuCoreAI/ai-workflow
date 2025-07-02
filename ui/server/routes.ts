import type { Express } from "express";
import { createServer, type Server } from "http";
import path from "path";
import express from "express";

export async function registerRoutes(app: Express): Promise<Server> {
  // Serve static assets including workflow.json
  app.use('/assets', express.static(path.join(process.cwd(), 'client/public/assets')));

  // API endpoint to get workflow data
  app.get('/api/workflow', async (req, res) => {
    try {
      const workflowPath = path.join(process.cwd(), 'client/public/assets/workflow.json');
      const fs = await import('fs/promises');
      const data = await fs.readFile(workflowPath, 'utf-8');
      const workflow = JSON.parse(data);
      res.json(workflow);
    } catch (error) {
      console.error('Error loading workflow:', error);
      res.status(500).json({ 
        error: 'Failed to load workflow data',
        message: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  // Health check endpoint
  app.get('/api/health', (req, res) => {
    res.json({ 
      status: 'ok', 
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    });
  });

  const httpServer = createServer(app);

  return httpServer;
}
