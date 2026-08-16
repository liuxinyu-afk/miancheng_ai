from sqlalchemy import Column,Integer,String,Text,DateTime,TinyInt,ForeignKey,Numeric,Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer,primary_key=True,autoincrement=True)
    username = Column(String(50),unique=True,nullable=False)
    password = Column(String(255),nullable=False)
    role = Column(Enum('student','teacher','auditor','admin'),default='student')
    auth_status = Column(TinyInt,default=0)
    avatar = Column(String(255),nullable=True)
    nickname = Column(String(50),nullable=False)
    register_time = Column(DateTime,default=datetime.now)
    account_status = Column(TinyInt,default=1)

class TaskPackage(Base):
    __tablename__ = "task_package"
    package_id = Column(Integer,primary_key=True,autoincrement=True)
    task_title = Column(String(200),nullable=False)
    task_category = Column(String(50),nullable=False)
    generate_source = Column(Enum('ai','user'),nullable=False)
    publisher_id = Column(Integer,ForeignKey("user.user_id"))
    audit_status = Column(TinyInt,default=0)
    create_time = Column(DateTime,default=datetime.now)
    description = Column(Text,nullable=True)
    is_official = Column(TinyInt,default=0)

class TaskItem(Base):
    __tablename__ = "task_item"
    item_id = Column(Integer,primary_key=True,autoincrement=True)
    package_id = Column(Integer,ForeignKey("task_package.package_id"))
    task_name = Column(String(200),nullable=False)
    task_desc = Column(Text,nullable=True)
    sort_num = Column(Integer,default=1)
    expect_hours = Column(Numeric(3,1),nullable=False)
    finish_status = Column(TinyInt,default=0)

class MarketResource(Base):
    __tablename__ = "market_resource"
    resource_id = Column(Integer,primary_key=True,autoincrement=True)
    title = Column(String(200),nullable=False)
    category = Column(String(50),nullable=False)
    content = Column(Text,nullable=True)
    attach_url = Column(String(255),nullable=True)
    publisher_id = Column(Integer,ForeignKey("user.user_id"))
    user_role = Column(String(20),nullable=False)
    audit_status = Column(TinyInt,default=0)
    teacher_tag = Column(TinyInt,default=0)
    publish_time = Column(DateTime,default=datetime.now)
    reject_reason = Column(Text,nullable=True)

class CheckRecord(Base):
    __tablename__ = "check_record"
    check_id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("user.user_id"))
    item_id = Column(Integer,ForeignKey("task_item.item_id"))
    check_time = Column(DateTime,default=datetime.now)
    check_status = Column(TinyInt,default=1)
    study_note = Column(Text,nullable=True)

class Note(Base):
    __tablename__ = "note"
    note_id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("user.user_id"))
    package_id = Column(Integer,ForeignKey("task_package.package_id"),nullable=True)
    content = Column(Text,nullable=False)
    create_time = Column(DateTime,default=datetime.now)
    update_time = Column(DateTime,default=datetime.now,onupdate=datetime.now)
    is_public = Column(TinyInt,default=0)

class AchievementPost(Base):
    __tablename__ = "achievement_post"
    post_id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("user.user_id"))
    content = Column(Text,nullable=False)
    img_url = Column(String(255),nullable=True)
    like_count = Column(Integer,default=0)
    comment_count = Column(Integer,default=0)
    audit_status = Column(TinyInt,default=0)
    publish_time = Column(DateTime,default=datetime.now)

class AuditLog(Base):
    __tablename__ = "audit_log"
    audit_id = Column(Integer,primary_key=True,autoincrement=True)
    auditor_id = Column(Integer,ForeignKey("user.user_id"))
    target_id = Column(Integer,nullable=False)
    content_type = Column(String(30),nullable=False)
    audit_result = Column(TinyInt,nullable=False)
    reject_reason = Column(Text,nullable=True)
    audit_time = Column(DateTime,default=datetime.now)