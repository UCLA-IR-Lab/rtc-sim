import argparse
import multiprocessing
import time
from pathlib import Path

import toml

from .archon import Archon
from .redis import Redis
from .mmap import Mmap

config_path = str(Path().absolute()) + "/config.toml"
config = toml.load(open(config_path))

archon_address = config['archon']['address']
archon_port = config['archon']['port']
archon_timeout = config['archon']['timeout']
archon_delay = config['archon']['delay']

redis_address = config['redis']['address']
redis_port = config['redis']['port']
redis_password = config['redis']['password']
redis_database = config['redis']['database']
redis_unix_socket_path = config['redis']['unix_socket_path']

mmap_file_path = config['mmap']['file_path']

def read_archon():
    archon = Archon(archon_address, archon_port, archon_timeout)
    timer = archon.get_timer()
    archon.close()
    
    return timer

def connect_redis(type):
    return Redis(type=type, address=redis_address, port=redis_port, us_path=redis_unix_socket_path, password=redis_password, database=redis_database)

def write_rtc(mode, verif_dict, shm):
    timer = read_archon()
    
    if mode == 'redis_tcp':
        redis = connect_redis(0)
        redis.set_timer(timer)
    elif mode == 'redis_us':
        redis = connect_redis(1)
        redis.set_timer(timer)
    elif mode == 'mmap':
        mmap_cls.write_short(0, timer)
    else:
        shm.value = timer
    
    verif_dict['w'] = timer
    
def read_rtc(mode, verif_dict, shm, delay):
    time.sleep(delay)
    
    timer = 0
    
    if mode == 'redis_tcp':
        redis = connect_redis(0)
        timer = redis.get_timer()
    elif mode == 'redis_us':
        redis = connect_redis(1)
        timer = redis.get_timer()
    elif mode == 'mmap':
        timer = mmap_cls.read_short(0)
    else:
        timer = shm.value  
    verif_dict['r'] = timer

def rtc_simulation(mode, hz):
    delay = 1/hz + archon_delay
    
    manager = multiprocessing.Manager()
    verif_dict = manager.dict()
    
    shm = multiprocessing.Value('q', 0)
    
    i, matched_ctr = 0, 0
    
    while i < 100:
        write_process = multiprocessing.Process(name="write", target=write_rtc, args=(mode, verif_dict, shm,))
        read_process = multiprocessing.Process(name="read", target=read_rtc, args=(mode, verif_dict, shm, delay))
        write_process.start()
        read_process.start()
        write_process.join()
        read_process.join()

        if verif_dict['w'] == verif_dict['r']:
            matched_ctr += 1
            
        i += 1
        
    return matched_ctr

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="Example: python -m rtc_sim --mode mmap")
    parser.add_argument('--mode', choices=['redis_tcp', 'redis_us', 'mmap', 'shm'])    
    args = parser.parse_args()

    mode = args.mode
    
    if mode == 'mmap':
        mmap_cls = Mmap(mmap_file_path)
    
    # hertz = [25, 50, 75, 100, 125, 150, 175, 200, 225, 250,
    #          275, 300, 325, 350, 375, 400, 425, 450, 475, 500]
    hertz = [400, 425, 450, 475, 500]
    
    for hz in hertz:
        matched_ctrs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i, _ in enumerate(matched_ctrs):
            matched_ctr = rtc_simulation(mode, hz)
            matched_ctrs[i] = matched_ctr
        
        print(f"{hz}Hz: {sum(matched_ctrs)/len(matched_ctrs)}")