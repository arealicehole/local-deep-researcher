# Research API Contract - Local Deep Researcher

## Overview
API contract for the Local Deep Researcher system, enabling frontend GUIs to interact with the LangGraph-based research backend.

## Base Configuration

```yaml
Base URL: /api/v1
Content-Type: application/json
WebSocket URL: ws://localhost:8000/ws/research
```

## 1. RESTful Endpoints

### Research Operations

```yaml
# Start New Research
POST /api/v1/research
  Body: ResearchRequest
  Response: ResearchResponse (201 Created)
  Description: Initiates a new research session

# Get Research Status
GET /api/v1/research/{sessionId}
  Path param: sessionId (string/UUID)
  Response: ResearchStatusResponse
  Description: Gets current status and progress

# List Research Sessions
GET /api/v1/research
  Query params: 
    - page (int, default: 0)
    - size (int, default: 10)
    - sort (string, default: "createdAt,desc")
  Response: Page<ResearchSummaryResponse>

# Get Research Result
GET /api/v1/research/{sessionId}/result
  Path param: sessionId (string/UUID)
  Response: ResearchResultResponse
  Description: Gets final research markdown with sources

# Cancel Research
DELETE /api/v1/research/{sessionId}
  Path param: sessionId (string/UUID)
  Response: 204 No Content
  Description: Cancels ongoing research

# Export Research
GET /api/v1/research/{sessionId}/export
  Path param: sessionId (string/UUID)
  Query params:
    - format (enum: "markdown", "pdf", "json")
  Response: File download or JSON
```

### Model Management

```yaml
# List Available Models
GET /api/v1/models
  Query params:
    - provider (enum: "ollama", "lmstudio")
  Response: ModelListResponse

# Get Model Info
GET /api/v1/models/{modelName}
  Path param: modelName (string)
  Response: ModelInfoResponse

# Pull Model (Ollama only)
POST /api/v1/models/pull
  Body: ModelPullRequest
  Response: ModelPullResponse
```

### Configuration

```yaml
# Get Current Configuration
GET /api/v1/config
  Response: ConfigurationResponse

# Update Configuration
PUT /api/v1/config
  Body: ConfigurationRequest
  Response: ConfigurationResponse
```

## 2. Request/Response DTOs

### Research DTOs

```typescript
// Request DTO for starting research
interface ResearchRequest {
  topic: string;              // Required, min: 5, max: 500 chars
  maxIterations?: number;     // Optional, default: 3, min: 1, max: 10
  model?: string;            // Optional, defaults to configured model
  searchApi?: "duckduckgo" | "tavily" | "perplexity" | "searxng";
  fetchFullPage?: boolean;   // Optional, default: false
  temperature?: number;      // Optional, 0.0-1.0, default: 0.7
}

// Response when research is initiated
interface ResearchResponse {
  sessionId: string;         // UUID
  status: ResearchStatus;
  topic: string;
  config: {
    maxIterations: number;
    model: string;
    searchApi: string;
  };
  createdAt: string;        // ISO 8601
  estimatedTime?: number;   // Seconds
}

// Status response for ongoing research
interface ResearchStatusResponse {
  sessionId: string;
  status: ResearchStatus;
  currentIteration: number;
  maxIterations: number;
  currentPhase?: ResearchPhase;
  progress: number;         // 0-100
  messages: string[];       // Recent log messages
  updatedAt: string;
}

// Research summary for list view
interface ResearchSummaryResponse {
  sessionId: string;
  topic: string;
  status: ResearchStatus;
  model: string;
  iterations: number;
  duration?: number;        // Seconds
  createdAt: string;
  completedAt?: string;
}

// Final research result
interface ResearchResultResponse {
  sessionId: string;
  topic: string;
  summary: string;          // Markdown content
  sources: SourceInfo[];
  searchQueries: string[];
  iterations: IterationInfo[];
  metadata: {
    model: string;
    totalTokens?: number;
    duration: number;
    searchApi: string;
  };
}

// Enums
enum ResearchStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled"
}

enum ResearchPhase {
  GENERATING_QUERY = "generating_query",
  SEARCHING = "searching",
  SUMMARIZING = "summarizing",
  REFLECTING = "reflecting",
  FINALIZING = "finalizing"
}

// Supporting types
interface SourceInfo {
  title: string;
  url: string;
  snippet: string;
  relevance?: number;      // 0-1
  usedInSummary: boolean;
}

interface IterationInfo {
  iteration: number;
  query: string;
  sourcesFound: number;
  knowledgeGaps?: string[];
  summary?: string;
}
```

### Model Management DTOs

```typescript
interface ModelListResponse {
  provider: "ollama" | "lmstudio";
  models: ModelInfo[];
}

interface ModelInfo {
  name: string;
  size?: number;           // Bytes
  quantization?: string;   // e.g., "Q4_K_M"
  context?: number;        // Context window size
  parameters?: number;     // Parameter count
  loaded?: boolean;
  capabilities?: {
    jsonMode: boolean;
    toolCalling: boolean;
    streaming: boolean;
  };
}

interface ModelPullRequest {
  modelName: string;       // e.g., "llama3.2:latest"
}

interface ModelPullResponse {
  status: "pulling" | "completed" | "failed";
  progress?: number;       // 0-100
  message?: string;
}
```

### Configuration DTOs

```typescript
interface ConfigurationRequest {
  llmProvider?: "ollama" | "lmstudio";
  localLlm?: string;
  maxWebResearchLoops?: number;  // 1-10
  searchApi?: "duckduckgo" | "tavily" | "perplexity" | "searxng";
  fetchFullPage?: boolean;
  ollamaBaseUrl?: string;
  lmstudioBaseUrl?: string;
  stripThinkingTokens?: boolean;
  useToolCalling?: boolean;
  temperature?: number;           // 0.0-1.0
  maxTokens?: number;            // 100-32000
}

interface ConfigurationResponse extends ConfigurationRequest {
  version: string;
  supportedModels: string[];
  availableSearchApis: string[];
}
```

