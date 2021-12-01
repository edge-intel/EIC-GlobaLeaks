# -*- coding: UTF-8
from globaleaks.db.migrations.update import MigrationBase
from globaleaks.handlers.admin.operation import db_reset_smtp_settings
from globaleaks.models import Model
from globaleaks.models.enums import *
from globaleaks.models.properties import *
from globaleaks.utils.utility import datetime_now, datetime_null, datetime_never


class InternalTip_v_57(Model):
    __tablename__ = 'internaltip'
    id = Column(UnicodeText(36), primary_key=True, default=uuid4)
    tid = Column(Integer, default=1, nullable=False)
    creation_date = Column(DateTime, default=datetime_now, nullable=False)
    update_date = Column(DateTime, default=datetime_now, nullable=False)
    context_id = Column(UnicodeText(36), nullable=False)
    progressive = Column(Integer, default=0, nullable=False)
    https = Column(Boolean, default=False, nullable=False)
    mobile = Column(Boolean, default=False, nullable=False)
    total_score = Column(Integer, default=0, nullable=False)
    expiration_date = Column(DateTime, default=datetime_never, nullable=False)
    enable_two_way_comments = Column(Boolean, default=True, nullable=False)
    enable_two_way_messages = Column(Boolean, default=True, nullable=False)
    enable_attachments = Column(Boolean, default=True, nullable=False)
    enable_whistleblower_identity = Column(Boolean, default=False, nullable=False)
    important = Column(Boolean, default=False, nullable=False)
    label = Column(UnicodeText, default='', nullable=False)
    wb_last_access = Column(DateTime, default=datetime_now, nullable=False)
    status = Column(UnicodeText(36), nullable=True)
    substatus = Column(UnicodeText(36), nullable=True)
    crypto_tip_pub_key = Column(UnicodeText(56), default='', nullable=False)


class ReceiverFile_v_57(Model):
    __tablename__ = 'receiverfile'
    id = Column(UnicodeText(36), primary_key=True, default=uuid4)
    internalfile_id = Column(UnicodeText(36), nullable=False)
    receivertip_id = Column(UnicodeText(36), nullable=False)
    filename = Column(UnicodeText(255), nullable=False)
    last_access = Column(DateTime, default=datetime_null, nullable=False)
    new = Column(Boolean, default=True, nullable=False)


class ReceiverTip_v_57(Model):
    __tablename__ = 'receivertip'
    id = Column(UnicodeText(36), primary_key=True, default=uuid4)
    internaltip_id = Column(UnicodeText(36), nullable=False)
    receiver_id = Column(UnicodeText(36), nullable=False)
    last_access = Column(DateTime, default=datetime_null, nullable=False)
    access_counter = Column(Integer, default=0, nullable=False)
    important = Column(Boolean, default=False, nullable=False)
    label = Column(UnicodeText, default='', nullable=False)
    new = Column(Boolean, default=True, nullable=False)
    enable_notifications = Column(Boolean, default=True, nullable=False)
    crypto_tip_prv_key = Column(UnicodeText(84), default='', nullable=False)


class WhistleblowerFile_v_57(Model):
    __tablename__ = 'whistleblowerfile'
    id = Column(UnicodeText(36), primary_key=True, default=uuid4)
    receivertip_id = Column(UnicodeText(36), nullable=False)
    name = Column(UnicodeText, nullable=False)
    filename = Column(UnicodeText(255), unique=True, nullable=False)
    size = Column(Integer, nullable=False)
    content_type = Column(UnicodeText, nullable=False)
    creation_date = Column(DateTime, default=datetime_now, nullable=False)
    last_access = Column(DateTime, default=datetime_null, nullable=False)
    description = Column(UnicodeText, nullable=False)
    new = Column(Boolean, default=True, nullable=False)


class MigrationScript(MigrationBase):
    def migrate_InternalTip(self):
        m = self.model_from['Config']

        tids = [tid[0] for tid in self.session_old.query(m.tid) \
                                      .filter(m.var_name == 'private_annotations',
                                              m.value == True)]

        for old_obj in self.session_old.query(self.model_from['InternalTip']):
            new_obj = self.model_to['InternalTip']()
            for key in new_obj.__table__.columns._data.keys():
                if key == 'tor':
                    setattr(new_obj, key, not getattr(old_obj, 'https'))
                elif key == 'score':
                    setattr(new_obj, key, getattr(old_obj, 'total_score'))
                else:
                    setattr(new_obj, key, getattr(old_obj, key))

            if new_obj.tid in tids:
                for old_rtip in self.session_old.query(self.model_from['ReceiverTip']) \
                                                .filter(self.model_from['ReceiverTip'].internaltip_id == old_obj.id):
                    if old_rtip.important:
                        new_obj.important = True

                    if old_rtip.label:
                        new_obj.label = old_rtip.label

            self.session_new.add(new_obj)

    def migrate_ReceiverTip(self):
        pass

    def migrate_ReceiverFile(self):
        pass

    def migrate_WhistleblowerFile(self):
        pass

    def epilogue(self):
        for model in ['ReceiverTip', 'ReceiverFile', 'WhistleblowerFile']:
            for old_obj in self.session_old.query(self.model_from[model]):
                new_obj = self.model_to[model]()
                for key in new_obj.__table__.columns._data.keys():
                    if key == 'access_date':
                        setattr(new_obj, key, getattr(old_obj, 'last_access'))
                    else:
                        setattr(new_obj, key, getattr(old_obj, key))

                self.session_new.add(new_obj)
