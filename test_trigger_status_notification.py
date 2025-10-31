"""
Test triggering status change notification
"""
from app.db.session import SessionLocal
from app.models.work_order import WorkOrder
from app.services.notification_service import notify_status_change

def trigger_status_notification():
    db = SessionLocal()  # This will use your PostgreSQL from .env
    
    try:
        # Get a work order with a customer
        work_order = db.query(WorkOrder).filter(
            WorkOrder.customer_id.isnot(None)
        ).first()
        
        if not work_order:
            print("❌ No work orders found with customer_id")
            print("💡 Make sure you've run: python seed.py")
            return
        
        print(f"📋 Work Order #{work_order.id}")
        print(f"   Customer ID: {work_order.customer_id}")
        print(f"   Current Status: {work_order.status}")
        
        # Change status to something different
        current_status = work_order.status.value if hasattr(work_order.status, 'value') else work_order.status
        
        # Cycle through statuses for testing
        status_cycle = {
            "pending": "in_progress",
            "in_progress": "completed",
            "completed": "pending",
            "waiting_parts": "in_progress",
            "cancelled": "pending"
        }
        
        new_status = status_cycle.get(current_status, "in_progress")
        
        # Update the work order status
        work_order.status = new_status
        db.commit()
        
        # Create notification
        notification = notify_status_change(db, work_order, new_status)
        
        print(f"\n✅ Status updated: {current_status} → {new_status}")
        print(f"🔔 Notification created:")
        print(f"   ID: {notification.id}")
        print(f"   Title: {notification.title}")
        print(f"   Message: {notification.message}")
        print(f"   Type: {notification.type}")
        print(f"\n💡 Check your frontend - new notification should appear!")
        print(f"   (Frontend polls every 30 seconds, or refresh the page)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    trigger_status_notification()