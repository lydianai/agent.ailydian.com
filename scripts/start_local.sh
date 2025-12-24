#!/bin/bash
#
# Local Development Startup Script
#
# This script starts all required services for local development.
#

set -e  # Exit on error

echo "🏥 Healthcare-AI-Quantum-System - Local Startup"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Start databases and infrastructure
echo ""
echo "📦 Starting infrastructure services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check PostgreSQL
echo "   Checking PostgreSQL..."
until docker exec healthcare-ai-postgres pg_isready -U healthcare_admin > /dev/null 2>&1; do
    echo "   ⏳ Waiting for PostgreSQL..."
    sleep 2
done
echo "   ✅ PostgreSQL ready"

# Check MongoDB
echo "   Checking MongoDB..."
until docker exec healthcare-ai-mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    echo "   ⏳ Waiting for MongoDB..."
    sleep 2
done
echo "   ✅ MongoDB ready"

# Check Redis
echo "   Checking Redis..."
until docker exec healthcare-ai-redis redis-cli ping > /dev/null 2>&1; do
    echo "   ⏳ Waiting for Redis..."
    sleep 2
done
echo "   ✅ Redis ready"

echo ""
echo "================================================"
echo "✅ All infrastructure services are running!"
echo ""
echo "Services:"
echo "  - PostgreSQL:  localhost:5432"
echo "  - MongoDB:     localhost:27017"
echo "  - Redis:       localhost:6379"
echo "  - Kafka:       localhost:9092"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure"
echo "  2. Install Python dependencies: pip install -r requirements.txt"
echo "  3. Start API: python main.py"
echo "  4. Test: python scripts/test_api.py"
echo ""
echo "To stop services: docker-compose down"
echo "================================================"
