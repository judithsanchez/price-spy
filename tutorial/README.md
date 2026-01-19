# Price Spy Codebase Visual Tutorial

This guide uses Mermaid diagrams to visualize the architecture, data models, and core usage flows of the Price Spy application.

## 1. System Architecture
This high-level view shows the layers of the application and how they interact with external services.

```mermaid
graph TB
    subgraph "Interface Layer"
        CLI["spy.py (CLI tool)"]
        WebServer["FastAPI Web Server"]
        Dashboard["Jinja2 Dashboard UI"]
    end

    subgraph "Core Logic Layer"
        Scheduler["Scheduler (APScheduler)<br/>Daily extraction trigger"]
        Queue["Extraction Queue (Semaphore)<br/>Concurrency & Rate limiting"]
        Browser["Browser Controller<br/>Playwright screenshots"]
        Vision["Vision Engine<br/>Gemini AI Price Extraction"]
        Calculator["Price Calculator<br/>Unit price & Comparisons"]
        EmailReport["Email Reporter<br/>Daily status emails"]
    end

    subgraph "Data Access Layer"
        Repos["Repositories (CRUD)<br/>Encapsulated SQL logic"]
        DB[("SQLite Database<br/>(pricespy.db)")]
    end

    subgraph "External Services"
        Internet["Internet<br/>Product URLs"]
        GeminiAPI["Google Gemini API<br/>Visual LLM"]
        EmailServer["SMTP Server"]
    end

    %% Flow
    CLI --> Repos
    CLI --> Browser
    CLI --> Vision
    
    WebServer --> Repos
    WebServer --> Dashboard
    WebServer --> Queue
    WebServer --> Scheduler
    
    Scheduler --> Queue
    Scheduler --> EmailReport
    
    Queue --> Browser
    Queue --> Vision
    Queue --> Repos
    
    Browser --> Internet
    Vision --> GeminiAPI
    EmailReport --> EmailServer
    EmailReport --> Repos
    
    Repos --> DB
```

## 2. Data Model (ER Diagram)
The database structure is centered around products and stores linked by tracked items.

```mermaid
erDiagram
    PRODUCT ||--o{ TRACKED_ITEM : "to monitor"
    STORE ||--o{ TRACKED_ITEM : "hosts"
    TRACKED_ITEM ||--o{ PRICE_HISTORY : "historical data"
    TRACKED_ITEM ||--o{ EXTRACTION_LOG : "audit trail"
    
    PRODUCT {
        int id PK
        string name
        string category
        float target_price "Alert threshold"
        int current_stock
    }
    
    STORE {
        int id PK
        string name
        float shipping_cost_standard
        float free_shipping_threshold
    }
    
    TRACKED_ITEM {
        int id PK
        int product_id FK
        int store_id FK
        string url
        float quantity_size "e.g. 250"
        string quantity_unit "e.g. ml"
        int items_per_lot "e.g. 6-pack"
        datetime last_checked_at
        bool is_active
    }
    
    PRICE_HISTORY {
        int id PK
        float price
        string currency
        float confidence "LLM confidence"
        string url
        datetime created_at
    }

    EXTRACTION_LOG {
        int id PK
        int tracked_item_id FK
        string status "success/error"
        string model_used "gemini-1.5-* / 2.0-*"
        string error_message
        int duration_ms
    }
```

## 3. Usage Flows

### Adding a New Product
This sequence diagram shows the layers touched when creating a new core product definition.

```mermaid
sequenceDiagram
    autonumber
    participant U as "User (CLI/Web)"
    participant I as "spy.py / app/api/main.py"
    participant M as "app/models/schemas.py (Product)"
    participant R as "app/storage/repositories.py (ProductRepository)"
    participant D as "app/storage/database.py (SQLite)"

    Note over U, D: Usage: Adding a new core product definition

    U->>I: Command: add-product "Coffee"
    I->>M: Instantiate Product schema
    M-->>I: Validated Object
    I->>R: repository.insert(product)
    R->>D: SQL: INSERT INTO products...
    D-->>R: row_id
    R-->>I: product_id
    I-->>U: Success Message "Product added with ID: X"
```

### Tracking a New URL
Linking a specific URL to a product and store.

