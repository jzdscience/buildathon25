#!/bin/bash

# Docker Local Testing Script for Codebase Time Machine

echo "================================================"
echo "Codebase Time Machine - Docker Testing Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="codebase-time-machine"
IMAGE_TAG="latest"
CONTAINER_NAME="codebase-time-machine-test"
PORT=8080

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --port) PORT="$2"; shift ;;
        --name) CONTAINER_NAME="$2"; shift ;;
        --tag) IMAGE_TAG="$2"; shift ;;
        --help) 
            echo "Usage: ./docker-test.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port PORT      Port to expose (default: 8080)"
            echo "  --name NAME      Container name (default: codebase-time-machine-test)"
            echo "  --tag TAG        Image tag (default: latest)"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  Container: ${CONTAINER_NAME}"
echo "  Port: ${PORT}"
echo ""

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}Error: Docker is not running${NC}"
        echo "Please start Docker and try again"
        exit 1
    fi
}

# Function to stop and remove existing container
cleanup_container() {
    if docker ps -a | grep -q "${CONTAINER_NAME}"; then
        echo -e "${YELLOW}Stopping and removing existing container...${NC}"
        docker stop "${CONTAINER_NAME}" >/dev/null 2>&1
        docker rm "${CONTAINER_NAME}" >/dev/null 2>&1
    fi
}

# Function to build the Docker image
build_image() {
    echo -e "${GREEN}Building Docker image...${NC}"
    if docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .; then
        echo -e "${GREEN}✓ Image built successfully${NC}"
    else
        echo -e "${RED}✗ Failed to build image${NC}"
        exit 1
    fi
}

# Function to run the container
run_container() {
    echo -e "${GREEN}Starting container...${NC}"
    if docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${PORT}:${PORT}" \
        -e PORT="${PORT}" \
        -e DEBUG=true \
        "${IMAGE_NAME}:${IMAGE_TAG}"; then
        echo -e "${GREEN}✓ Container started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start container${NC}"
        exit 1
    fi
}

# Function to check if the application is running
check_health() {
    echo -e "${YELLOW}Waiting for application to start...${NC}"
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PORT}" | grep -q "200\|302"; then
            echo -e "${GREEN}✓ Application is running!${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo ""
    echo -e "${RED}✗ Application failed to start${NC}"
    echo "Container logs:"
    docker logs "${CONTAINER_NAME}"
    return 1
}

# Main execution
main() {
    echo -e "${YELLOW}Starting Docker test...${NC}"
    echo ""
    
    # Check Docker
    check_docker
    
    # Clean up existing container
    cleanup_container
    
    # Build image
    build_image
    echo ""
    
    # Run container
    run_container
    echo ""
    
    # Check health
    if check_health; then
        echo ""
        echo "================================================"
        echo -e "${GREEN}Success! Application is running${NC}"
        echo "================================================"
        echo ""
        echo "Access the application at: http://localhost:${PORT}"
        echo ""
        echo "Useful commands:"
        echo "  View logs:    docker logs -f ${CONTAINER_NAME}"
        echo "  Stop:         docker stop ${CONTAINER_NAME}"
        echo "  Remove:       docker rm ${CONTAINER_NAME}"
        echo "  Shell access: docker exec -it ${CONTAINER_NAME} /bin/bash"
        echo ""
    else
        echo ""
        echo -e "${RED}Failed to start application${NC}"
        echo "Check the logs above for more information"
        exit 1
    fi
}

# Run main function
main

