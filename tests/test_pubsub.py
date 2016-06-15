# -*- coding: utf-8 -*-

import pytest
from wood.pubsub import redis_pubsub_factory

use_redis = pytest.mark.skipif(not pytest.config.getoption("--redis"), reason="need --runslow option to run")


@use_redis
def test_redis_pubsub(event_loop):
    channel = '1'
    publish_message = 'Hello World!'
    subscriber, publisher = redis_pubsub_factory(event_loop)
    event_loop.run_until_complete(subscriber.connect())
    event_loop.run_until_complete(publisher.connect())
    subscriber.subscribe(channel)
    event_loop.run_until_complete(publisher.publish(channel, publish_message))
    _, response_message = event_loop.run_until_complete(subscriber.get())
    assert publish_message == response_message


@use_redis
def test_redis_dont_get_unsubscribed_messages(event_loop):
    subscriber, publisher = redis_pubsub_factory(event_loop)
    event_loop.run_until_complete(subscriber.connect())
    event_loop.run_until_complete(publisher.connect())
    subscriber.subscribe('2')
    event_loop.run_until_complete(publisher.publish('1', 'Message#1'))
    event_loop.run_until_complete(publisher.publish('2', 'Message#2'))
    _, response_message = event_loop.run_until_complete(subscriber.get())
    assert "Message#2" == response_message


@use_redis
def test_redis_subscribe_to_multiple_channels(event_loop):
    subscriber, publisher = redis_pubsub_factory(event_loop)
    event_loop.run_until_complete(subscriber.connect())
    event_loop.run_until_complete(publisher.connect())
    subscriber.subscribe('1')
    subscriber.subscribe('2')
    event_loop.run_until_complete(publisher.publish('1', 'Message#1'))
    event_loop.run_until_complete(publisher.publish('2', 'Message#2'))
    channel1, response_message1 = event_loop.run_until_complete(subscriber.get())
    channel2, response_message2 = event_loop.run_until_complete(subscriber.get())
    assert "Message#1" == response_message1
    assert "Message#2" == response_message2
