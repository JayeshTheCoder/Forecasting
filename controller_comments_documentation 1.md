# Controller Comments - AI-Powered Financial Analysis System

## Executive Summary

The **Controller Comments** module is an Agentic AI-based system designed to automate the generation of financial controller commentary for enterprise performance metrics. It extracts data from various ERP systems (SAP, BI, Hyperion) via CSV/Excel files or direct database connections, processes it through AI agents, and generates insightful financial narratives that explain company performance across key business dimensions.

### Business Value
- **Reduces manual effort**: Eliminates hours of manual data analysis in SAP and other sources
- **Ensures consistency**: Standardized commentary format across all metrics and periods
- **Improves accuracy**: AI-powered analysis reduces human error in variance calculations
- **Enables scalability**: Supports multiple currencies, periods (MOM/QTD), and organizational structures

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA INPUT LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  CSV/Excel Mode                    │    Database Mode (SQL Server/MySQL)    │
│  ─────────────                     │    ─────────────────────────────────   │
│  • SAP Extracts                    │    • Raw_Sales_Data                    │
│  • BI Reports                      │    • Raw_PEX_Data                      │
│  • Hyperion Files                  │    • Raw_C1_Data                       │
│                                    │    • Raw_OrderEntry_Data               │
│                                    │    • Raw_WC_*_Data                     │
└────────────────┬───────────────────┴──────────────────┬─────────────────────┘
                 │                                      │
                 ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TOOL FACTORY & CONFIGURATION                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Sales      │  │    PEX       │  │     C1       │  │  Order Entry │    │
│  │  Analysis    │  │  Analysis    │  │  Analysis    │  │  Analysis    │    │
│  │   Tool       │  │   Tool       │  │   Tool       │  │   Tool       │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Working Capital Analysis Tool                    │   │
│  │  • AR Aging Analysis  • DSO Analysis  • ITO Analysis  • Inventory   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Supporting Components:                                                    │
│  • threshold_config.py - Pydantic-based threshold validation              │
│  • currency_utils.py   - Multi-currency forex conversion                  │
│  • database_manager.py - Singleton DB connection with retry logic         │
└─────────────────────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CREWAI AGENT ORCHESTRATION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ANALYST AGENT (Per Metric)                       │   │
│  │  • Executes the analysis tool                                       │   │
│  │  • Receives JSON output with calculations                           │   │
│  │  • Generates structured financial commentary                        │   │
│  │  • Follows strict template patterns                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EDITOR AGENT (Per Metric)                        │   │
│  │  • Refines grammar and professional tone                            │   │
│  │  • Adds executive summary                                           │   │
│  │  • Validates against business rules                                 │   │
│  │  • Ensures numerical fidelity                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Process: Sequential (Analysis → Editing)                                  │
│  LLM: Azure OpenAI (GPT-4.1 / o3-mini for planning)                        │
└─────────────────────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT GENERATION                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Professional Financial Controller Commentary                            │
│  • Executive Summary                                                       │
│  • Detailed Variance Analysis                                              │
│  • Hierarchical Breakdown (Division → DPC → SBU/SPG)                       │
│  • Formatted with $XXX (YYY% vs PY) pattern                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Supported Metrics

### 1. Sales Analysis
**Purpose**: Analyze sales performance across divisions, DPCs, SBUs, channels, and customer segments.

**Input Files**: Single CSV with columns:
- `P1-Division`, `P2-DPC`, `P3-SBU`, `P4-SPG`
- `Customer Group`, `Distribution Channel`, `Holding`
- `Product/Service`, `Sales doc. type`
- Sales columns (CY/PY format)

**Key Features**:
- Division-level analysis (LAB, IND, PI, RET, PRO)
- DPC drill-down with threshold filtering
- SBU/SPG contributor analysis
- Channel and customer segmentation
- Special handling for Retail (no DPC) and T&L (no channel)

**Analysis Tool**: `SalesAnalysisTool`
**Controller**: `SalesCrewController`

---

### 2. PEX (Personnel Expenses) Analysis
**Purpose**: Comprehensive analysis of period expenses with vendor and headcount integration.