```mermaid
sequenceDiagram
    autonumber
    participant U as "User (CLI/Web)"
    participant I as "spy.py / app/api/main.py"
    participant R as "app/storage/repositories.py"
    participant M as "app/models/schemas.py"
    participant D as "app/storage/database.py"

    Note over U, D: Usage: Linking a URL to a Product and Store

    U->>I: Command: track --url <URL> --product-id 1 --store-id 1
    I->>R: get_product(1), get_store(1)
    R-->>I: Exists? (Validation)
    I->>M: Instantiate TrackedItem schema
    M-->>I: Validated Object
    I->>R: repository.insert(tracked_item)
    R->>D: SQL: INSERT INTO tracked_items...
    D-->>R: row_id
    R-->>I: item_id
    I-->>U: Success Message "Tracking URL with ID: X"
```

### Price Extraction Flow (Simplified)
The core logic of the application: Browser automation -> Vision AI -> Database storage.

```mermaid
sequenceDiagram
    autonumber
    participant U as "User (CLI/Web)"
    participant I as "spy.py / app/api/main.py"
    participant B as "app/core/browser.py"
    participant V as "app/core/vision.py"
    participant R as "app/storage/repositories.py"
    participant D as "app/storage/database.py"

    Note over U, D: Usage: Extracting price from a URL (Manual or Auto)

    U->>I: Command: extract <URL>
    I->>B: capture_screenshot(url)
    B-->>I: bytes (image content)
    I->>V: extract_product_info(screenshot)
    V->>V: Call Google Gemini API
    V-->>I: ProductInfo (Name, Price, Currency)
    I->>R: repository.insert(PriceHistoryRecord)
    R->>D: SQL: INSERT INTO price_history...
    D-->>R: success
    I-->>U: Display extracted price and comparison
```

### Detailed Price Extraction Lifecycle
A deep dive into the functions, files, and logic phases (Optimized for Dark Mode).

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#1f2937', 'primaryTextColor': '#f3f4f6', 'primaryBorderColor': '#374151', 'lineColor': '#9ca3af', 'secondaryColor': '#111827', 'tertiaryColor': '#1f2937' }}}%%
sequenceDiagram
    autonumber
    
    participant U as "User (CLI/Web)"
    participant Spy as "spy.py"
    participant Browser as "app/core/browser.py"
    participant Vision as "app/core/vision.py"
    participant Gemini as "Google Gemini API"
    participant Calc as "app/core/price_calculator.py"
    participant Repo as "app/storage/repositories.py"
    participant DB as "app/storage/database.py"

    Note over U, DB: Core Journey: Extracting Price from a product URL

    U->>Spy: main() -> cmd_extract(url)
    
    rect rgb(45, 45, 45)
        Note right of Spy: Phase 1: Browser Automation
        Spy->>Browser: capture_screenshot(url)
        Browser->>Browser: async with async_playwright()
        Browser->>Browser: page.goto(url, wait_until='networkidle')
        Browser-->>Spy: returns screenshot (bytes)
    end

    rect rgb(30, 40, 60)
        Note right of Spy: Phase 2: AI Vision Extraction
        Spy->>Vision: extract_with_structured_output(screenshot_bytes, api_key)
        Vision->>Vision: _call_gemini_api(bytes, config)
        Vision->>Gemini: POST /v1beta/models/gemini-1.5-flash:generateContent
        Gemini-->>Vision: returns JSON string
        Vision->>Vision: ExtractionResult.model_validate_json(text)
        Vision-->>Spy: returns (ExtractionResult, model_used)
    end

    rect rgb(30, 60, 40)
        Note right of Spy: Phase 3: Data Processing & Growth
        Spy->>Repo: TrackedItemRepository.get_by_url(url)
        Repo-->>Spy: returns tracked_item data (if any)
        
        Spy->>Calc: calculate_volume_price(price, lot, size, unit)
        Calc-->>Spy: returns unit_price (e.g. 0.45/100ml)
        
        Spy->>Repo: PriceHistoryRepository.get_latest_by_url(url)
        Repo-->>Spy: returns previous_price_record
        
        Spy->>Calc: compare_prices(current, previous)
        Calc-->>Spy: returns PriceComparison (drop detection)
    end

    rect rgb(60, 30, 30)
        Note right of Spy: Phase 4: Persistence
        Spy->>Repo: PriceHistoryRepository.insert(PriceHistoryRecord)
        Repo->>DB: execute("INSERT INTO price_history...")
        DB-->>Repo: row_id
        
        Note right of Spy: Phase 5: Feedback
        Spy-->>U: Print: Product Name, Price, Unit Price, Price Drop?
    end
```

## How to use

If you have the **Mermaid** extension installed in VS Code, these diagrams will render directly in the Markdown preview. You can also copy the ` ```mermaid ` blocks into the [Mermaid Live Editor](https://mermaid.live/).
