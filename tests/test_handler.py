import logging
from logging import LogRecord
from unittest import mock

import pytest

from firehose_handler.handler import FirehoseHandler


class TestFirehoseHandler:
    @pytest.fixture
    @mock.patch('firehose_handler.handler.boto3.Session')
    def handler(self, _):
        return FirehoseHandler(
            profile_name='Profile Name',
            region_name='Region Name',
            delivery_stream_name='Delivery Stream Name',
        )

    @pytest.fixture
    def log_record(self):
        return LogRecord(
            name='Test Logger',
            level=logging.ERROR,
            pathname='/python/test/path/module.py',
            lineno=55,
            msg='Value Error',
            args=None,
            exc_info=None,
        )

    @mock.patch('firehose_handler.handler.boto3.Session')
    def test_init(self, mock_session):
        mock_session_instance = mock.Mock()
        mock_session.return_value = mock_session_instance

        mock_client = mock.Mock()
        mock_session_instance.client = mock_client

        mock_firehose = mock.Mock()
        mock_client.return_value = mock_firehose

        handler = FirehoseHandler(
            profile_name='Profile Name',
            region_name='Region Name',
            delivery_stream_name='Delivery Stream Name',
        )

        mock_session.assert_called_once_with(
            profile_name='Profile Name',
            region_name='Region Name',
        )
        mock_client.assert_called_once_with(service_name='firehose')

        assert handler.firehose == mock_firehose
        assert handler.delivery_stream_name == 'Delivery Stream Name'
        assert handler.record is None

    @mock.patch('firehose_handler.handler.FirehoseHandler.flush')
    @mock.patch('firehose_handler.handler.FirehoseHandler.format')
    def test_emit(self, mock_format, mock_flush, log_record, handler):
        mock_format.return_value = 'Formatted Message'

        handler.emit(log_record)

        mock_format.assert_called_once_with(log_record)
        assert handler.record == b'Formatted Message'
        mock_flush.assert_called_once_with()

    @mock.patch('firehose_handler.handler.FirehoseHandler.handleError')
    @mock.patch('firehose_handler.handler.FirehoseHandler.flush')
    @mock.patch('firehose_handler.handler.FirehoseHandler.format')
    def test_emit_raise_exception(
        self, mock_format, mock_flush, mock_handle_error, log_record, handler
    ):
        mock_format.side_effect = Exception('Unknown Error Occurred')

        handler.emit(log_record)

        mock_format.assert_called_once_with(log_record)
        assert handler.record is None
        mock_flush.assert_not_called()
        mock_handle_error.assert_called_once_with(log_record)

    @mock.patch('firehose_handler.handler.FirehoseHandler.release')
    @mock.patch('firehose_handler.handler.FirehoseHandler.acquire')
    def test_flush(self, mock_acquire, mock_release, handler):
        mock_put_record = mock.Mock()
        handler.firehose.put_record = mock_put_record
        handler.record = b'Formatted Message'

        handler.flush()

        mock_acquire.assert_called_once_with()
        mock_put_record.assert_called_once_with(
            DeliveryStreamName='Delivery Stream Name',
            Record={'Data': b'Formatted Message'},
        )
        assert handler.record is None
        mock_release.assert_called_once_with()

    @mock.patch('firehose_handler.handler.FirehoseHandler.release')
    @mock.patch('firehose_handler.handler.FirehoseHandler.acquire')
    def test_flush_raise_exception(self, mock_acquire, mock_release, handler):
        mock_put_record = mock.Mock()
        handler.firehose.put_record = mock_put_record
        mock_put_record.side_effect = Exception('Unexpected Error Occured')
        handler.record = b'Formatted Message'

        with pytest.raises(Exception):
            handler.flush()

        mock_acquire.assert_called_once_with()
        mock_put_record.assert_called_once_with(
            DeliveryStreamName='Delivery Stream Name',
            Record={'Data': b'Formatted Message'},
        )
        assert handler.record is None
        mock_release.assert_called_once_with()

    def test_repr(self, handler):
        assert repr(handler) == '[FirehoseHandler] Delivery Stream Name'
