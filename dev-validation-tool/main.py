import argparse
import toml
import numpy as np
import os
import shutil
import time
from loguru import logger 
from watchdog.events import *
from watchdog.observers import Observer

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir',help = "numpy data dir", default="/tmp/ub/")
    parser.add_argument('--confpath',help = "config path", default="ubconfig.toml")
    args = parser.parse_args()
    return args


class EventHandler(FileSystemEventHandler):
    def __init__(self, datadir, confpath):
        FileSystemEventHandler.__init__(self)
        self.datadir = datadir
        self.confpath = confpath
        self.round = 0
    
    def on_moved(self, event):
        logger.debug("on_moved")
        self.check_and_print()

    def on_created(self, event):
        logger.debug("on_created")
        self.check_and_print()

    def on_deleted(self, event):
        logger.debug("on_deleted")
        self.check_and_print()
    
    def on_modified(self, event):
        logger.debug("on_modified")
        self.check_and_print()

    def load_file(self, name):
        try:
            data = np.load(os.path.join(self.datadir, name+".npy"))
            if data is None:
                data = np.load(os.path.join(self.datadir, name))

            if data is None:
                logger.error(f"load {name} failed")
        
            return data
        except Exception as e:
            logger.error(e)
            return None

    def check_and_print(self):
        logger.info(f"")
        logger.info(f"-------------- {self.round} ------------")
        conf = toml.load(self.confpath)
        if conf is None:
            logger.error(f"parse conf {self.confpath} is None")
            return
        
        data = conf["data"]
        logger.info(f"data pairs {len(data)}")

        for idx,pair in enumerate(data):
            if type(pair) is not list:
                logger.error(f"idx {idx} is {type(pair)}")
                continue
            
            if len(pair) != 2:
                logger.error(f"len of idx {idx} is {len(pair)}")
                continue
            
            left = self.load_file(pair[0])
            right = self.load_file(pair[1])
        
            if left is None or right is None:
                continue

            left = left.reshape(-1)
            right = right.reshape(-1)

            same = np.allclose(left, right, rtol=conf['rtol'], atol=conf['atol'])
            logger.info(f"{pair[0]} \t vs {pair[1]} \t {same}")
            if not same:
                diff = left - right
                logger.error(f"max diff {diff.max()}")

        self.round += 1

def main():
    args = parse_args()

    if not os.path.exists(args.confpath):
        shutil.copy("config.toml", args.confpath)
    if not os.path.isfile(args.confpath):
        logger.error(f"{args.confpath} already exists, but not a file")
        return

    if not os.path.exists(args.datadir):
        os.mkdir(args.datadir)
    if not os.path.isdir(args.datadir):
        logger.error(f"{args.datadir} already exists, but not a dir")
        return

    observer = Observer()
    handler = EventHandler(args.datadir, args.confpath)
    observer.schedule(handler, args.datadir, False)
    observer.schedule(handler, args.confpath, False)
    observer.schedule(handler, ".", False)


    observer.start()
    logger.info(f"start serving on {args.confpath} and {args.datadir}...")
    try:
        while True:
            time.sleep(3)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