**Input Files**: 3 Excel files
1. **PEX Data**: Cost elements, functional areas, current/previous year amounts
2. **Vendor Data**: Vendor names, offsetting accounts, variance amounts
3. **Headcount Data**: Department-level FTE counts and variances

**Key Features**:
- 17 expense categories (Base Compensation, Social Costs, T&E, etc.)
- Vendor analysis for material expense categories
- FTE/headcount integration for personnel categories
- Category ordering by business importance
- Cost element and functional area breakdowns

**Analysis Tool**: `PEXDataTool`
**Controller**: `PEXCrewController`

---

### 3. C1 (Contribution Margin Level 1) Analysis
**Purpose**: Analyze C1 margin performance with mix impact and price realization.

**Input Files**: 2 Excel files (for MO organizations)
1. **Main C1 Data**: Sales, C1 amounts by hierarchy (Division, DPC, SBU, SPG)
2. **PR Data**: Price realization weighted sales data

**Key Features**:
- BPS (basis points) variance analysis
- Sales mix impact calculation
- Price realization (PR) reporting
- MO (Marketing Org) vs PO (Purchasing Org) modes
- Cost driver analysis for PO organizations
- Low margin checks with product/customer details

**Analysis Tool**: `C1FinancialAnalysisToolNew`
**Controller**: `C1CrewController`

---

### 4. Order Entry Analysis
**Purpose**: Analyze order entry/bookings performance similar to sales analysis.

**Input Files**: Single CSV with order entry columns

**Key Features**:
- Same hierarchical structure as Sales
- Division → DPC → SBU/SPG → Channel → Customer
- Special handling for Retail and T&L divisions
- Triple collapse mode for single-product structures

**Analysis Tool**: `OrderEntryAnalysisTool`
**Controller**: `OrderEntryCrewController`

---

### 5. Working Capital Analysis
**Purpose**: Comprehensive working capital metrics analysis.

**Input Files**: 4 Excel files
1. **AR Aging**: Accounts receivable aging buckets
2. **DSO**: Days Sales Outstanding calculations
3. **ITO**: Inventory Turnover metrics
4. **Inventory**: Inventory levels by category

**Key Features**:
- Past due AR > 30 days analysis
- DSO L3M (Last 3 Months) trends
- LTM ITO (Last 12 Months) analysis
- Inventory MoM variance by category
- Customer-level AR analysis

**Analysis Tool**: `WorkingCapitalAnalysisTool`
**Controller**: `WorkingCapitalCrewController`

---

## Code Structure

```
functions/controller_comments/
│
├── __init__.py                          # Module initialization
│
├── core/                                # Core infrastructure
│   ├── __init__.py
│   ├── database_manager.py              # Singleton DB manager with retry logic
│   └── state_schemas.py                 # (For LangGraph migration)
│
├── sales/                               # Sales Analysis
│   ├── __init__.py
│   ├── SalesAnalysisTool.py             # Main analysis tool (~1500 lines)
│   ├── sales_crew_controller.py         # CrewAI controller (~1000 lines)
│   └── sales_langgraph_controller.py    # (Future: LangGraph version)
│
├── pex/                                 # PEX Analysis
│   ├── __init__.py
│   ├── pex_analysis_tool.py             # PEX + Vendor + Headcount tool (~1400 lines)
│   ├── pex_crew_controller.py           # CrewAI controller (~880 lines)
│   └── pex_langgraph_controller.py      # (Future: LangGraph version)
│
├── c1/                                  # C1 Analysis
│   ├── __init__.py
│   ├── C1FinancialAnalysisToolNew_v2_SSI.py  # Main C1 tool (~2000+ lines)
│   ├── c1_crew_controller.py            # CrewAI controller (~920 lines)
│   ├── c1_config.py                     # Configuration classes
│   ├── c1_core.py                       # Core calculation utilities
│   ├── c1_dpc_config.py                 # DPC-specific configurations
│   ├── c1_po_workflow.py                # Purchasing org cost workflow
│   └── c1_langgraph_controller.py       # (Future: LangGraph version)
│
├── orderentry/                          # Order Entry Analysis
│   ├── __init__.py
│   ├── OrderEntryAnalysisTool.py        # Order entry tool (~800 lines)
│   ├── order_entry_crew_controller.py   # CrewAI controller (~1000 lines)
│   └── order_entry_langgraph_controller.py  # (Future: LangGraph version)
│
├── workingcapital/                      # Working Capital Analysis
│   ├── __init__.py
│   ├── WorkingCapitalAnalysisTool.py    # 4-file WC tool (~1200 lines)
│   ├── WorkingCapitalAnalysisToolnothresh.py  # No-threshold version
│   ├── working_capital_crew_controller.py  # CrewAI controller (~435 lines)
│   └── working_capital_langgraph_controller.py  # (Future: LangGraph version)
│
├── tool_factory.py                      # Centralized tool creation factory
├── threshold_config.py                  # Pydantic threshold configurations
├── currency_utils.py                    # Forex rate and currency conversion
├── currency_optimization_mixin.py       # Currency optimization for tools
├── status_messages.py                   # Standardized status messaging
├── metrics_tracker.py                   # Token usage tracking
│
└── db/                                  # Database setup
    ├── schema.sql                       # SQL schema for DB mode
    └── setup_local_mysql.py             # Local DB setup script
```

