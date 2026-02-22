"""
n8n Integration Module for AURORA
Provides webhook endpoints and workflow automation capabilities
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookData(BaseModel):
    """Base model for incoming webhook data"""
    source: str
    event_type: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None

class VODIngestionRequest(BaseModel):
    """Model for VOD ingestion requests"""
    video_url: str
    source_type: str  # 'youtube', 'twitch', 'local'
    priority: str = 'normal'  # 'low', 'normal', 'high'
    metadata: Optional[Dict[str, Any]] = {}

class AnalysisStatusRequest(BaseModel):
    """Model for analysis status requests"""
    analysis_id: str
    status: str  # 'started', 'processing', 'completed', 'failed'
    results: Optional[Dict[str, Any]] = {}

class NotificationRequest(BaseModel):
    """Model for notification requests"""
    recipient: str
    message: str
    notification_type: str  # 'discord', 'email', 'slack'
    priority: str = 'normal'

class AuroraWorkflowManager:
    """Manages n8n workflows and automation"""
    
    def __init__(self):
        self.active_workflows = {}
        self.workflow_history = []
        self.webhook_subscriptions = {}
        
    async def trigger_vod_ingestion(self, request: VODIngestionRequest) -> Dict[str, Any]:
        """Trigger VOD ingestion workflow"""
        workflow_id = str(uuid.uuid4())
        
        workflow_data = {
            "workflow_id": workflow_id,
            "type": "vod_ingestion",
            "status": "started",
            "request": request.dict(),
            "started_at": datetime.now().isoformat(),
            "steps": [
                {"step": "download", "status": "pending"},
                {"step": "analysis", "status": "pending"},
                {"step": "storage", "status": "pending"},
                {"step": "notification", "status": "pending"}
            ]
        }
        
        self.active_workflows[workflow_id] = workflow_data
        logger.info(f"Started VOD ingestion workflow: {workflow_id}")
        
        # Start background processing
        asyncio.create_task(self.process_vod_workflow(workflow_id))
        
        return {
            "workflow_id": workflow_id,
            "status": "started",
            "message": "VOD ingestion workflow initiated"
        }
    
    async def process_vod_workflow(self, workflow_id: str):
        """Process VOD ingestion workflow steps"""
        if workflow_id not in self.active_workflows:
            return
            
        workflow = self.active_workflows[workflow_id]
        
        try:
            # Step 1: Download
            workflow["steps"][0]["status"] = "processing"
            await asyncio.sleep(2)  # Simulate download
            workflow["steps"][0]["status"] = "completed"
            
            # Step 2: Analysis
            workflow["steps"][1]["status"] = "processing"
            # This would integrate with your existing analysis system
            await asyncio.sleep(5)  # Simulate analysis
            workflow["steps"][1]["status"] = "completed"
            
            # Step 3: Storage
            workflow["steps"][2]["status"] = "processing"
            await asyncio.sleep(1)  # Simulate storage
            workflow["steps"][2]["status"] = "completed"
            
            # Step 4: Notification
            workflow["steps"][3]["status"] = "processing"
            await self.send_workflow_notification(workflow_id)
            workflow["steps"][3]["status"] = "completed"
            
            # Mark workflow as completed
            workflow["status"] = "completed"
            workflow["completed_at"] = datetime.now().isoformat()
            
            # Move to history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            logger.info(f"Completed VOD ingestion workflow: {workflow_id}")
            
        except Exception as e:
            workflow["status"] = "failed"
            workflow["error"] = str(e)
            logger.error(f"Failed VOD workflow {workflow_id}: {e}")
    
    async def send_workflow_notification(self, workflow_id: str):
        """Send workflow completion notification"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
            
        # This would integrate with Discord/Slack/Email
        notification_data = {
            "type": "workflow_completed",
            "workflow_id": workflow_id,
            "video_url": workflow["request"]["video_url"],
            "status": workflow["status"],
            "completed_at": datetime.now().isoformat()
        }
        
        # Simulate notification sending
        logger.info(f"Sending notification: {notification_data}")
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific workflow"""
        return self.active_workflows.get(workflow_id)
    
    def get_all_workflows(self) -> Dict[str, Any]:
        """Get all workflows (active and historical)"""
        return {
            "active": self.active_workflows,
            "history": self.workflow_history[-10:],  # Last 10 workflows
            "total_active": len(self.active_workflows),
            "total_completed": len(self.workflow_history)
        }
    
    def register_webhook(self, event_type: str, callback_url: str) -> Dict[str, Any]:
        """Register webhook for n8n integration"""
        webhook_id = str(uuid.uuid4())
        
        self.webhook_subscriptions[webhook_id] = {
            "event_type": event_type,
            "callback_url": callback_url,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Registered webhook {webhook_id} for {event_type}")
        
        return {
            "webhook_id": webhook_id,
            "event_type": event_type,
            "status": "registered"
        }
    
    async def trigger_webhooks(self, event_type: str, data: Dict[str, Any]):
        """Trigger registered webhooks for an event"""
        for webhook_id, webhook in self.webhook_subscriptions.items():
            if webhook["event_type"] == event_type:
                # This would make HTTP call to n8n webhook
                logger.info(f"Triggering webhook {webhook_id} for {event_type}")

# Global workflow manager instance
workflow_manager = AuroraWorkflowManager()

def setup_n8n_routes(app: FastAPI):
    """Setup n8n integration routes"""
    
    @app.post("/n8n/webhook/ingest", tags=["n8n Integration"])
    async def ingest_vod_webhook(request: VODIngestionRequest):
        """Webhook for VOD ingestion from n8n"""
        try:
            result = await workflow_manager.trigger_vod_ingestion(request)
            return result
        except Exception as e:
            logger.error(f"VOD ingestion webhook error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/n8n/webhook/analysis-status", tags=["n8n Integration"])
    async def analysis_status_webhook(request: AnalysisStatusRequest):
        """Webhook for analysis status updates from n8n"""
        try:
            # Update workflow status
            if request.analysis_id in workflow_manager.active_workflows:
                workflow = workflow_manager.active_workflows[request.analysis_id]
                workflow["status"] = request.status
                if request.results:
                    workflow["results"] = request.results
            
            return {"status": "updated", "analysis_id": request.analysis_id}
        except Exception as e:
            logger.error(f"Analysis status webhook error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/n8n/webhook/notify", tags=["n8n Integration"])
    async def notification_webhook(request: NotificationRequest):
        """Webhook for notifications from n8n"""
        try:
            # Process notification
            notification_data = {
                "recipient": request.recipient,
                "message": request.message,
                "type": request.notification_type,
                "priority": request.priority,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Processing notification: {notification_data}")
            return {"status": "sent", "notification_id": str(uuid.uuid4())}
        except Exception as e:
            logger.error(f"Notification webhook error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/n8n/workflows", tags=["n8n Integration"])
    async def get_workflows():
        """Get all workflows status"""
        return workflow_manager.get_all_workflows()
    
    @app.get("/n8n/workflows/{workflow_id}", tags=["n8n Integration"])
    async def get_workflow(workflow_id: str):
        """Get specific workflow status"""
        workflow = workflow_manager.get_workflow_status(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    
    @app.post("/n8n/webhooks/register", tags=["n8n Integration"])
    async def register_webhook(event_type: str, callback_url: str):
        """Register new webhook for n8n integration"""
        try:
            result = workflow_manager.register_webhook(event_type, callback_url)
            return result
        except Exception as e:
            logger.error(f"Webhook registration error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/n8n/status", tags=["n8n Integration"])
    async def get_n8n_status():
        """Get n8n integration status"""
        return {
            "status": "active",
            "active_workflows": len(workflow_manager.active_workflows),
            "registered_webhooks": len(workflow_manager.webhook_subscriptions),
            "total_completed": len(workflow_manager.workflow_history),
            "supported_events": [
                "vod_ingestion",
                "analysis_completed",
                "workflow_failed",
                "notification_sent"
            ]
        }
    
    @app.post("/n8n/trigger/youtube-monitor", tags=["n8n Integration"])
    async def trigger_youtube_monitor(channel_id: str, max_videos: int = 5):
        """Trigger YouTube channel monitoring workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # This would integrate with YouTube API
            workflow_data = {
                "workflow_id": workflow_id,
                "type": "youtube_monitor",
                "status": "started",
                "channel_id": channel_id,
                "max_videos": max_videos,
                "started_at": datetime.now().isoformat()
            }
            
            workflow_manager.active_workflows[workflow_id] = workflow_data
            
            return {
                "workflow_id": workflow_id,
                "status": "started",
                "message": f"YouTube monitoring started for channel: {channel_id}"
            }
        except Exception as e:
            logger.error(f"YouTube monitor trigger error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Export for use in main backend
__all__ = ['setup_n8n_routes', 'workflow_manager']
