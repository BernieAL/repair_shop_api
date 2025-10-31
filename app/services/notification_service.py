"""
Service for creating notifications
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType
from app.models.work_order import WorkOrder
from datetime import datetime

def create_notification(
    db: Session,
    customer_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    work_order_id: int = None
):
    """Create a notification for a customer"""
    notification = Notification(
        customer_id=customer_id,
        work_order_id=work_order_id,
        type=notification_type,
        title=title,
        message=message,
        read=False,
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def notify_status_change(db: Session, work_order: WorkOrder, new_status: str):
    """Notify customer when work order status changes"""
    status_messages = {
        "pending": "Your repair request has been received",
        "in_progress": "Your repair is now in progress",
        "waiting_parts": "Waiting for parts to arrive",
        "completed": "Great news! Your repair is complete",
        "cancelled": "Your repair has been cancelled"
    }
    
    return create_notification(
        db=db,
        customer_id=work_order.customer_id,
        notification_type=NotificationType.STATUS_CHANGE,
        title="Repair Status Updated",
        message=f"Work order #{work_order.id}: {status_messages.get(new_status, 'Status updated')}",
        work_order_id=work_order.id
    )


def notify_new_message(db: Session, work_order: WorkOrder, sender_name: str):
    """Notify customer about new message from technician"""
    return create_notification(
        db=db,
        customer_id=work_order.customer_id,
        notification_type=NotificationType.MESSAGE,
        title=f"New message from {sender_name}",
        message=f"You have a new message about work order #{work_order.id}",
        work_order_id=work_order.id
    )


def notify_tech_note(db: Session, work_order: WorkOrder):
    """Notify customer when technician adds notes"""
    return create_notification(
        db=db,
        customer_id=work_order.customer_id,
        notification_type=NotificationType.TECH_NOTE,
        title="Technician Note Added",
        message=f"The technician has added notes to work order #{work_order.id}",
        work_order_id=work_order.id
    )