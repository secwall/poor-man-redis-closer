# Closing partitioned redis primary from load

This is an example of method used in Yandex Cloud before introduction of RDSync.

## Requirements

* Docker
* GNU Make
* Python >= 3.10 (tox and Python 3.11 for tests)

## Running demo

With using closer:
```
make demo-with-closer
```

Without using closer:
```
make demo-without-closer
```

One would see results like `Lost keys 29/4947` in first case and `Lost keys 5121/9978` in second.

## Caveats

This is just an example of losing less data with redis.
Code here is not production ready (and it is intended).
Consider using [WAIT](https://redis.io/commands/wait) in application if closing
from load for partitioned primary is used.
