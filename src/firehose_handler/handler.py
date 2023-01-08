from logging import Handler

import boto3


class FirehoseHandler(Handler):
    def __init__(self, profile_name, region_name, delivery_stream_name):
        super().__init__()

        self.record = None

        session = boto3.Session(
            profile_name=profile_name,
            region_name=region_name,
        )
        self.firehose = session.client(service_name='firehose')
        self.delivery_stream_name = delivery_stream_name

    def emit(self, record):
        try:
            msg = self.format(record)
            self.record = msg.encode(encoding='UTF-8')
            self.flush()
        except Exception:
            self.handleError(record)

    def flush(self):
        self.acquire()
        try:
            if self.record is not None:
                try:
                    self.firehose.put_record(
                        DeliveryStreamName=self.delivery_stream_name,
                        Record={'Data': self.record},
                    )
                finally:
                    self.record = None
        finally:
            self.release()

    def __repr__(self):
        return f'[{self.__class__.__name__}] {self.delivery_stream_name}'
