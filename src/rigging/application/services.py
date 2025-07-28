"""Application services - Business logic implementation"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from datetime import datetime

from rigging.domain.models import (
    Hook, HookType, HookConfiguration, HookExecution,
    Template, Workflow, ToolMatcher, Handler
)
from rigging.domain.exceptions import (
    HookConfigurationError, TemplateError, WorkflowError
)
from rigging.infrastructure.repositories import (
    HookRepository, ExecutionRepository, TemplateRepository
)


class HookService:
    """Service for managing hooks"""
    
    def __init__(self, hook_repo: HookRepository):
        self.hook_repo = hook_repo
    
    def create_hook(self, hook: Hook) -> Hook:
        """Create and validate a new hook"""
        if not hook.is_valid_matcher():
            raise HookConfigurationError(
                f"Invalid matcher '{hook.matcher}' for hook type {hook.type}"
            )
        return self.hook_repo.save(hook)
    
    def get_hook(self, hook_id: str) -> Optional[Hook]:
        """Get a hook by ID"""
        return self.hook_repo.get(hook_id)
    
    def list_hooks(self, hook_type: Optional[HookType] = None) -> List[Hook]:
        """List all hooks, optionally filtered by type"""
        hooks = self.hook_repo.get_all()
        if hook_type:
            hooks = [h for h in hooks if h.type == hook_type]
        return hooks
    
    def update_hook(self, hook_id: str, updates: Dict[str, Any]) -> Optional[Hook]:
        """Update a hook"""
        hook = self.hook_repo.get(hook_id)
        if not hook:
            return None
        
        for key, value in updates.items():
            if hasattr(hook, key):
                setattr(hook, key, value)
        
        if not hook.is_valid_matcher():
            raise HookConfigurationError(
                f"Invalid matcher '{hook.matcher}' for hook type {hook.type}"
            )
        
        return self.hook_repo.save(hook)
    
    def delete_hook(self, hook_id: str) -> bool:
        """Delete a hook"""
        return self.hook_repo.delete(hook_id)
    
    def enable_hook(self, hook_id: str) -> Optional[Hook]:
        """Enable a hook"""
        return self.update_hook(hook_id, {"enabled": True})
    
    def disable_hook(self, hook_id: str) -> Optional[Hook]:
        """Disable a hook"""
        return self.update_hook(hook_id, {"enabled": False})


class ConfigurationService:
    """Service for managing hook configurations"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.claude_settings_path = config_path / ".claude" / "settings.json"
    
    def load_configuration(self) -> HookConfiguration:
        """Load hook configuration from Claude settings"""
        if not self.claude_settings_path.exists():
            return HookConfiguration()
        
        try:
            with open(self.claude_settings_path, 'r') as f:
                data = json.load(f)
            
            hooks_data = data.get("hooks", [])
            hooks = []
            
            for hook_data in hooks_data:
                # Convert Claude format to our format
                handler_data = hook_data["handler"]
                handler = Handler(**handler_data)
                hook = Hook(
                    type=HookType(hook_data["type"]),
                    matcher=hook_data.get("matcher"),
                    handler=handler
                )
                hooks.append(hook)
            
            return HookConfiguration(hooks=hooks)
        except Exception as e:
            raise HookConfigurationError(f"Failed to load configuration: {e}")
    
    def save_configuration(self, config: HookConfiguration) -> None:
        """Save hook configuration to Claude settings"""
        self.claude_settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing settings
        if self.claude_settings_path.exists():
            with open(self.claude_settings_path, 'r') as f:
                settings = json.load(f)
        else:
            settings = {}
        
        # Convert to Claude format
        hooks_data = []
        for hook in config.hooks:
            if hook.enabled:
                hook_dict = {
                    "type": hook.type,
                    "handler": hook.handler.model_dump(exclude_none=True)
                }
                if hook.matcher:
                    hook_dict["matcher"] = hook.matcher
                hooks_data.append(hook_dict)
        
        settings["hooks"] = hooks_data
        
        # Save with backup
        if self.claude_settings_path.exists():
            backup_path = self.claude_settings_path.with_suffix('.json.backup')
            backup_path.write_text(self.claude_settings_path.read_text())
        
        with open(self.claude_settings_path, 'w') as f:
            json.dump(settings, f, indent=2)


class ExecutionService:
    """Service for hook execution tracking"""
    
    def __init__(self, execution_repo: ExecutionRepository):
        self.execution_repo = execution_repo
    
    def record_execution(self, execution: HookExecution) -> HookExecution:
        """Record a hook execution"""
        return self.execution_repo.save(execution)
    
    def get_execution(self, execution_id: int) -> Optional[HookExecution]:
        """Get an execution by ID"""
        return self.execution_repo.get(execution_id)
    
    def list_executions(
        self, 
        hook_type: Optional[HookType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[HookExecution]:
        """List executions with optional filtering"""
        return self.execution_repo.get_recent(
            hook_type=hook_type, 
            limit=limit, 
            offset=offset
        )
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_repo.get_stats()


class TemplateService:
    """Service for managing templates"""
    
    def __init__(self, template_repo: TemplateRepository):
        self.template_repo = template_repo
    
    def list_templates(self, category: Optional[str] = None) -> List[Template]:
        """List available templates"""
        templates = self.template_repo.get_all()
        if category:
            templates = [t for t in templates if t.category == category]
        return templates
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template by ID"""
        return self.template_repo.get(template_id)
    
    def install_template(
        self, 
        template_id: str, 
        variables: Optional[Dict[str, Any]] = None
    ) -> List[Hook]:
        """Install a template, returning the created hooks"""
        template = self.template_repo.get(template_id)
        if not template:
            raise TemplateError(f"Template '{template_id}' not found")
        
        # Apply variables to template
        hooks = []
        for hook in template.hooks:
            hook_dict = hook.model_dump()
            
            # Replace variables in strings
            if variables:
                hook_dict = self._apply_variables(hook_dict, variables)
            
            hooks.append(Hook(**hook_dict))
        
        return hooks
    
    def _apply_variables(self, data: Any, variables: Dict[str, Any]) -> Any:
        """Recursively apply variables to template data"""
        if isinstance(data, str):
            for key, value in variables.items():
                data = data.replace(f"{{{{{key}}}}}", str(value))
            return data
        elif isinstance(data, dict):
            return {k: self._apply_variables(v, variables) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._apply_variables(item, variables) for item in data]
        return data


class WorkflowService:
    """Service for workflow execution"""
    
    def __init__(self, workflow_path: Path):
        self.workflow_path = workflow_path
    
    def execute_workflow(
        self, 
        workflow_id: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow with the given context"""
        # This is a placeholder - actual implementation would:
        # 1. Load workflow definition
        # 2. Execute steps in order
        # 3. Handle conditions and loops
        # 4. Return results
        raise NotImplementedError("Workflow execution coming soon!")
    
    def list_workflows(self) -> List[Workflow]:
        """List available workflows"""
        workflows = []
        if self.workflow_path.exists():
            for workflow_file in self.workflow_path.glob("**/*.yaml"):
                # Load and parse workflow files
                pass
        return workflows