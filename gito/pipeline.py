import logging
from enum import StrEnum
from dataclasses import dataclass, field

from gito.utils import is_running_in_github_action
from microcore.utils import resolve_callable
from sympy.physics.control import step_response_plot


class PipelineEnv(StrEnum):
    LOCAL = "local"
    GH_ACTION = "gh_action"

    @staticmethod
    def all():
        return [PipelineEnv.LOCAL, PipelineEnv.GH_ACTION]

    @staticmethod
    def current():
        return PipelineEnv.GH_ACTION if is_running_in_github_action() else PipelineEnv.LOCAL

@dataclass
class PipelineStep:
    call: str
    envs: list[PipelineEnv] = field(default_factory=PipelineEnv.all)

    def run(self, *args, **kwargs):
        fn = resolve_callable(self.call)
        fn(*args, **kwargs)

@dataclass
class Pipeline:
    ctx: dict = field(default_factory=dict)
    steps: dict[PipelineStep] = field(default_factory=dict)

    def run(self, *args, **kwargs):
        cur_env = PipelineEnv.current()
        self.ctx["pipeline_out"] = self.ctx.get("pipeline_out", {})
        for step_name, step in self.steps.items():
            if not step.envs or cur_env in step.envs:
                logging.info(f"Running pipeline step: {step_name}")
                step_output = step.run(*args, **kwargs, **self.ctx)
                if isinstance(step_output, dict):
                    self.ctx["pipeline_out"].update(step_output)
                self.ctx["pipeline_out"][step_name] = step_output
        return self.ctx["pipeline_out"]
