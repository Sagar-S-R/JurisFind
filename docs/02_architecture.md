# JurisFind: End-to-End User Data Flows
**Scope:** Complete interaction mapping from Frontend UI $\rightarrow$ Backend API $\rightarrow$ Database/AI $\rightarrow$ UI State.

This document traces exactly what happens to data under the hood for every major user action in the JurisFind platform.

---

## Flow 1: Global Semantic Search
*User action: User types a legal query (e.g., "Medical negligence cases") in `SearchPage.jsx` and clicks Search.*

1.  **Frontend State:** React updates the `query` state variable.
2.  **API Client:** Calls `casesApi.search(query, token, 10)` which sends a `POST /api/search` request with a JSON body.
3.  **Backend Route:** `search_router.search` (`backend/app/api/routes/search.py`) validates the input.
4.  **Service Layer:** Passes the query to `QdrantSearchService.search`.
5.  **AI Embedding:** The text is passed to `_embed()`, which uses the local CPU singleton `SentenceTransformer("all-mpnet-base-v2")` to generate a 768-dimensional float array.
6.  **Vector Search (Qdrant):** The vector is sent to the Qdrant database (running on port 6333) via `client.query_points`. Qdrant returns the raw chunk hits.
7.  **Hydration (PostgreSQL):** The service groups the chunk hits by `document_id`. It then executes a bulk SQL query against the `legal_documents` table to retrieve full metadata (title, court, year, etc.) for those specific IDs.
8.  **Response:** Backend returns a structured JSON `SearchResponse`.
9.  **Frontend Render:** React receives the JSON, updates the `results` array, and renders the case cards displaying the similarity percentage and context snippets.

---

## Flow 2: "Analyze in Assistant"
*User action: User clicks the "Analyze in Assistant" button on a specific search result card in `SearchPage.jsx`.*

1.  **API Client:** Calls `casesApi.analyze(caseId, token)`.
2.  **Backend Route:** `POST /api/cases/{case_id}/analyze` (`cases.py`).
3.  **Database Lookup (PostgreSQL):** 
    *   Backend checks if this specific case already exists in the `documents` table (which holds pgvector data).
    *   If it doesn't exist, it creates a new `Document` record with `source_type="legal_case"` and points to the local PDF path.
4.  **Celery Ingestion (Async):** If the document is new or not "ready", it fires `process_document_task.delay(doc_id, path)` to RabbitMQ so the worker can chunk and embed the case into `pgvector` for RAG.
5.  **Session Creation:** Backend creates a new `AssistantSession` in the database.
6.  **Attachment:** Backend creates a `SessionDocument` link, attaching the case to the new session.
7.  **Response:** Returns `{ session_id, document_id }`.
8.  **Frontend Navigation:** React Router intercepts the response and forcefully navigates the user to `/chat/{session_id}` to begin chatting.

---

## Flow 3: Uploading a Private PDF
*User action: User clicks the paperclip icon in `AssistantPage.jsx`, selects a PDF from their computer, and hits the Send button.*

1.  **Frontend Staging:** The file is temporarily held in React state (`stagedFile`).
2.  **Upload API:** On submit, `docsApi.upload` sends a `multipart/form-data` request to `POST /api/documents/upload`.
3.  **Backend Persistence:** 
    *   `BlobStorageService` saves the raw byte stream to disk (`backend/data/uploaded_documents/...`).
    *   Creates a `Document` record in PostgreSQL with `owner_id = current_user.id`.
4.  **Async Processing Trigger:** Dispatches `process_document_task` to the Celery worker.
5.  **Frontend Linking:** The API returns the new `document.id`. The frontend immediately calls `POST /api/sessions/{session_id}/documents` to link the new document to the active chat session.
6.  **Celery Pipeline (Background):**
    *   `PyMuPDF` extracts text and page numbers.
    *   `LangChain` chunks the text (1000 chars).
    *   `SentenceTransformers` embeds the chunks on the CPU.
    *   Chunks and Vectors are bulk-inserted into PostgreSQL (`pgvector`).
    *   Groq API generates a summary.
    *   Document status updates to `ready`.
7.  **Frontend Polling/Update:** The UI eventually reflects that the document is ready for chatting.

---

## Flow 4: Chatting with Documents (RAG Flow)
*User action: User types a question in an active session with attached documents and hits enter (`AssistantPage.jsx`).*

1.  **Frontend Request:** Calls `sessionsApi.sendMessageStream`, sending `POST /api/sessions/{session_id}/messages`.
2.  **State Save:** Backend saves the user's raw message to the `messages` table in PostgreSQL.
3.  **Context Check:** Backend checks the `session_documents` table and sees documents are attached. It routes to the **RAG Path**.
4.  **Retrieval Service:** 
    *   Embeds the user's question to a 768-dim vector.
    *   Executes a raw SQL `pgvector` query: `ORDER BY embedding <=> :query_vec`.
    *   **Crucial Filter:** Constrains the search using `WHERE document_id = ANY(:attached_doc_ids)`.
5.  **Prompt Assembly:** The top 8 returned chunks (with their page numbers and titles) are formatted into a large context string block.
6.  **LLM Streaming (Groq):** The backend opens a connection to Groq (`llama-3.3-70b-versatile`), passing the context, the last 6 chat messages, and the user's prompt.
7.  **SSE Response:** FastAPI yields text chunks back to the frontend using Server-Sent Events (`data: {"content": "..."}`).
8.  **Frontend Render:** React state updates continuously, creating a "typing" effect on screen.
9.  **Wrap-up:** Once Groq finishes, the backend yields a final `event: citations` payload so the UI can render clickable source pills. The backend then saves the final AI answer to the `messages` table.

---

## Flow 5: General Chat (No Documents)
*User action: User creates a "New Chat", attaches no files, types a question, and hits enter.*

1.  **Frontend Request:** Same as Flow 4 (`POST /api/sessions/{session_id}/messages`).
2.  **Context Check:** Backend checks `session_documents`, sees it is empty. Routes to the **General Chatbot Path**.
3.  **Domain Guardrail:** `LegalChatbotAgent` checks if the question is legally relevant using a lightweight classification prompt.
    *   *If non-legal:* Rejects the prompt ("I am a specialized legal assistant...") and saves to DB.
4.  **LLM Streaming:** If valid, the system prompt instructs the AI to act as an expert on Indian law. It calls Groq without any RAG context.
5.  **Response & Render:** Streams the response via SSE exactly like Flow 4, but without citation events at the end.

---

## Flow 6: Viewing / Downloading a PDF
*User action: User clicks "View PDF" or "Download" on a citation pill or document card.*

1.  **Frontend Action:** An `<a>` tag or `<iframe>` is triggered with the URL `/api/search/pdf/{document_id}` (for corpus cases) or `/api/documents/{id}/pdf` (for user uploads).
2.  **Backend Route:** 
    *   Backend receives the UUID, queries PostgreSQL to find the actual local filename.
    *   Constructs the absolute path to `backend/data/pdfs/` or the uploaded documents folder.
3.  **Response:** Returns a `FileResponse`.
    *   For **Viewing**: Header is set to `Content-Disposition: inline`, allowing the browser (or React `PdfViewerModal` iframe) to render it natively.
    *   For **Downloading**: The frontend forces a download using the HTML5 `download` attribute on the anchor tag.
