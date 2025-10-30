"""add messages table

Revision ID: add_messages_table
Revises: add_notifications_table
Create Date: 2025-10-30 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_messages_table'
down_revision = 'add_notifications_table'  
branch_labels = None
depends_on = None


def upgrade():
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('work_order_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('sender_type', sa.Enum('CUSTOMER', 'TECHNICIAN', 'SYSTEM', name='sendertype'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_messages_id', 'messages', ['id'])
    op.create_index('ix_messages_work_order_id', 'messages', ['work_order_id'])
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_messages_created_at', 'messages')
    op.drop_index('ix_messages_sender_id', 'messages')
    op.drop_index('ix_messages_work_order_id', 'messages')
    op.drop_index('ix_messages_id', 'messages')
    
    # Drop table
    op.drop_table('messages')
    
    # Drop enum type (PostgreSQL specific)
    op.execute('DROP TYPE IF EXISTS sendertype')