---

## Key Components Deep Dive

### 1. Tool Factory (`tool_factory.py`)

The Tool Factory implements the **Factory Pattern** to create appropriately configured tools based on:
- **Metric Type**: Sales, PEX, C1, Order Entry, Working Capital
- **Threshold Mode**: With thresholds vs Without thresholds
- **Period Type**: MOM (Month-over-Month) vs QTD (Quarter-to-Date)
- **Currency**: USD or local currency with conversion
- **Organization Type**: MO (Marketing) or PO (Purchasing) - for C1 only

```python
# Example usage
from functions.controller_comments.tool_factory import get_controller_with_tool

controller = get_controller_with_tool(
    metric_type="Sales Analysis",
    use_thresholds=True,
    period_type="MOM",
    currency="EUR"
)
```

### 2. Threshold Configuration (`threshold_config.py`)

Uses **Pydantic** for immutable, validated threshold configurations:

**Sales Thresholds** (example):
- LAB Division: Labtec ($300K, 10%), Pipettes ($200K, 10%), etc.
- IND Division: $450K, 10%
- PI Division: $450K, 20%
- RET Division: $250K, 15%
- PRO Division: $250K, 10%

**PEX Thresholds**:
- Variance threshold: $90,000
- Percentage threshold: 3%
- Vendor materiality: 2% of category

**QTD Multiplier**: 3x MOM amounts for quarter-to-date analysis

### 3. Currency Utilities (`currency_utils.py`)

**Features**:
- Forex rate loading from `forex_rates.json`
- Thread-safe caching with 1-hour TTL
- Threshold pre-conversion and caching
- 28 supported currencies (USD, EUR, GBP, JPY, INR, etc.)
- Performance monitoring (<100ms requirement)

**Conversion Logic**:
```
converted_threshold = usd_threshold * forex_rate
```

**Cache Architecture**:
- `ForexRateCache`: Caches forex rates
- `ThresholdCache`: Caches pre-converted thresholds

### 4. Database Manager (`database_manager.py`)

**Singleton Pattern** with:
- Connection pooling (5 connections, max 10 overflow)
- Retry logic with exponential backoff (3 attempts)
- Health check (`ping()` method)
- Flexible date matching (exact → month → global fallback)

**Supported Tables**:
- `Dim_Unit`: Business unit dimension
- `Raw_Sales_Data`: Sales fact data
- `Raw_OrderEntry_Data`: Order entry fact data
- `Raw_C1_Data`, `Raw_C1_PR_Data`: C1 data
- `Raw_PEX_Data`, `Raw_PEX_Vendor_Data`, `Raw_PEX_Headcount_Data`: PEX data
- `Raw_WC_*_Data`: Working capital data

**Data Source Mode**:
- `DATA_SOURCE_MODE=CSV`: File-based input (legacy)
- `DATA_SOURCE_MODE=DB`: Database-driven input

