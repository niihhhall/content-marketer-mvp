"""Research pipeline framework."""

from abc import ABC, abstractmethod


class ResearchStep(ABC):
    """A single step in the research pipeline."""

    @property
    @abstractmethod
    def name(self):
        ...

    @abstractmethod
    def execute(self, context):
        """Execute step, reading/writing to shared context dict."""
        ...


class ResearchPipeline:
    """Ordered sequence of research steps."""

    def __init__(self, name, steps):
        self.name = name
        self.steps = steps

    def run(self, initial_context):
        context = dict(initial_context)
        for step in self.steps:
            print(f"  [{step.name}]")
            context = step.execute(context)
        return context
