@echo off
cd backend
git add .
git commit -m "Updated deployment configuration"
git push -u azure master --force
if errorlevel 1 (
    echo Deployment failed
    exit /b 1
)
echo Deployment completed successfully