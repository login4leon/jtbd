
from dataclasses import dataclass, field
from typing import Callable, Optional, Any


@dataclass
class Step:                      # ① 步骤抽象
    name: str
    run : Callable[["Context"], None]
    compensate : Optional[Callable[["Context"], None]] = None

@dataclass
class Context:                   # ② 共享上下文

    inputs: dict = field(default_factory=dict)
    retries: int = 0

    # def __init__(self, **kwargs: Any) -> None:
    #     if kwargs:
    #         self.inputs = kwargs


class Workflow:                  # ③ 状态机
    def __init__(self, steps: list[Step], **kwargs: Any) -> None:
        self.steps = steps
        self.ctx = Context(kwargs)
        self._index = 0

    def run(self):
        try:
            for i, step in enumerate(self.steps):
                self._index = i + 1
                self.ctx = step.run(self.ctx)
                print(self._index, step.name, self.ctx)
        except Exception as e:
            # self.rollback()
            raise

