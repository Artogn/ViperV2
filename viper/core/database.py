# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

from __future__ import unicode_literals  # make all strings unicode in python2
from datetime import datetime
import json

from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from viper.common.out import *
from viper.common.objects import File, Singleton
from viper.core.project import __project__
from viper.core.config import Config

cfg = Config()

Base = declarative_base()

project_name = __project__.name
if project_name == None:
    project_name = 'default'

association_table = Table(
    '{0}_association'.format(project_name),
    Base.metadata,
    Column('tag_id', Integer, ForeignKey('{0}_tag.id'.format(project_name))),
    Column('note_id', Integer, ForeignKey('{0}_note.id'.format(project_name))),
    Column('malware_id', Integer, ForeignKey('{0}_malware.id'.format(project_name))),
    Column('analysis_id', Integer, ForeignKey('{0}_analysis.id'.format(project_name)))
)


class Malware(Base):
    __tablename__ = '{0}_malware'.format(project_name)

    id = Column(Integer(), primary_key=True)
    name = Column(String(255), nullable=True)
    size = Column(Integer(), nullable=False)
    type = Column(Text(), nullable=True)
    mime = Column(String(255), nullable=True)
    md5 = Column(String(32), nullable=False, index=True)
    crc32 = Column(String(8), nullable=False)
    sha1 = Column(String(40), nullable=False)
    sha256 = Column(String(64), nullable=False, index=True)
    sha512 = Column(String(128), nullable=False)
    ssdeep = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=False), default=datetime.now(), nullable=False)
    parent_id = Column(Integer(), ForeignKey('{0}_malware.id'.format(project_name)))
    parent = relationship('Malware', lazy='subquery', remote_side=[id])

    tag = relationship(
        'Tag',
        lazy='subquery',
        secondary=association_table,
        backref=backref('{0}_malware'.format(project_name))
    )
    note = relationship(
        'Note',
        lazy='subquery',
        cascade='all, delete',
        secondary=association_table,
        backref=backref('{0}_malware'.format(project_name))
    )
    analysis = relationship(
        'Analysis',
        lazy='subquery',
        cascade='all, delete',
        secondary=association_table,
        backref=backref('{0}_malware'.format(project_name))
    )
    __table_args__ = (Index(
        '{0}_hash_index'.format(project_name),
        'md5',
        'crc32',
        'sha1',
        'sha256',
        'sha512',
        unique=True
    ),)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Malware('{0}','{1}')>".format(self.id, self.md5)

    def __init__(self,
                 md5,
                 crc32,
                 sha1,
                 sha256,
                 sha512,
                 size,
                 type=None,
                 mime=None,
                 ssdeep=None,
                 name=None,
                 parent=None):
        self.md5 = md5
        self.sha1 = sha1
        self.crc32 = crc32
        self.sha256 = sha256
        self.sha512 = sha512
        self.size = size
        self.type = type
        self.mime = mime
        self.ssdeep = ssdeep
        self.name = name
        self.parent = parent


