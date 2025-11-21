import ray
import time

ray.init(num_cpus=4)

@ray.remote
def task_running_300_seconds():
    print("Start!")
    time.sleep(300)

@ray.remote
class Actor:
    def __init__(self):
        print("Actor created")

# Create 2 tasks
tasks = [task_running_300_seconds.remote() for _ in range(2)]

# Create 2 actors
actors = [Actor.remote() for _ in range(2)]

ray.get(tasks)