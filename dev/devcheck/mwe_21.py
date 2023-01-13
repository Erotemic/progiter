import ubelt as ub
cap = ub.CaptureStdout()

with cap:
    from random import randint
    from time import time, sleep
    import progiter

    start = time()
    for i in progiter.ProgIter(range(100)):
        sleep(i/10000)
    print(time() - start)

import re
import sys
parts = re.split('(\r)', cap.text)
print('parts = {}'.format(ub.repr2(parts, nl=1)))

print(f'Slowly show progression of bug: ({len(parts)} steps)')
for p in parts:
    sleep(1)
    sys.stdout.write(p)
    sys.stdout.flush()