class Tag(Base):
    __tablename__ = '{0}_tag'.format(project_name)

    id = Column(Integer(), primary_key=True)
    tag = Column(String(255), nullable=False, unique=True, index=True)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Tag ('{0}','{1}'>".format(self.id, self.tag)

    def __init__(self, tag):
        self.tag = tag


class Note(Base):
    __tablename__ = '{0}_note'.format(project_name)

    id = Column(Integer(), primary_key=True)
    title = Column(String(255), nullable=True)
    body = Column(Text(), nullable=False)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Note ('{0}','{1}'>".format(self.id, self.title)

    def __init__(self, title, body):
        self.title = title
        self.body = body


class Analysis(Base):
    __tablename__ = '{0}_analysis'.format(project_name)

    id = Column(Integer(), primary_key=True)
    cmd_line = Column(String(255), nullable=True)
    results = Column(Text(), nullable=False)
    stored_at = Column(DateTime(timezone=False), default=datetime.now(), nullable=False)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Note ('{0}','{1}'>".format(self.id, self.cmd_line)

    def __init__(self, cmd_line, results):
        self.cmd_line = cmd_line
        self.results = results


class Ticket(Base):
    __tablename__ = '{0}_ticket'.format(project_name)

    id = Column(Integer(), primary_key=True)
    title = Column(String(255), nullable=True)
    description = Column(Text(), nullable=False)
    created_at = Column(DateTime(timezone=False), default=datetime.now(), nullable=False)

    def to_dict(self):
        row_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            row_dict[column.name] = value

        return row_dict

    def __repr__(self):
        return "<Ticket ('{0}','{1}'>".format(self.id, self.title)

    def __init__(self, title, description):
        self.title = title
        self.description = description


class Database:
    # __metaclass__ = Singleton

    def __init__(self):
        connection_string = cfg.database.conn_string

        if not connection_string:
            db_path = os.path.join(__project__.get_path(), 'viper.db')
            self.engine = create_engine('sqlite:///{0}'.format(db_path), poolclass=NullPool)
        else:
            self.engine = create_engine(connection_string, poolclass=NullPool)
        self.engine.echo = False
        self.engine.pool_timeout = 60

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def __del__(self):
        self.engine.dispose()

    def add_tags(self, sha256, tags):
        session = self.Session()

        malware_entry = session.query(Malware).filter(Malware.sha256 == sha256).first()
        if not malware_entry:
            return

        tags = tags.strip()
        if ',' in tags:
            tags = tags.split(',')
        else:
            tags = tags.split()

        for tag in tags:
            tag = tag.strip().lower()
            if tag == '':
                continue

            try:
                malware_entry.tag.append(Tag(tag))
                session.commit()
            except IntegrityError as e:
                session.rollback()
                try:
                    malware_entry.tag.append(session.query(Tag).filter(Tag.tag == tag).first())
                    session.commit()
                except SQLAlchemyError:
                    session.rollback()

    def list_tags(self):
        session = self.Session()
        rows = session.query(Tag).all()
        return rows

    def delete_tag(self, tag_name, sha256):
        session = self.Session()
        
        try:
            # First remove the tag from the sample
            malware_entry = session.query(Malware).filter(Malware.sha256 == sha256).first()
            tag = session.query(Tag).filter(Tag.tag == tag_name).first()
            try:
                malware_entry = session.query(Malware).filter(Malware.sha256 == sha256).first()
                malware_entry.tag.remove(tag)
                session.commit()
            except:
                print_error("Tag {0} does not exist for this sample".format(tag_name))
            # If tag has no entries drop it
            count = len(self.find('tag', tag_name))
            if count == 0:
                session.delete(tag)
                session.commit()
                print_warning("Tag {0} has no additional entries dropping from Database".format(tag_name))
        except SQLAlchemyError as e:
            print_error("Unable to delete tag: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def add_note(self, sha256, title, body):
        session = self.Session()

        malware_entry = session.query(Malware).filter(Malware.sha256 == sha256).first()
        if not malware_entry:
            return

        try:
            malware_entry.note.append(Note(title, body))
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to add note: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def get_note(self, note_id):
        session = self.Session()
        note = session.query(Note).get(note_id)
        return note

    def edit_note(self, note_id, body):
        session = self.Session()

        try:
            session.query(Note).get(note_id).body = body
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to update note: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def delete_note(self, note_id):
        session = self.Session()

        try:
            note = session.query(Note).get(note_id)
            session.delete(note)
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to delete note: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def add(self, obj, name=None, tags=None, parent_sha=None):
        session = self.Session()

        if not name:
            name = obj.name

        if parent_sha:
            parent_sha = session.query(Malware).filter(Malware.sha256 == parent_sha).first()

        if isinstance(obj, File):
            try:
                malware_entry = Malware(md5=obj.md5,
                                        crc32=obj.crc32,
                                        sha1=obj.sha1,
                                        sha256=obj.sha256,
                                        sha512=obj.sha512,
                                        size=obj.size,
                                        type=obj.type,
                                        mime=obj.mime,
                                        ssdeep=obj.ssdeep,
                                        name=name,
                                        parent=parent_sha)
                print malware_entry
                session.add(malware_entry)
                session.commit()
            except IntegrityError:
                session.rollback()
                malware_entry = session.query(Malware).filter(Malware.md5 == obj.md5).first()
            except SQLAlchemyError as e:
                print_error("Unable to store file: {0}".format(e))
                session.rollback()
                return False

        if tags:
            self.add_tags(sha256=obj.sha256, tags=tags)

        return True

    def delete_file(self, id):
        session = self.Session()

        try:
            malware = session.query(Malware).get(id)
            if not malware:
                print_error("The opened file doesn't appear to be in the database, have you stored it yet?")
                return

            session.delete(malware)
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to delete file: {0}".format(e))
            session.rollback()
            return False
        finally:
            session.close()

        return True

    def find(self, key, value=None, offset=0):
        session = self.Session()
        offset = int(offset)
        rows = None

        if key == 'all':
            rows = session.query(Malware).all()
        elif key == 'latest':
            if value:
                try:
                    value = int(value)
                except ValueError:
                    print_error("You need to specify a valid number as a limit for your query")
                    return None
            else:
                value = 5

            rows = session.query(Malware).order_by(Malware.id.desc()).limit(value).offset(offset)
        elif key == 'md5':
            rows = session.query(Malware).filter(Malware.md5 == value).all()
        elif key == 'sha1':
            rows = session.query(Malware).filter(Malware.sha1 == value).all()
        elif key == 'sha256':
            rows = session.query(Malware).filter(Malware.sha256 == value).all()
        elif key == 'tag':
            rows = session.query(Malware).filter(Malware.tag.any(Tag.tag == value.lower())).all()
        elif key == 'name':
            if '*' in value:
                value = value.replace('*', '%')
            else:
                value = '%{0}%'.format(value)

            rows = session.query(Malware).filter(Malware.name.like(value)).all()
        elif key == 'note':
            value = '%{0}%'.format(value)
            rows = session.query(Malware).filter(Malware.note.any(Note.body.like(value))).all()
        elif key == 'type':
            rows = session.query(Malware).filter(Malware.type.like('%{0}%'.format(value))).all()
        elif key == 'mime':
            rows = session.query(Malware).filter(Malware.mime.like('%{0}%'.format(value))).all()
        else:
            print_error("No valid term specified")

        return rows

    def get_sample_count(self):
        session = self.Session()
        return session.query(Malware.id).count()

    def add_parent(self, malware_sha256, parent_sha256):
        session = self.Session()

        # try:
        if True:
            malware = session.query(Malware).filter(Malware.sha256 == malware_sha256).first()
            malware.parent = session.query(Malware).filter(Malware.sha256 == parent_sha256).first()
            session.commit()

            # except SQLAlchemyError as e:
            # print_error("Unable to add parent: {0}".format(e))
            # session.rollback()
            # finally:
            # session.close()

    def delete_parent(self, malware_sha256):
        session = self.Session()

        # try:
        if True:
            malware = session.query(Malware).filter(Malware.sha256 == malware_sha256).first()
            malware.parent = None
            session.commit()

            # except SQLAlchemyError as e:
            # print_error("Unable to add parent: {0}".format(e))
            # session.rollback()
            # finally:
            # session.close()

    def get_children(self, parent_id):
        session = self.Session()
        children = session.query(Malware).filter(Malware.parent_id == parent_id).all()
        child_samples = ''
        for child in children:
            child_samples += '{0},'.format(child.sha256)
        return child_samples

    # Store Module / Cmd Output
    def add_analysis(self, sha256, cmd_line, results):
        results = json.dumps(results)
        session = self.Session()

        malware_entry = session.query(Malware).filter(Malware.sha256 == sha256).first()
        if not malware_entry:
            return
        try:
            malware_entry.analysis.append(Analysis(cmd_line, results))
            session.commit()
        except SQLAlchemyError as e:
            print_error("Unable to store analysis: {0}".format(e))
            session.rollback()
        finally:
            session.close()

    def get_analysis(self, analysis_id):
        session = self.Session()
        analysis = session.query(Analysis).get(analysis_id)
        return analysis
