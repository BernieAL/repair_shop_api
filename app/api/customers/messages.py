"""
Messages API endpoints for customer portal
Handles communication threads between customers and technicians
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.message import Message, SenderType
from app.models.work_order import WorkOrder
from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.schemas.message import MessageCreate, MessageResponse, MessageThread, MessageMarkRead

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/work-order/{work_order_id}", response_model=MessageThread)
async def get_work_order_messages(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_customer: User = Depends(get_current_user)
):
    """
    Get all messages for a specific work order (message thread)
    Only returns messages for work orders owned by the current customer
    """
    # Verify work order belongs to customer
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == work_order_id,
        WorkOrder.customer_id == current_customer.id
    ).first()
    
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found or access denied"
        )
    
    # Get all messages for this work order, ordered by creation time
    messages = db.query(Message).filter(
        Message.work_order_id == work_order_id
    ).order_by(Message.created_at.asc()).all()
    
    # Count unread messages (messages from technician that customer hasn't read)
    unread_count = db.query(Message).filter(
        Message.work_order_id == work_order_id,
        Message.sender_type == SenderType.TECHNICIAN,
        Message.is_read == 0
    ).count()
    
    # Format messages with sender info
    formatted_messages = []
    for msg in messages:
        msg_dict = msg.to_dict()
        
        # Add sender name based on sender type
        if msg.sender_type == SenderType.CUSTOMER:
            msg_dict["sender_name"] = current_customer.name
            msg_dict["sender_avatar"] = None  # Could add customer avatar URL
        elif msg.sender_type == SenderType.TECHNICIAN:
            # In production, fetch from technician table
            msg_dict["sender_name"] = work_order.assigned_technician or "Technician"
            msg_dict["sender_avatar"] = None
        else:  # SYSTEM
            msg_dict["sender_name"] = "System"
            msg_dict["sender_avatar"] = None
        
        formatted_messages.append(MessageResponse(**msg_dict))
    
    return MessageThread(
        work_order_id=work_order_id,
        total_messages=len(messages),
        unread_count=unread_count,
        messages=formatted_messages
    )


@router.post("/work-order/{work_order_id}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    work_order_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_customer: User = Depends(get_current_user)
):
    """
    Send a new message in a work order thread
    Customer can only send messages to their own work orders
    """
    # Verify work order belongs to customer
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == work_order_id,
        WorkOrder.customer_id == current_customer.id
    ).first()
    
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found or access denied"
        )
    
    # Create new message
    new_message = Message(
        work_order_id=work_order_id,
        sender_id=current_customer.id,
        sender_type=SenderType.CUSTOMER,
        message=message_data.message,
        is_read=0  # New messages are unread
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # TODO: Create notification for technician (when technician system is built)
    # This would notify the assigned technician that customer sent a message
    
    # Format response
    msg_dict = new_message.to_dict()
    msg_dict["sender_name"] = current_customer.name
    msg_dict["sender_avatar"] = None
    
    return MessageResponse(**msg_dict)


@router.put("/mark-read", status_code=status.HTTP_200_OK)
async def mark_messages_read(
    mark_read_data: MessageMarkRead,
    db: Session = Depends(get_db),
    current_customer: User = Depends(get_current_user)
):
    """
    Mark specific messages as read
    Customer can only mark messages in their own work orders
    """
    if not mark_read_data.message_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No message IDs provided"
        )
    
    # Get messages and verify they belong to customer's work orders
    messages = db.query(Message).join(WorkOrder).filter(
        Message.id.in_(mark_read_data.message_ids),
        WorkOrder.customer_id == current_customer.id
    ).all()
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found or access denied"
        )
    
    # Mark messages as read
    marked_count = 0
    for message in messages:
        if message.is_read == 0:
            message.is_read = 1
            marked_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "marked_count": marked_count,
        "message": f"Marked {marked_count} message(s) as read"
    }


@router.get("/unread-count")
async def get_unread_message_count(
    db: Session = Depends(get_db),
    current_customer: User = Depends(get_current_user)
):
    """
    Get total count of unread messages across all work orders
    Only counts messages from technicians (not customer's own messages)
    """
    unread_count = db.query(Message).join(WorkOrder).filter(
        WorkOrder.customer_id == current_customer.id,
        Message.sender_type == SenderType.TECHNICIAN,
        Message.is_read == 0
    ).count()
    
    return {"unread_count": unread_count}


@router.get("/recent", response_model=List[MessageResponse])
async def get_recent_messages(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_customer: User = Depends(get_current_user)
):
    """
    Get recent messages across all work orders
    Useful for showing recent activity in dashboard
    """
    messages = db.query(Message).join(WorkOrder).filter(
        WorkOrder.customer_id == current_customer.id
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    # Format messages
    formatted_messages = []
    for msg in messages:
        work_order = db.query(WorkOrder).filter(WorkOrder.id == msg.work_order_id).first()
        
        msg_dict = msg.to_dict()
        
        if msg.sender_type == SenderType.CUSTOMER:
            msg_dict["sender_name"] = current_customer.name
        elif msg.sender_type == SenderType.TECHNICIAN:
            msg_dict["sender_name"] = work_order.assigned_technician or "Technician"
        else:
            msg_dict["sender_name"] = "System"
        
        msg_dict["sender_avatar"] = None
        formatted_messages.append(MessageResponse(**msg_dict))
    
    return formatted_messages