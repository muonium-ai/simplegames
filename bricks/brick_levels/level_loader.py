import json
import os
from brick_colors import get_brick_color

class LevelLoader:
    def __init__(self, levels_dir="levels"):
        self.levels_dir = levels_dir
        self.current_level = 1
        self.max_level = self._count_levels()
    
    def _count_levels(self):
        """Count how many level files exist"""
        count = 0
        while os.path.exists(os.path.join(self.levels_dir, f"level{count + 1}.json")):
            count += 1
        return count
    
    def load_level(self, level_number=None):
        """Load a specific level or current level if none specified"""
        if level_number is None:
            level_number = self.current_level
            
        try:
            with open(os.path.join(self.levels_dir, f"level{level_number}.json"), 'r') as f:
                level_data = json.load(f)
            return level_data
        except FileNotFoundError:
            return None
    
    def next_level(self):
        """Advance to next level if available"""
        if self.current_level < self.max_level:
            self.current_level += 1
            return True
        return False

    def create_bricks(self, Brick):
        """Create brick objects from current level data"""
        level_data = self.load_level()
        if not level_data:
            return []
            
        bricks = []
        for brick_data in level_data["bricks"]:
            brick = Brick(
                x=brick_data["x"],
                y=brick_data["y"],
                hit=brick_data["hits"]
            )
            brick.color = get_brick_color(brick_data["color"])
            bricks.append(brick)
        return bricks
