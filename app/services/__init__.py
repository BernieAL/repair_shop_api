"""
Notification helper for messaging system
Creates notifications when technicians send messages to customers
"""
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType
from app.models.message import Message, SenderType
from app.models.work_order import WorkOrder


def create_message_notification(
    db: Session,
    message: Message,
    work_order: WorkOrder
):
    """
    Create a notification when a technician sends a message
    This should be called after a technician creates a message
    """
    # Only create notifications for messages from technicians
    if message.sender_type != SenderType.TECHNICIAN:
        return None
    
    # Create notification for the customer
    notification = Notification(
        customer_id=work_order.customer_id,
        work_order_id=work_order.id,
        type=NotificationType.TECH_NOTE,
        title=f"New message on Repair #{work_order.id}",
        message=f"{work_order.assigned_technician or 'Your technician'} sent you a message",
        is_read=0
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


def create_system_message(
    db: Session,
    work_order_id: int,
    message_text: str
):
    """
    Create a system message for important automated notifications
    Examples: "Repair status changed to completed", "Estimate ready for approval"
    """
    system_message = Message(
        work_order_id=work_order_id,
        sender_id=0,  # 0 indicates system
        sender_type=SenderType.SYSTEM,
        message=message_text,
        is_read=0
    )
    
    db.add(system_message)
    db.commit()
    db.refresh(system_message)
    
    return system_message