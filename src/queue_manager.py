#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: adapter_db

:Synopsis:
    Database model to support queueing objects from PASTA for use by the
    PASTA+ GMN Adapter.
 
:Author:
    servilla

:Created:
    3/2/17
"""
import os

import daiquiri
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import properties


logger = daiquiri.getLogger(__name__)

Base = declarative_base()


class Queue(Base):
    """
    SQLAlchemy ORM for adapter queue
    """
    __tablename__ = 'queue'

    package = Column(String, primary_key=True)
    scope = Column(String, nullable=False)
    identifier = Column(Integer, nullable=False)
    revision = Column(Integer, nullable=False)
    method = Column(String, primary_key=True)
    datetime = Column(DateTime, nullable=False)
    owner = Column(String, nullable=False)
    doi = Column(String, nullable=False)
    dequeued = Column(Boolean, nullable=False, default=False)


class QueueManager(object):
    """
    Queue management class for the adapter queue
    """
    def __init__(self, queue=properties.QUEUE):
        self.queue = queue
        db = 'sqlite:///' + self.queue
        engine = create_engine(db)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def delete_queue(self):
        """
        Removes the sqlite database from the file system
        :return:
        """
        os.remove(self.queue)

    def dequeue(self, package=None, method=None):
        """
        Sets the PASTA event in the adapter queue to "dequeued"

        :param package: The PASTA data package identifier
        :param method: The PASTA event method type
        :return: None
        """
        try:
            event = self.session.query(Queue).filter(
                Queue.package == package,
                Queue.method == method).one()
            event.dequeued = True
            self.session.commit()
        except NoResultFound as e:
            p = package
            logger.error('{e} - {p}'.format(e=e, p=p))

    def enqueue(self, event=None):
        """
        Enters the PASTA event onto the adapter queue

        :param event: Instance of utility Event class
        :return: None
        """
        scope, identifier, revision = event.package.split('.')

        event = Queue(
            package=event.package,
            scope=scope,
            identifier=identifier,
            revision=revision,
            method=event.method,
            datetime=event.datetime,
            owner=event.owner,
            doi=event.doi
        )
        try:
            self.session.add(event)
            self.session.commit()
        except IntegrityError as e:
            logger.error(e)
            self.session.rollback()

    def get_count(self):
        """
        Returns the event record count of the adapter queue

        :return: Event record count scalar
        """
        return self.session.query(func.count(Queue.package)).scalar()

    def get_event(self, package=None, method=None):
        """
        Returns the adapter queue event record for the given package and method

        :param package: The PASTA data package identifier
        :param method: The PASTA event method type
        :return: Adapter queue event record object
        """
        try:
            return self.session.query(Queue).filter(
                Queue.package == package,
                Queue.method == method).one()
        except NoResultFound as e:
            p = package
            logger.error('{e} - {p}'.format(e=e, p=p))

    def get_head(self):
        """
        Returns the head event record of the adapter queue (that is not set
        to "dequeued")

        :return: Head event record
        """
        return self.session.query(Queue).filter(
            Queue.dequeued == False).order_by(Queue.datetime).first()

    def get_last_datetime(self):
        """
        Return the datetime of the last adapter queue entry

        :return: Last datetime object of queue
        """
        datetime = None
        event = self.session.query(Queue).order_by(desc(Queue.datetime)).first()
        if event is not None:
            datetime = event.datetime
        return datetime

    def get_predecessor(self, package=None):
        """
        Return the first predecessor of the event package

        :param event_package: Package instance of event package
        :return: Predecessor as event record or None if none found
        """
        scope, identifier, revision = package.split('.')
        return self.session.query(Queue).filter(Queue.scope == scope,
                    Queue.identifier == identifier,
                    Queue.revision < revision).order_by(
                    desc(Queue.revision)).first()

    def is_dequeued(self, package=None, method=None):
        """
        Returns boolean of dequeued status of the specific package and method

        :param package: The PASTA data package identifier
        :param method: The PASTA event method type
        :return: Boolean of dequeued status
        """
        dequeued = None
        try:
            event = self.session.query(Queue).filter(
                Queue.package == package,
                Queue.method == method).one()
            dequeued = event.dequeued
        except NoResultFound as e:
            p = package
            logger.error('{e} - {p}'.format(e=e, p=p))
        return dequeued


def main():
    return 0


if __name__ == "__main__":
    main()
