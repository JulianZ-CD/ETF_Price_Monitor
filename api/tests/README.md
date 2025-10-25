# Backend Test Suite

✅ **95 tests** | 100% passing | 65 unit + 30 integration

## Quick Start

```bash
# Run all tests
pytest api/tests/

# Run with coverage
pytest api/tests/ --cov=api --cov-report=term

# Run specific type
pytest api/tests/unit/          # Unit tests only
pytest api/tests/integration/   # Integration tests only
```

---

## Test Structure

```
api/tests/
├── conftest.py              # Shared fixtures and test configuration
├── pytest.ini               # Pytest settings
├── test_data/               # Mock data for testing
│   ├── test_prices.csv      # Small price dataset (5 stocks, 5 days)
│   ├── test_etf_valid.csv   # Valid ETF configuration
│   └── test_etf_invalid.csv # Invalid data for error testing
├── unit/                    # Unit tests (65 tests)
│   ├── test_data_loader.py  # DataLoader class (9 tests)
│   ├── test_calculator.py   # ETFCalculator class (17 tests)
│   ├── test_validator.py    # ETFValidator class (22 tests)
│   └── test_etf_parser.py   # ETFDataParser class (17 tests)
└── integration/             # Integration tests (30 tests)
    ├── test_api.py          # API endpoints (14 tests)
    └── test_validation_api.py # API validation (16 tests)
```

---

## Test Coverage

### Unit Tests (65 tests)

#### DataLoader (9 tests)
- Singleton pattern behavior
- DataFrame structure and types
- Data loading and caching
- Available symbols lookup
- Data immutability (copy protection)

#### ETFCalculator (17 tests)
- ETF price calculation accuracy
- Weighted constituent pricing
- Latest price retrieval
- Top holdings ranking
- Edge cases (unknown symbols, missing data)

#### ETFValidator (22 tests)
- Weight sum validation (must equal 1.0 ±0.5%)
- Weight range validation (0 to 1)
- Symbol existence checking
- Duplicate symbol detection (4 tests)
- Empty data handling
- Comprehensive validate_all integration
- Tolerance configuration

#### ETFDataParser (17 tests)
- CSV format parsing and validation
- Required column checking (name, weight)
- Type conversion (weights to float)
- Error handling (malformed CSV, invalid data)
- Edge cases (empty files, whitespace, large datasets)

### Integration Tests (30 tests)

#### API Endpoints (14 tests)
- Successful ETF upload workflow
- Response format validation
- Error handling (malformed CSV, missing columns)
- Health check and CORS
- End-to-end workflow

#### API Validation (16 tests)
- Weight validation at API layer
- Symbol validation with clear errors
- Duplicate symbol rejection
- Empty data rejection
- Multiple error reporting
- Edge cases (zero weights, single constituent)

---

## Key Testing Concepts

### Fixtures (in `conftest.py`)
Reusable test components that provide:
- Mock DataLoader with small test dataset
- Pre-configured ETFCalculator instances
- Sample constituent data
- Test client for API calls

### Mocking Strategy
- **DataLoader**: Uses `test_prices.csv` instead of real data (faster, predictable)
- **Calculator**: Uses mocked DataLoader for isolated testing
- **Validator**: No mocking needed (pure logic, no external dependencies)

### Unit vs Integration
- **Unit**: Test individual classes in isolation (use mocks)
- **Integration**: Test complete workflows with real FastAPI client

---

## Common Commands

```bash
# Verbose output
pytest api/tests/ -v

# Show print statements
pytest api/tests/ -s

# Stop on first failure
pytest api/tests/ -x

# Run specific test
pytest api/tests/unit/test_validator.py::TestWeightSumValidation::test_valid_weight_sum_exactly_one

# Filter by marker
pytest api/tests/ -m unit         # Only unit tests
pytest api/tests/ -m integration  # Only integration tests

# Coverage report
pytest api/tests/ --cov=api --cov-report=html
# Open htmlcov/index.html to view detailed coverage
```

---

## What These Tests Catch

### Problems Found & Fixed
1. ✅ **Unknown symbols**: Now rejected with clear error (was just logged)
2. ✅ **Invalid weights**: Sum must equal 1.0 ±0.5% (was accepted silently)
3. ✅ **Weight range**: Must be 0-1 (negative/over 1 now rejected)
4. ✅ **Empty data**: Now explicitly rejected (was returning zeros)
5. ✅ **Duplicate symbols**: Now detected and rejected with clear error message
6. ✅ **CSV format errors**: Parser validates format before business logic runs

### Services Added
- `ETFValidator` service for comprehensive data quality checks
- `ETFDataParser` service for CSV parsing and format validation
- API-layer validation before processing
- Clear, actionable error messages
- Configurable tolerance (default: 0.5% for floating-point precision)

---

## Best Practices

✅ **DO:**
- Write descriptive test names (`test_calculate_etf_prices_correct_math`)
- Use docstrings to explain what's being tested
- Test both success and failure cases
- Use fixtures to avoid code duplication

❌ **DON'T:**
- Test multiple unrelated things in one test
- Depend on external state or files
- Use magic numbers without explanation
- Skip error messages in assertions

