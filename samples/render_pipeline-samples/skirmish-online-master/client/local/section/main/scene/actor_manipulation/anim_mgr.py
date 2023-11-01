from client.local.animation.base import AnimationBase
from client.local.model.actor import ConfiguredActor
from direct.task.Task import Task
from client.local import core


class AnimationManager:
    def __init__(self, actor: ConfiguredActor):
        self.actor = actor
        self.considered_animations = {}
        self.anim_in_previous_tick = None
        task = Task(self.update_anim_task)
        core.instance.task_mgr.add(task, f"Update animation of actor {actor}")

    def consider_animation(self, anim: AnimationBase) -> None:
        self.considered_animations[anim.IMPORTANCE] = anim

    def remove_animation(self, anim: AnimationBase) -> None:
        if anim in self.considered_animations.values():
            del self.considered_animations[anim.IMPORTANCE]

    def action_ended(self, current_anim):
        return self.anim_in_previous_tick is not None and current_anim is None

    def update_anim_task(self, task):
        try:
            current_anim = self.actor.get_current_anim_uf()
            if self.action_ended(current_anim):
                self.remove_animation(self.anim_in_previous_tick)
                self.anim_in_previous_tick = None
                current_anim = None

            m_imp_anim = self.get_most_important_animation()
            if m_imp_anim is None:
                return Task.cont

            if m_imp_anim == current_anim:
                self.anim_in_previous_tick = current_anim
                return Task.cont

            self.actor.play_anim_uf(m_imp_anim)
            return Task.cont
        except:
            return Task.done


    def get_most_important_animation(self):
        keys = self.considered_animations.keys()
        if len(keys) < 1:
            return None
        highest_anim_level = max(keys)
        return self.considered_animations[highest_anim_level]

