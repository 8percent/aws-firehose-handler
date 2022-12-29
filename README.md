# AWS Firehose Handler

![Build](https://github.com/8percent/aws-firehose-handler/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/8percent/aws-firehose-handler/branch/master/graph/badge.svg?token=QKO8M4RLO6)](https://codecov.io/gh/8percent/aws-firehose-handler)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


Python logging handler to load data into AWS Kinesis Delivery Stream

### Demo Script
```
import logging.config

CONFIG = {
    'version': 1,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s %(process)d %(processName)s %(thread)d %(threadName)s'
        },
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s %(process)d %(processName)s %(thread)d %(threadName)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'firehose': {
            'level': 'INFO',
            'formatter': 'json',
            'class': 'firehose_handler.FirehoseHandler',
            'profile_name': 'Insert AWS Credential Profile Name',
            'region_name': 'Insert AWS Region Name',
            'delivery_stream_name': 'Insert Delivery Stream Name',
        },
    },
    'loggers': {
        'test-logger': {
            'handlers': ['firehose'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

logging.config.dictConfig(CONFIG)
logger = logging.getLogger('test-logger')


def test():
    try:
        raise NameError("fake NameError")
    except NameError as e:
        logger.error(e, exc_info=True)


if __name__ == '__main__':
    test()
```