## 3. WebSocket Events

For real-time research progress updates:

```typescript
// Client -> Server
interface WSClientMessage {
  type: "subscribe" | "unsubscribe";
  sessionId: string;
}

// Server -> Client
interface WSServerMessage {
  type: WSEventType;
  sessionId: string;
  data: any;
  timestamp: string;
}

enum WSEventType {
  STATUS_CHANGED = "status_changed",
  ITERATION_STARTED = "iteration_started",
  ITERATION_COMPLETED = "iteration_completed",
  QUERY_GENERATED = "query_generated",
  SEARCH_STARTED = "search_started",
  SEARCH_COMPLETED = "search_completed",
  SOURCES_FOUND = "sources_found",
  SUMMARY_UPDATED = "summary_updated",
  REFLECTION_STARTED = "reflection_started",
  KNOWLEDGE_GAPS = "knowledge_gaps",
  RESEARCH_COMPLETED = "research_completed",
  ERROR = "error"
}

// Event-specific data types
interface IterationStartedData {
  iteration: number;
  maxIterations: number;
}

interface QueryGeneratedData {
  query: string;
  iteration: number;
}

interface SourcesFoundData {
  count: number;
  sources: SourceInfo[];
}

interface SummaryUpdatedData {
  partialSummary: string;
  iteration: number;
}
```

## 4. Error Responses

```json
{
  "timestamp": "2024-01-20T10:30:00Z",
  "status": 400,
  "error": "Bad Request",
  "message": "Validation failed",
  "path": "/api/v1/research",
  "errors": [
    {
      "field": "topic",
      "message": "Topic must be between 5 and 500 characters"
    }
  ]
}
```

### Error Codes

```typescript
enum ErrorCode {
  VALIDATION_ERROR = "VALIDATION_ERROR",
  MODEL_NOT_FOUND = "MODEL_NOT_FOUND",
  MODEL_NOT_LOADED = "MODEL_NOT_LOADED",
  RESEARCH_NOT_FOUND = "RESEARCH_NOT_FOUND",
  RESEARCH_ALREADY_EXISTS = "RESEARCH_ALREADY_EXISTS",
  LLM_CONNECTION_ERROR = "LLM_CONNECTION_ERROR",
  SEARCH_API_ERROR = "SEARCH_API_ERROR",
  RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED",
  INTERNAL_ERROR = "INTERNAL_ERROR"
}
```

## 5. HTTP Status Codes

- **200 OK**: Successful GET, PUT requests
- **201 Created**: Successful POST creating new research
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Validation errors
- **404 Not Found**: Research session or model not found
- **409 Conflict**: Research already in progress for topic
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected server error
- **503 Service Unavailable**: LLM provider not available

## 6. Validation Rules

### Research Topic
- Required
- Length: 5-500 characters
- No special characters that could break markdown

### Model Name
- Must match available models from `/api/v1/models`
- Format: `model:tag` for Ollama (e.g., "llama3.2:latest")

### Iterations
- Range: 1-10
- Default: 3

### Temperature
- Range: 0.0-1.0
- Default: 0.7

### Page Size
- Range: 1-100
- Default: 10

## 7. Authentication & Security

```yaml
Authentication:
  Type: Optional (for local use)
  Method: Bearer token (if enabled)
  Header: Authorization: Bearer {token}

Rate Limiting:
  Research creation: 10 per hour per IP
  Status checks: 60 per minute per session
  
CORS:
  Allowed Origins: 
    - http://localhost:3000 (React)
    - http://localhost:5173 (Vite)
    - http://localhost:8501 (Streamlit)
    - http://localhost:7860 (Gradio)
```

## 8. Implementation Notes

### Backend (Python/FastAPI)

```python
# Use Pydantic for validation
from pydantic import BaseModel, Field, validator

class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=5, max_length=500)
    max_iterations: int = Field(3, ge=1, le=10)
    model: Optional[str] = None
    
    @validator('topic')
    def validate_topic(cls, v):
        # Custom validation logic
        return v

# Async endpoints for LangGraph integration
@app.post("/api/v1/research", status_code=201)
async def start_research(request: ResearchRequest):
    # Invoke LangGraph workflow
    pass

# WebSocket for real-time updates
@app.websocket("/ws/research")
async def websocket_endpoint(websocket: WebSocket):
    # Stream graph events
    pass
```

### Frontend (TypeScript/React)

```typescript
// Zod schemas matching backend validation
import { z } from 'zod';

const ResearchRequestSchema = z.object({
  topic: z.string().min(5).max(500),
  maxIterations: z.number().min(1).max(10).default(3),
  model: z.string().optional(),
});

// TanStack Query hooks
export const useStartResearch = () => {
  return useMutation({
    mutationFn: (data: ResearchRequest) => 
      api.post('/research', data),
  });
};

// WebSocket hook for real-time updates
export const useResearchProgress = (sessionId: string) => {
  // WebSocket connection logic
};
```

## 9. Testing Endpoints

```bash
# Start research
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Impact of AI on education"}'

# Check status
curl http://localhost:8000/api/v1/research/{sessionId}

# Get result
curl http://localhost:8000/api/v1/research/{sessionId}/result
```

## 10. Future Enhancements

- Batch research operations
- Research templates and presets
- Collaborative research sessions
- Research history and versioning
- Custom prompt engineering
- Integration with vector databases
- Research scheduling and automation

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-20  
**Authors**: AI Research Team