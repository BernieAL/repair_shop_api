"""
Test triggering message notification
"""
from app.db.session import SessionLocal
from app.models.work_order import WorkOrder
from app.models.message import Message, SenderType
from app.services.notification_service import notify_new_message

def trigger_message_notification():
    db = SessionLocal()
    
    try:
        # Get a work order
        work_order = db.query(WorkOrder).first()
        
        if not work_order:
            print("❌ No work orders found")
            return
        
        print(f"📋 Work Order #{work_order.id}")
        print(f"   Customer ID: {work_order.customer_id}")
        
        # Create technician message
        message = Message(
            work_order_id=work_order.id,
            sender_id=1,
            sender_type=SenderType.TECHNICIAN,
            message="Your repair is progressing well. Should be done by tomorrow!",
            is_read=0
        )
        db.add(message)
        db.commit()
        
        # Create notification
        notification = notify_new_message(db, work_order, "Tech Support")
        
        print(f"\n✅ Message created")
        print(f"🔔 Notification created:")
        print(f"   ID: {notification.id}")
        print(f"   Title: {notification.title}")
        print(f"   Message: {notification.message}")
        print(f"\n💡 Check your frontend - new notification should appear!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    trigger_message_notification()