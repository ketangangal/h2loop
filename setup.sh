#!/bin/bash
# H2Loop Setup Script
# This script sets up the development environment for the H2Loop project

set -e  # Exit on error

echo "🚀 H2Loop Setup Script"
echo "======================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"
echo ""

# Check if Node.js is installed
echo -e "${BLUE}Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js is not installed. Please install Node.js 18 or higher.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
echo -e "${GREEN}✓ npm found: $(npm --version)${NC}"
echo ""

# Setup Backend
echo -e "${BLUE}Setting up Backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
deactivate

cd ..
echo ""

# Setup Frontend
echo -e "${BLUE}Setting up Frontend...${NC}"
cd frontend

# Install npm dependencies
echo "Installing npm dependencies..."
npm install
echo -e "${GREEN}✓ npm dependencies installed${NC}"

cd ..
echo ""

# Create .env.example files if they don't exist
echo -e "${BLUE}Setting up environment files...${NC}"

if [ ! -f "backend/.env.example" ]; then
    cat > backend/.env.example << 'EOF'
# Azure OpenAI Configuration (Optional - uses stub if not configured)
AZURE_API_KEY=your-api-key-here
AZURE_API_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_DEPLOYMENT=your-deployment-name
AZURE_API_VERSION=2024-06-01
EOF
    echo -e "${GREEN}✓ Created backend/.env.example${NC}"
fi

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠ Created backend/.env - Please update with your Azure OpenAI credentials${NC}"
else
    echo -e "${GREEN}✓ backend/.env already exists${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo -e "1. Configure Azure OpenAI (optional):"
echo -e "   ${YELLOW}nano backend/.env${NC}"
echo ""
echo -e "2. Start the backend server:"
echo -e "   ${YELLOW}cd backend && source .venv/bin/activate && python main.py${NC}"
echo ""
echo -e "3. In a new terminal, start the frontend:"
echo -e "   ${YELLOW}cd frontend && npm run dev${NC}"
echo ""
echo -e "4. Open your browser:"
echo -e "   ${YELLOW}http://localhost:5173${NC}"
echo ""
echo -e "${BLUE}Convenience scripts:${NC}"
echo -e "   ${YELLOW}./run-backend.sh${NC}  - Start backend server"
echo -e "   ${YELLOW}./run-frontend.sh${NC} - Start frontend dev server"
echo -e "   ${YELLOW}./run-all.sh${NC}      - Start both servers"
echo ""

