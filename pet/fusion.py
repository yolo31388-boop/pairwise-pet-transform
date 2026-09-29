"""宠物合体与变身系统 - 含9个bug"""
from dataclasses import dataclass, field

@dataclass
class Pet:
    pid: str
    name: str
    level: int = 1
    element: str = "fire"
    atk: int = 100
    skills: list = field(default_factory=list)
    intimacy: int = 0  # bug1: 不检查

class FusionSystem:
    def __init__(self, seed=42):
        import random
        self.rng = random.Random(seed)

    def can_fuse(self, p1: Pet, p2: Pet) -> bool:
        # bug1: 无条件
        return True

    def calculate_fused_stats(self, p1: Pet, p2: Pet) -> dict:
        # bug2: 简单相加
        return {"atk": p1.atk + p2.atk}

    def get_fusion_skill(self, p1_element: str, p2_element: str) -> str:
        # bug3: 固定技能
        return "fusion_attack"

    def get_fusion_duration(self) -> float:
        # bug4: 无限时间
        return float("inf")

    def get_form_roll(self, target_form: str) -> tuple[str, bool]:
        # bug5: 随机无保底
        forms = ["fire", "water", "earth", "wind"]
        return self.rng.choice(forms), False

    def fusion_failure_cost(self) -> dict:
        # bug6: 无惩罚
        return {"material_cost": 0}

    def get_fusion_cooldown(self) -> float:
        # bug7: 无冷却
        return 0.0

    def get_energy_cost(self, skill: str) -> float:
        # bug8: 不消耗能量
        return 0.0

    def get_inherited_skills_limit(self) -> int:
        # bug9: 全继承
        return 999
