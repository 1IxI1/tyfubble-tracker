import math
from dataclasses import dataclass


BIG_TOP_SHED = range(2, 151)
INC_SHED = range(0, 151)
SMALL_DELTA_SHED = range(0, 136)
SMALL_DIST_SHED = range(0, 156)


@dataclass
class Bubble:
    """state can be 'small', 'increasing', 'decresing'"""
    center: tuple[int, int]
    top: int
    bottom: int
    height: int
    width: int
    is_big: bool = False
    state: str = 'small'
    id: int = -1


class BubbleTracker:
    bubbles: dict[tuple[int, int], Bubble]

    def __init__(self):
        self.bubbles = {}
        self.total_big = 0
        self.last_id = 0

    def add_bubble(self, bubble: Bubble):
        self.bubbles[bubble.center] = bubble

    def update(self, new_bubbles: list[tuple[int, int, int, int, bool]]):
        """Update bubbles with new_bubbles"""
        bubbles_copy = self.bubbles.copy()
        self.bubbles = {}

        found_big_bubble = False
        for rect in new_bubbles:
            x, y, w, h, is_big = rect
            cx, cy = x + w // 2, y + h // 2
            center = (cx, cy)
            new_bubble = Bubble(center, y, y + h, h, w, is_big)
            if is_big and not found_big_bubble:
                for b in bubbles_copy.values():
                    if b.is_big:
                        if b.top - new_bubble.top in BIG_TOP_SHED:
                            new_bubble.id = b.id
                            bubbles_copy.pop(b.center)
                            if new_bubble.bottom - b.bottom in INC_SHED:
                                new_bubble.state = 'increasing'
                            else:
                                new_bubble.state = 'decreasing'
                        else:
                            self.total_big += 1
                            self.last_id += 1
                            new_bubble.id = self.last_id
                            # because it's a new bubble
                            new_bubble.state = 'increasing'

                        self.add_bubble(new_bubble)
                        found_big_bubble = True
                        break
                else:
                    self.total_big += 1
                    self.last_id += 1
                    new_bubble.id = self.last_id
                    self.add_bubble(new_bubble)
                    found_big_bubble = True
            else:
                new_bubble.state = 'small'
                for b in bubbles_copy.values():
                    delta_h = math.fabs(new_bubble.height - b.height)
                    delta_w = math.fabs(new_bubble.width - b.width)
                    # distance between centers of bubbles (pythagoras)
                    dist = math.sqrt(
                            (new_bubble.center[0] - b.center[0]) ** 2 +
                            (new_bubble.center[1] - b.center[1]) ** 2
                        )
                    if delta_h in SMALL_DELTA_SHED and \
                       delta_w in SMALL_DELTA_SHED and \
                       dist in SMALL_DIST_SHED:
                        new_bubble.id = b.id
                        bubbles_copy.pop(b.center)
                        self.add_bubble(new_bubble)
                        break
                else:
                    self.last_id += 1
                    new_bubble.id = self.last_id
                    self.add_bubble(new_bubble)

        return self.bubbles


if __name__ == '__main__':
    import random
    import time
    from pprint import pprint

    def random_bubbles():
        bubbles = []
        has_big = False
        for _ in range(3):
            x = random.randint(0, 640)
            y = random.randint(0, 480)
            w = random.randint(10, 100)
            h = random.randint(10, 100)
            is_big = False
            if not has_big:
                is_big = random.choice([True, False])
                if is_big:
                    has_big = True
            bubbles.append((x, y, w, h, is_big))
        return bubbles

    bt = BubbleTracker()
    while True:
        new_bubbles = random_bubbles()
        bt.update(new_bubbles)
        print('-' * 80)
        pprint(bt.bubbles)
        time.sleep(1)
