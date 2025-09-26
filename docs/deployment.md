# Deployment

## Overview

Legal Case can be deployed to various cloud platforms with different trade-offs for cost, scalability, and maintenance.

## Backend Deployment

### Azure App Service

1. **Create App Service**:
   - Runtime: Python 3.9
   - Pricing tier: B1 or higher

2. **Configure Environment**:
   ```bash
   # Set environment variables in Azure portal
   GROQ_API_KEY=your_key_here
   ```

3. **Deploy Code**:
   - Use Azure CLI or Git deployment
   - Ensure `requirements.txt` is included

4. **Database**: Use Azure Blob Storage for FAISS index

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t legal-case-backend .
docker run -p 8000:8000 legal-case-backend
```

## Frontend Deployment

### Vercel

1. **Connect Repository**: Import from GitHub
2. **Build Settings**:
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Environment Variables**:
   ```
   VITE_API_BASE_URL=https://your-backend-url.com/api
   ```

### Netlify

1. **Deploy Settings**:
   - Build command: `npm run build`
   - Publish directory: `dist`

2. **Environment Variables**: Set in Netlify dashboard

## Production Considerations

### Security
- Use HTTPS everywhere
- Store secrets in environment variables
- Implement rate limiting
- Regular security updates

### Performance
- Enable caching
- Use CDN for static assets
- Monitor resource usage
- Scale based on load

### Monitoring
- Application Insights (Azure)
- Vercel Analytics
- Custom logging
- Error tracking

## Cost Optimization

- **Azure**: Pay-as-you-go, scale to zero
- **Vercel**: Generous free tier, pay for usage
- **Netlify**: Free for personal projects