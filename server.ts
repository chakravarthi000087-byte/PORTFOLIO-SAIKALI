import { spawn, type ChildProcess } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import express, { type Request, type Response } from 'express';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = Number(process.env.PORT || 3000);
const PYTHON_PORT = Number(process.env.PYTHON_BACKEND_PORT || 8001);
const PYTHON_ORIGIN = `http://127.0.0.1:${PYTHON_PORT}`;

let pythonProcess: ChildProcess | null = null;
let shuttingDown = false;

function startPythonBackend(): void {
  if (shuttingDown) {
    return;
  }

  pythonProcess = spawn('python3', ['-m', 'backend.local_server', '--port', String(PYTHON_PORT)], {
    cwd: __dirname,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  pythonProcess.stdout?.on('data', (chunk: Buffer) => {
    const line = chunk.toString().trim();
    if (line) {
      console.log(`[python] ${line}`);
    }
  });

  pythonProcess.stderr?.on('data', (chunk: Buffer) => {
    const line = chunk.toString().trim();
    if (line) {
      console.error(`[python:err] ${line}`);
    }
  });

  pythonProcess.on('exit', (code) => {
    pythonProcess = null;
    if (!shuttingDown && code !== 0) {
      console.error(`Python backend exited with code ${code}; restarting in 1s...`);
      setTimeout(startPythonBackend, 1000);
    }
  });
}

async function fetchPythonWithRetry(
  targetUrl: string,
  init: RequestInit,
  attempts = 8,
): Promise<globalThis.Response> {
  let lastError: unknown = null;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fetch(targetUrl, init);
    } catch (err) {
      lastError = err;
      await new Promise((resolve) => setTimeout(resolve, 150));
    }
  }
  throw lastError;
}

function stopPythonBackend(): void {
  shuttingDown = true;
  if (pythonProcess && !pythonProcess.killed) {
    pythonProcess.kill('SIGTERM');
  }
}

process.on('SIGINT', () => {
  stopPythonBackend();
  process.exit(0);
});

process.on('SIGTERM', () => {
  stopPythonBackend();
  process.exit(0);
});

async function bootstrap(): Promise<void> {
  startPythonBackend();

  const app = express();
  app.use(express.raw({ type: '*/*', limit: '1mb' }));

  app.use('/api', async (req: Request, res: Response) => {
    const targetUrl = `${PYTHON_ORIGIN}${req.originalUrl}`;
    try {
      const hasBody = !['GET', 'HEAD', 'OPTIONS'].includes(req.method.toUpperCase());
      const bodyBuffer = hasBody && Buffer.isBuffer(req.body) ? req.body : undefined;
      const upstream = await fetchPythonWithRetry(targetUrl, {
        method: req.method,
        headers: {
          'Content-Type': req.get('content-type') || 'application/json',
        },
        body: bodyBuffer && bodyBuffer.length > 0 ? new Uint8Array(bodyBuffer) : undefined,
      });

      const responseText = await upstream.text();
      res.status(upstream.status);
      const contentType = upstream.headers.get('content-type');
      if (contentType) {
        res.setHeader('Content-Type', contentType);
      }
      res.send(responseText);
    } catch (err) {
      console.error('Python proxy error:', err);
      res.status(502).json({
        ok: false,
        message: 'Python backend service is unavailable.',
      });
    }
  });

  if (process.env.NODE_ENV !== 'production') {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distDir = path.resolve(__dirname, 'dist');
    app.use(express.static(distDir));
    app.get('*', (_req: Request, res: Response) => {
      const indexFile = path.join(distDir, 'index.html');
      if (fs.existsSync(indexFile)) {
        res.sendFile(indexFile);
      } else {
        res.status(404).send('Build output not found. Run npm run build first.');
      }
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Portfolio server running at http://0.0.0.0:${PORT}`);
  });
}

bootstrap().catch((err) => {
  console.error('Failed to start portfolio server:', err);
  stopPythonBackend();
  process.exit(1);
});
