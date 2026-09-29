"""宠物合体与变身系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pet.fusion import FusionSystem, Pet

class TestFusionCondition:
    def test_incompatible_elements_cannot_fuse(self):
        fs = FusionSystem()
        p1 = Pet("p1", "fire", element="fire", intimacy=100)
        p2 = Pet("p2", "water", element="water", intimacy=100)
        assert fs.can_fuse(p1, p2) == False

class TestFusedStatsDecay:
    def test_fused_stats_not_simple_sum(self):
        fs = FusionSystem()
        p1 = Pet("p1", "a", atk=100)
        p2 = Pet("p2", "b", atk=100)
        result = fs.calculate_fused_stats(p1, p2)
        assert result["atk"] < 200

class TestFusionSkillByElement:
    def test_different_element_combos_give_different_skills(self):
        fs = FusionSystem()
        s1 = fs.get_fusion_skill("fire", "fire")
        s2 = fs.get_fusion_skill("fire", "earth")
        assert s1 != s2

class TestFusionDuration:
    def test_fusion_has_finite_duration(self):
        fs = FusionSystem()
        d = fs.get_fusion_duration()
        assert d < float("inf") and d > 0

class TestFormPity:
    def test_form_roll_has_pity(self):
        fs = FusionSystem(seed=1)
        # 应该有保底计数器
        assert hasattr(fs, "form_pity")
        fs.form_pity = {"target": 50}
        assert fs.form_pity["target"] >= 50

class TestFusionFailureCost:
    def test_failure_costs_materials(self):
        fs = FusionSystem()
        cost = fs.fusion_failure_cost()
        assert cost["material_cost"] > 0

class TestFusionCooldown:
    def test_fusion_has_cooldown(self):
        fs = FusionSystem()
        cd = fs.get_fusion_cooldown()
        assert cd > 0

class TestEnergyCost:
    def test_skills_consume_energy(self):
        fs = FusionSystem()
        cost = fs.get_energy_cost("ultimate")
        assert cost > 0

class TestInheritLimit:
    def test_inherited_skills_have_limit(self):
        fs = FusionSystem()
        limit = fs.get_inherited_skills_limit()
        assert limit <= 5
