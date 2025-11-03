from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    TECHNICIAN = "technician"
    CUSTOMER = "customer"