### 5. Status Messages (`status_messages.py`)

Centralized status messaging with emoji support for UI consistency:
- Initialization stages: 🚀 Initializing
- Analysis stages: 🔍 Analyzing, 📊 Processing
- Agent stages: 🤖 AI Agents Active, 🧠 Planning
- Completion: ✅ Analysis Complete
- Errors: ❌ Error Occurred

---

## Agent Architecture

### Current: CrewAI Implementation

Each metric controller creates 2 agents:

#### Agent 1: Analyst Agent
```python
Agent(
    role="Sales Analysis Controller",  # Or metric-specific role
    goal="Execute tool and generate detailed financial commentary",
    backstory="Expert financial analyst with tool execution capabilities",
    tools=[analysis_tool],  # The specific metric tool
    llm=azure_llm,
    allow_delegation=False,
    reasoning=True,
    max_reasoning_attempts=3
)
```

#### Agent 2: Editor Agent
```python
Agent(
    role="Senior Financial Editor",
    goal="Refine language, add executive summary, ensure professional tone",
    backstory="Seasoned editor from top-tier financial publication",
    llm=azure_llm,
    allow_delegation=False
)
```

### Task Flow
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Analysis Task  │────▶│   Crew Execute  │────▶│  Editing Task   │
│                 │     │                 │     │                 │
│ • Execute tool  │     │ • Agent 1 runs  │     │ • Refine output │
│ • Generate JSON │     │ • Generate text │     │ • Add summary   │
│ • Create comm.  │     │ • Pass context  │     │ • Polish tone   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Final Output   │
                                               └─────────────────┘
```

### Future: LangGraph Migration

The codebase includes placeholder files for LangGraph migration:
- `*_langgraph_controller.py` files exist but are not yet implemented
- LangGraph will provide more explicit state management
- Better control flow for complex multi-step analysis
- Improved observability and debugging

---

## Data Flow

### CSV/Excel Mode

```
1. User uploads CSV/Excel files via Streamlit UI
2. Controller validates file existence and format
3. Tool loads data using pandas
4. Tool performs calculations and aggregations
5. Tool applies threshold filters (if enabled)
6. Tool generates structured JSON output
7. Analyst Agent receives JSON and generates commentary
8. Editor Agent refines commentary
9. Final output returned to user
```

### Database Mode

```
1. User selects Unit and Date from UI
2. DatabaseManager fetches data from appropriate tables
3. Tool processes DataFrame (same as CSV mode)
4. Remaining flow identical to CSV mode
5. Benefits: No file uploads, centralized data, better security
```

---

## Commentary Templates

### Sales/Order Entry Template Structure
```
## Overall Sales Summary
During [Month Year], Sales totaled $X (+Y% vs PY), with Product Sales at $A (+B% vs PY) 
and Service Sales at $C (+D% vs PY). Product performance was driven by...

A. Product Level Commentary

A.0 Product Level Summary:
Product performance shows variance of $X (+Y% vs PY).

**Contributing Divisions**: [Division contributors]

    A.1 [Division Name]:
    The [Division] division reported variance of $X (+Y% vs PY).
    
    **Contributing DPCs**: [DPC contributors]
    **Impacting SBUs**: [SBU contributors]
    
        A.1.X.1 [DPC Name]:
        The [DPC] DPC resulted in change of $X (+Y% vs PY).
        
        A.1.X.1.1 SBU: [SBU contributors/offsetters]
        A.1.X.1.2 Channel: [Channel analysis]
        A.1.X.1.3 Customer Segmentation: [Segment analysis]

B. Service Level Commentary (if applicable)
```

### PEX Template Structure
```
**Summary**
PEX excluding bonuses and commissions totaled $X, [increasing/decreasing] by $Y (Z% vs PY) 
compared to previous year, primarily due to...

**Comprehensive Period Expense Analysis - [Month]**

**Base Compensation**
Base compensation [increased/decreased] by $X (Y% vs PY), representing a Z% [rise/decline] 
compared to the previous year. This [increase/decrease] was primarily driven by...

