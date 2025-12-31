#!/bin/bash
# Check if all required tools are installed

echo "🔍 H2Loop Requirements Check"
echo "============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ALL_OK=true

# Check Python
echo -n "Python 3.8+: "
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Found $VERSION${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ALL_OK=false
fi

# Check Node.js
echo -n "Node.js 18+: "
if command -v node &> /dev/null; then
    VERSION=$(node --version)
    echo -e "${GREEN}✓ Found $VERSION${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ALL_OK=false
fi

# Check npm
echo -n "npm:         "
if command -v npm &> /dev/null; then
    VERSION=$(npm --version)
    echo -e "${GREEN}✓ Found v$VERSION${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    ALL_OK=false
fi

# Check mmdc (optional)
echo -n "mmdc:        "
if command -v mmdc &> /dev/null; then
    echo -e "${GREEN}✓ Found (Mermaid validation will work)${NC}"
else
    echo -e "${YELLOW}⚠ Not found (Mermaid validation will be skipped)${NC}"
    echo "           Install with: npm install -g @mermaid-js/mermaid-cli"
fi

echo ""

if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✓ All required dependencies are installed!${NC}"
    echo ""
    echo "Run './setup.sh' to set up the project."
else
    echo -e "${RED}✗ Some required dependencies are missing.${NC}"
    echo ""
    echo "Please install:"
    echo "  - Python 3.8+: https://www.python.org/downloads/"
    echo "  - Node.js 18+: https://nodejs.org/"
    exit 1
fi


