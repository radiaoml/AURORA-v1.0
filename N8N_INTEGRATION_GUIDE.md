# AURORA n8n Integration Guide

## 🚀 Overview
This guide explains how to integrate AURORA with n8n for automated workflow management and enhanced tactical intelligence processing.

## 📋 Prerequisites
- **n8n Instance**: Self-hosted or cloud-based n8n installation
- **AURORA Backend**: Running on http://localhost:8000
- **API Access**: Network connectivity between n8n and AURORA

## 🛠️ Setup Instructions

### 1. Install AURORA n8n Integration
The n8n integration is already included in your AURORA backend:
- `n8n_integration.py`: Core integration module
- `n8n_workflows/`: Pre-built workflow templates

### 2. Start AURORA Backend
```bash
python aurora_backend.py
```
This will automatically enable n8n integration endpoints.

### 3. Import Workflows into n8n

#### Method 1: Import JSON Files
1. Open n8n interface
2. Click "Import from file"
3. Select workflow files from `n8n_workflows/` directory:
   - `aurora_vod_ingestion.json`: Automated VOD processing
   - `multi_agent_pipeline.json`: Multi-agent coordination

#### Method 2: Manual Setup
Create workflows manually using the node configurations below.

## 🔄 Available Workflows

### 1. VOD Ingestion Automation
**File**: `aurora_vod_ingestion.json`

**Purpose**: Automatically process YouTube videos from specified channels

**Features**:
- Hourly channel monitoring
- Automatic VOD download and analysis
- Discord notifications on completion
- Analytics database storage

**Setup**:
1. Configure YouTube API key in the "Check YouTube Channel" node
2. Set target channel ID
3. Configure Discord webhook URL
4. Activate workflow

### 2. Multi-Agent Pipeline
**File**: `multi_agent_pipeline.json`

**Purpose**: Orchestrate multi-agent analysis with intelligent routing

**Features**:
- Sequential agent processing
- Confidence-based routing
- Multi-channel notifications
- Performance analytics

**Setup**:
1. Configure notification endpoints (Discord, Email, Slack)
2. Set confidence thresholds
3. Configure analytics database
4. Activate workflow

## 🔌 API Endpoints

### Webhook Endpoints
- `POST /n8n/webhook/ingest`: Trigger VOD ingestion
- `POST /n8n/webhook/analysis-status`: Update analysis status
- `POST /n8n/webhook/notify`: Send notifications
- `POST /n8n/webhooks/register`: Register new webhook

### Status Endpoints
- `GET /n8n/workflows`: Get all workflows status
- `GET /n8n/workflows/{workflow_id}`: Get specific workflow
- `GET /n8n/status`: Get n8n integration status

### Trigger Endpoints
- `POST /n8n/trigger/youtube-monitor`: Start YouTube monitoring

## 📊 Request/Response Formats

### VOD Ingestion Request
```json
{
  "video_url": "https://www.youtube.com/watch?v=example",
  "source_type": "youtube",
  "priority": "normal",
  "metadata": {
    "channel": "Example Channel",
    "title": "Video Title"
  }
}
```

### Analysis Status Update
```json
{
  "analysis_id": "workflow-uuid",
  "status": "completed",
  "results": {
    "CleanerBot": {"status": "completed", "confidence": 95.2},
    "AnalystBot": {"status": "completed", "confidence": 87.8},
    "CoachBot": {"status": "completed", "confidence": 91.5},
    "OracleBot": {"status": "completed", "confidence": 89.3}
  }
}
```

### Notification Request
```json
{
  "recipient": "discord",
  "message": "Analysis complete!",
  "notification_type": "discord",
  "priority": "high"
}
```

## 🎯 Advanced Configuration

### Custom Webhook Registration
```bash
curl -X POST "http://localhost:8000/n8n/webhooks/register" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "custom_event",
    "callback_url": "https://your-n8n-instance.com/webhook/custom"
  }'
```

### YouTube Channel Monitoring
```bash
curl -X POST "http://localhost:8000/n8n/trigger/youtube-monitor" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "UCv5q8E3N0C4E9m3L7x5Q",
    "max_videos": 5
  }'
```

## 🔧 Monitoring and Debugging

### Check Integration Status
```bash
curl "http://localhost:8000/n8n/status"
```

### Monitor Active Workflows
```bash
curl "http://localhost:8000/n8n/workflows"
```

### View Specific Workflow
```bash
curl "http://localhost:8000/n8n/workflows/{workflow_id}"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Connection Refused
- **Cause**: AURORA backend not running
- **Solution**: Start `python aurora_backend.py`

#### 2. Webhook Not Triggered
- **Cause**: Network connectivity issues
- **Solution**: Check firewall settings and network access

#### 3. Workflow Fails
- **Cause**: Invalid API keys or configuration
- **Solution**: Verify YouTube API key and notification endpoints

### Debug Mode
Enable debug logging in AURORA backend:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎮 Best Practices

### 1. Security
- Use HTTPS for webhook URLs
- Implement authentication for n8n endpoints
- Validate all incoming data

### 2. Performance
- Set appropriate intervals for scheduled workflows
- Use batch processing for multiple videos
- Monitor resource usage

### 3. Reliability
- Implement retry mechanisms in n8n workflows
- Set up error notifications
- Monitor workflow execution history

## 📈 Scaling Considerations

### Horizontal Scaling
- Deploy multiple AURORA backend instances
- Use load balancer for webhook distribution
- Implement queue system for high-volume processing

### Vertical Scaling
- Increase processing timeout for large VODs
- Optimize database queries for analytics
- Use caching for frequently accessed data

## 🔮 Future Enhancements

### Planned Features
- **Real-time Dashboard**: Live workflow monitoring
- **Advanced Routing**: Intelligent agent selection
- **Performance Analytics**: Historical workflow performance
- **Custom Nodes**: AURORA-specific n8n nodes

### Integration Opportunities
- **Discord Bot**: Direct Discord integration
- **Twitch API**: Live stream monitoring
- **Mobile App**: Push notifications for mobile devices

## 📞 Support

For issues with n8n integration:
1. Check AURORA backend logs
2. Verify n8n workflow configuration
3. Test API endpoints manually
4. Review this documentation

---

**🚀 Your AURORA + n8n integration creates the world's most automated Valorant tactical intelligence platform!**
