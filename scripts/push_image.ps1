# Push Docker image to Docker Hub
# This is a PowerShell wrapper for push_image.sh

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Push Image to Docker Hub                    " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Get Docker Hub username
$DOCKER_USERNAME = Read-Host "Enter your Docker Hub username"

if ([string]::IsNullOrWhiteSpace($DOCKER_USERNAME)) {
    Write-Host "❌ Username required!" -ForegroundColor Red
    exit 1
}

# Tag the image
$IMAGE_NAME = "${DOCKER_USERNAME}/intelligent-traffic-teamb:latest"
Write-Host ""
Write-Host "Tagging image as: $IMAGE_NAME" -ForegroundColor Green
docker tag intelligent-traffic-teamb:latest $IMAGE_NAME

# Login to Docker Hub
Write-Host ""
Write-Host "Logging in to Docker Hub..." -ForegroundColor Green
docker login

# Push the image
Write-Host ""
Write-Host "Pushing image (this will take 5-15 minutes)..." -ForegroundColor Yellow
docker push $IMAGE_NAME

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   ✅ Push Complete!                            " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your image is now available at:" -ForegroundColor Green
Write-Host "  docker pull $IMAGE_NAME" -ForegroundColor Cyan
Write-Host ""
Write-Host "Save this for RunPod:" -ForegroundColor Yellow
Write-Host "  IMAGE=$IMAGE_NAME" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: Copy this command to RunPod terminal:" -ForegroundColor Yellow
Write-Host ""
Write-Host "docker pull $IMAGE_NAME && docker run -d --name carla-system --gpus all --restart unless-stopped -p 2000:2000 -p 8000:8000 -p 6080:6080 $IMAGE_NAME" -ForegroundColor Cyan
Write-Host ""
