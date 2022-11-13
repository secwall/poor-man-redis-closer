"""
A simple demo for closer
"""

import argparse
import asyncio
import logging
import time

import docker
import redis
import redis.asyncio as async_redis


class Runner:
    def __init__(self, stop_closer=False):
        self.docker_client = docker.from_env()
        self.containers = self.discover_containers()
        self.tasks = {}
        self._should_stop_closer = stop_closer
        self.log = logging.getLogger(__name__)
        self.counter = 1
        self.recorded = set()

    async def run_load(self, target):
        """
        Run test load against target
        """
        while True:
            try:
                conn = async_redis.Redis(host=target, socket_timeout=0.1)
                await conn.ping()
                # Actually we are running in single thread here
                # So no locks/atomics are required
                value = self.counter
                self.counter += 1
                await conn.set(f'{value}', '1')
                self.recorded.add(f'{value}'.encode('utf-8'))
            except asyncio.CancelledError:
                return
            except Exception as exc:
                self.log.debug('Inserting for %s failed: %r', target, exc)
            await asyncio.sleep(0.1)

    def discover_containers(self):
        """
        Get a map of name -> docker container
        """
        res = {}
        for container in self.docker_client.containers.list():
            if container.labels.get('com.docker.compose.project') == 'poor-man-redis-closer':
                service = container.labels['com.docker.compose.service']
                if 'host' not in service:
                    continue
                res[service] = container
        return res

    def stop_closer(self):
        """
        Stop closer in containers
        """
        for name, container in self.containers.items():
            res = container.exec_run('supervisorctl stop closer')
            if res.exit_code != 0:
                raise RuntimeError(f'Unable to stop closer in {name}: {res.output}')

    def wait_redis(self):
        """
        Wait for host1 to become primary with 2 replicas
        """
        timeout = 60
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                ready = True
                conn = redis.Redis(host='host1')
                info = conn.info('replication')
                if info['connected_slaves'] != 2:
                    ready = False
                for host in ['host2', 'host3']:
                    replica_conn = redis.Redis(host=host)
                    info = replica_conn.info('replication')
                    if info['master_link_status'] != 'up':
                        ready = False
                    sentinel_conn = redis.Redis(host=host, port=26379)
                    replicas = sentinel_conn.sentinel_slaves('demo')
                    if len(replicas) != 2:
                        ready = False
                sentinel_conn = redis.Redis(host='host2', port=26379)
                status = sentinel_conn.sentinel_sentinels('demo')
                if len(status) != 2:
                    ready = False
                if ready:
                    return
            except Exception as exc:
                self.log.warning('Waiting for redis to become ready: %r', exc)
            time.sleep(1)
        raise RuntimeError('host1 is not ready')

    def wait_single_primary(self):
        """
        Wait for single primary with 2 replicas
        """
        timeout = 180
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                primaries = []
                for name in self.containers:
                    conn = redis.Redis(host=name, socket_timeout=0.1)
                    info = conn.info('replication')
                    if info['role'] == 'master':
                        primaries.append(name)
                if len(primaries) == 1:
                    return primaries[0]
                self.log.info('Waiting for single primary. Primaries: %s', ', '.join(primaries))
            except Exception as exc:
                self.log.debug('Waiting for single primary: %r', exc)
            time.sleep(1)
        raise RuntimeError('No single primary after network healing')

    def isolate(self, target):
        """
        Isolate container from other hosts
        """
        target_container = self.containers[target]
        addr = target_container.attrs['NetworkSettings']['Networks']['poor-man-redis-closer_default']['IPAddress']
        for name, container in self.containers.items():
            if name != target:
                res = container.exec_run(f'iptables -t filter -I INPUT -s {addr} -j DROP')
                if res.exit_code != 0:
                    raise RuntimeError(f'Unable to close {name} from {target}')
                res = container.exec_run(f'iptables -t filter -I OUTPUT -d {addr} -j DROP')
                if res.exit_code != 0:
                    raise RuntimeError(f'Unable to close {target} from {name}')

    def open(self, target):
        """
        Open container for other hosts
        """
        for name, container in self.containers.items():
            if name != target:
                res = container.exec_run('iptables -t filter -F INPUT')
                if res.exit_code != 0:
                    raise RuntimeError(f'Unable to open {name} for {target}')
                res = container.exec_run('iptables -t filter -F OUTPUT')
                if res.exit_code != 0:
                    raise RuntimeError(f'Unable to open {target} for {name}')

    def count_lost(self, primary):
        """
        Count lost record
        """
        conn = redis.Redis(host=primary)
        on_primary = set(conn.keys())
        lost = self.recorded.difference(on_primary)
        print(f'Lost keys {len(lost)}/{len(self.recorded)}')

    async def load(self):
        """
        Async part of run
        """
        for host in self.containers:
            self.tasks[host] = asyncio.create_task(self.run_load(host))
        print('Isolating host1')
        self.isolate('host1')
        print('Waiting for 10 minutes')
        await asyncio.sleep(600)
        for task in self.tasks.values():
            task.cancel()

    def run(self):
        """
        Run demo
        """
        self.wait_redis()
        if self._should_stop_closer:
            self.stop_closer()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.load())
        self.open('host1')
        print('Waiting for single primary after network heal')
        primary = self.wait_single_primary()
        self.count_lost(primary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-closer', action='store_true', help='Stop closer before running load')
    args = parser.parse_args()
    runner = Runner(args.no_closer)
    runner.run()