**Social Costs / Benefits**
[Similar structure with FTE data if available]

**[Other Categories]**
...
```

### C1 Template Structure
```
C1 Commentary: [ENTITY_NAME]

Summary Commentary:
Total C1 Margin was X% (vs Y% PY), representing a [increase/decrease] of Z bps vs PY, 
with [favorable/unfavorable] mix impact of W bps. Price Realization for Product was V bps.

Summary: [Division Name]
[Division] Division C1 Margin totaled X% (vs Y% PY), [increasing/decreasing] by Z bps vs PY 
with [favorable/unfavorable] mix impact of W bps.

Details: [DPC Name] DPC
[DPC] DPC C1 Margin totaled X% (vs Y% PY), [increasing/decreasing] by Z bps vs PY.

SBU Drivers:
[Favorable/Unfavorable] mix impact of X bps led by [increase/decrease] in [SBU] sales (+Y% vs PY)...

Low Margin Check:
- Products with Low Margins: [Product] (Sales: $X, C1: Y.Y%)
- Customer Segments: [Segment] (Sales: $X, C1: Y.Y%)
- Key Customers: [Customer] (Sales: $X, C1: Y.Y%)
```

---

## Configuration

### Environment Variables
```bash
# Database Connection (for DB mode)
DB_CONNECTION_STRING="mysql+pymysql://user:pass@host:port/dbname"

# Data Source Mode
DATA_SOURCE_MODE="CSV"  # or "DB"

# Azure OpenAI (for CrewAI)
AZURE_OPENAI_ENDPOINT="https://..."
AZURE_OPENAI_API_KEY="..."
AZURE_OPENAI_DEPLOYMENT="gpt-4.1"
```

### Forex Rates Configuration
File: `functions/controller_comments/forex_rates.json`
```json
{
  "rates": {
    "USD": 1.0,
    "EUR": 0.9240,
    "GBP": 0.7890,
    "INR": 83.6523,
    "JPY": 148.50
  },
  "metadata": {
    "last_updated": "2025-01-15",
    "source": "ECB"
  }
}
```

---

## Development Guidelines

### Adding a New Metric

1. **Create Tool Class**:
   - Inherit from `crewai.tools.BaseTool`
   - Define `name`, `description`, `args_schema`
   - Implement `_run()` method returning JSON

2. **Create Controller**:
   - Initialize 2 agents (Analyst + Editor)
   - Create analysis task with detailed prompt
   - Create editing task
   - Implement async/sync execution methods

3. **Register in Tool Factory**:
   - Add factory method for tool creation
   - Add controller creation method
   - Update `get_tool_info()`

4. **Add Thresholds** (if applicable):
   - Create Pydantic model in `threshold_config.py`
   - Add factory configurations
   - Add convenience function

### Testing

```python
# Test tool directly
tool = SalesAnalysisTool()
result = tool._run(file_path="test.csv")

# Test controller
controller = SalesCrewController()
result, tokens = controller.run_analysis_sync(
    file_path="test.csv",
    month="January 2025"
)
```

---

## Migration Notes

### CrewAI → LangGraph

The project is preparing for migration to LangGraph for better:
- State management
- Observability
- Control flow
- Debugging capabilities

Current placeholder files:
- `sales_langgraph_controller.py`
- `pex_langgraph_controller.py`
- `c1_langgraph_controller.py`
- `order_entry_langgraph_controller.py`
- `working_capital_langgraph_controller.py`

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "File not found" | Check file path, ensure file exists before controller call |
| "Invalid currency" | Verify currency code in `ALLOWED_CURRENCIES` |
| "Database connection failed" | Check `DB_CONNECTION_STRING`, ensure SQLAlchemy installed |
| "Threshold not applied" | Verify threshold config passed to tool factory |
| "Empty commentary" | Check if input data has values above threshold |
| "Token limit exceeded" | Reduce input data size or use smaller model |

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## License

Internal use only - Mettler Toledo AI Tools Platform

## Authors

AI Tools Platform Team

---

*Document Version: 1.0*
*Last Updated: January 2026*
