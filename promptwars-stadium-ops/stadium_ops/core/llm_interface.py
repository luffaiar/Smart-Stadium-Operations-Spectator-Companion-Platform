"""Abstract interface for LLM (Language Model) services.

This module defines the interface that all concrete Language Model strategies
must implement, decoupling core business logic from specific API frameworks.
"""

from abc import ABC, abstractmethod
from typing import Optional


class LLMService(ABC):
    """Abstract Base Class for language model query services."""

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """Generates a text completion based on a prompt and system instruction.

        Args:
            prompt: User-provided query or context.
            system_instruction: Guidelines or directives for the system model.

        Returns:
            The generated text string response.

        Raises:
            LLMRequestError: If the remote model invocation fails.
        """
        pass
