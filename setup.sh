#!/bin/bash

# Setup script for Indian Market Analysis Application

echo "=========================================="
echo "Indian Market Analysis - Setup"
echo "=========================================="

# Check Python version
echo ""
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ $PYTHON_VERSION"
else
    echo "   ✗ Python 3 not found"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "2. Creating virtual environment..."
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo ""
    echo "2. Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "3. Activating virtual environment..."
source venv/bin/activate
echo "   ✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "4. Upgrading pip..."
pip install --upgrade pip --quiet
echo "   ✓ pip upgraded"

# Install dependencies
echo ""
echo "5. Installing dependencies..."
echo "   (This may take a few minutes...)"
pip install -r requirements.txt --quiet
echo "   ✓ Dependencies installed"

# Check if .env exists
echo ""
echo "6. Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "   → Copying .env.example to .env"
    cp .env.example .env
    echo "   ⚠  Please edit .env with your database credentials"
else
    echo "   ✓ .env file exists"
fi

# Check if TA-Lib is installed
echo ""
echo "7. Checking TA-Lib..."
if python3 -c "import talib" 2>/dev/null; then
    echo "   ✓ TA-Lib is installed"
else
    echo "   ✗ TA-Lib not installed"
    echo ""
    echo "   Please install TA-Lib system package:"
    echo "   macOS:   brew install ta-lib"
    echo "   Ubuntu:  sudo apt-get install ta-lib"
    echo ""
    echo "   Then run: pip install TA-Lib"
fi

# Run test
echo ""
echo "8. Running setup test..."
python3 test_setup.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Install TA-Lib if not already installed (see above)"
echo "2. Edit .env with your PostgreSQL credentials"
echo "3. Run: python3 scripts/setup_db.py"
echo "4. Run: python3 scripts/seed_nifty50.py"
echo "5. Run: streamlit run src/presentation/streamlit_app/app.py"
echo ""
echo "Or simply run:"
echo "   source venv/bin/activate"
echo "   streamlit run src/presentation/streamlit_app/app.py"
