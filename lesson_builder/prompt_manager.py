from dataclasses import dataclass
from typing import List, Dict, Any
import json
from pathlib import Path
import yaml

@dataclass
class Example:
    input: Dict[str, Any]
    output: str

@dataclass
class PromptConfig:
    name: str
    description: str
    system_prompt: str
    examples: List[Example]

class PromptManager:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompt_configs: Dict[str, PromptConfig] = {}
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """Load all prompt configurations from the prompts directory."""
        for prompt_dir in self.prompts_dir.iterdir():
            if prompt_dir.is_dir():
                prompt_type = prompt_dir.name
                self.prompt_configs[prompt_type] = self._load_prompt_config(prompt_dir)
    
    def _load_prompt_config(self, prompt_dir: Path) -> PromptConfig:
        """Load a single prompt configuration from its directory."""
        # Load metadata
        with open(prompt_dir / "metadata.yaml") as f:
            metadata = yaml.safe_load(f)
        
        # Load system prompt
        with open(prompt_dir / "system_prompt.md") as f:
            system_prompt = f.read()
        
        # Load examples
        examples = []
        examples_dir = prompt_dir / "examples"
        for example_file in examples_dir.glob("*.json"):
            with open(example_file) as f:
                example_data = json.load(f)
                examples.append(Example(
                    input=example_data["input"],
                    output=example_data["output"]
                ))
        
        return PromptConfig(
            name=metadata["name"],
            description=metadata["description"],
            system_prompt=system_prompt,
            examples=examples
        )
    
    def get_prompt(self, prompt_type: str) -> PromptConfig:
        """Get a prompt configuration by type."""
        if prompt_type not in self.prompt_configs:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        return self.prompt_configs[prompt_type]
    
    def format_for_claude(self, prompt_type: str) -> tuple[str, str]:
        """Format the prompt and examples for Claude API."""
        config = self.get_prompt(prompt_type)
        
        # Format examples in Claude's expected format
        examples_text = ""
        for i, example in enumerate(config.examples, 1):
            examples_text += f"<example>\n<INPUT_PROMPT>\n"
            examples_text += json.dumps(example.input, indent=2)
            examples_text += "\n</INPUT_PROMPT>\n<IDEAL_OUTPUT>\n"
            examples_text += example.output
            examples_text += "\n</IDEAL_OUTPUT>\n</example>\n\n"
        
        return config.system_prompt, examples_text

    def list_prompt_types(self) -> List[str]:
        """List all available prompt types."""
        return list(self.prompt_configs.keys())