from __future__ import annotations

from datetime import datetime

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    SqliteDatabase,
    TextField,
)

database = SqliteDatabase(None, pragmas={"foreign_keys": 1, "journal_mode": "wal", "busy_timeout": 5000})


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    id = AutoField()
    username = CharField(unique=True, max_length=64)
    password_hash = CharField()
    is_active = BooleanField(default=True)
    must_change_password = BooleanField(default=False)
    expires_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)


class SystemUser(BaseModel):
    """Local krFTP console accounts, intentionally separate from transfer users."""
    id = AutoField()
    username = CharField(unique=True, max_length=64)
    password_hash = CharField()
    is_active = BooleanField(default=True)
    must_change_password = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)


class UserRoot(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, backref="roots", on_delete="CASCADE")
    protocol = CharField(default="BOTH", max_length=8)
    root_path = CharField()
    permissions = TextField(default="[]")
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        indexes = ((('user', 'protocol', 'root_path'), True),)


class IpRule(BaseModel):
    id = AutoField()
    network = CharField(unique=True)
    action = CharField(default="deny")
    reason = CharField(default="")
    created_at = DateTimeField(default=datetime.now)


class AuditLog(BaseModel):
    id = AutoField()
    occurred_at = DateTimeField(default=datetime.now, index=True)
    username = CharField(default="", index=True)
    protocol = CharField(default="")
    client_ip = CharField(default="", index=True)
    action = CharField()
    path = TextField(default="")
    result = CharField(default="SUCCESS")
    detail = TextField(default="")


class Setting(BaseModel):
    key = CharField(primary_key=True)
    value = TextField()
    updated_at = DateTimeField(default=datetime.now)
