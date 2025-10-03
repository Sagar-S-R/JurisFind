#!/bin/bash

# JurisFind Management Script
# Provides easy commands to manage your JurisFind deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_usage() {
    echo "JurisFind Management Script"
    echo ""
    echo "Usage: ./manage.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all containers"
    echo "  stop        - Stop all containers"
    echo "  restart     - Restart all containers"
    echo "  logs        - Show container logs"
    echo "  status      - Show container status"
    echo "  update      - Pull latest changes and rebuild"
    echo "  backup      - Backup data and logs"
    echo "  shell       - Open shell in backend container"
    echo "  test        - Run Azure integration tests"
    echo "  upload      - Upload PDFs to Azure"
    echo "  index       - Generate FAISS index"
    echo "  health      - Check API health"
    echo "  cleanup     - Remove unused Docker resources"
}

case "$1" in
    start)
        echo -e "${BLUE}Starting JurisFind containers...${NC}"
        docker-compose up -d
        echo -e "${GREEN}Containers started successfully${NC}"
        ;;
    
    stop)
        echo -e "${BLUE}Stopping JurisFind containers...${NC}"
        docker-compose down
        echo -e "${GREEN}Containers stopped${NC}"
        ;;
    
    restart)
        echo -e "${BLUE}Restarting JurisFind containers...${NC}"
        docker-compose restart
        echo -e "${GREEN}Containers restarted${NC}"
        ;;
    
    logs)
        if [ -n "$2" ]; then
            docker-compose logs -f "$2"
        else
            docker-compose logs -f
        fi
        ;;
    
    status)
        echo -e "${BLUE}Container Status:${NC}"
        docker-compose ps
        echo ""
        echo -e "${BLUE}Resource Usage:${NC}"
        docker stats --no-stream
        ;;
    
    update)
        echo -e "${BLUE}Updating JurisFind...${NC}"
        git pull
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        echo -e "${GREEN}Update completed${NC}"
        ;;
    
    backup)
        DATE=$(date +%Y%m%d_%H%M%S)
        BACKUP_DIR="backups/backup_$DATE"
        
        echo -e "${BLUE}Creating backup: $BACKUP_DIR${NC}"
        mkdir -p "$BACKUP_DIR"
        
        # Backup data and logs
        cp -r api/data "$BACKUP_DIR/" 2>/dev/null || echo "No data directory found"
        cp -r api/logs "$BACKUP_DIR/" 2>/dev/null || echo "No logs directory found"
        cp .env "$BACKUP_DIR/" 2>/dev/null || echo "No .env file found"
        
        # Create tar archive
        tar -czf "backup_$DATE.tar.gz" -C backups "backup_$DATE"
        rm -rf "$BACKUP_DIR"
        
        echo -e "${GREEN}Backup created: backup_$DATE.tar.gz${NC}"
        ;;
    
    shell)
        echo -e "${BLUE}Opening shell in backend container...${NC}"
        docker exec -it jurisfind_backend bash
        ;;
    
    test)
        echo -e "${BLUE}Running Azure integration tests...${NC}"
        docker exec jurisfind_backend python tests/test_azure_integration.py
        ;;
    
    upload)
        echo -e "${BLUE}Uploading PDFs to Azure...${NC}"
        docker exec jurisfind_backend python helpers/azure_data_manager.py upload-pdfs --pdf-dir ./data/pdfs
        ;;
    
    index)
        echo -e "${BLUE}Generating FAISS index...${NC}"
        docker exec jurisfind_backend python helpers/azure_data_manager.py generate-index
        ;;
    
    health)
        echo -e "${BLUE}Checking API health...${NC}"
        curl -f http://localhost/api/health | jq . || echo "API not responding"
        ;;
    
    cleanup)
        echo -e "${BLUE}Cleaning up Docker resources...${NC}"
        docker system prune -f
        docker volume prune -f
        echo -e "${GREEN}Cleanup completed${NC}"
        ;;
    
    *)
        print_usage
        exit 1
        ;;
esac