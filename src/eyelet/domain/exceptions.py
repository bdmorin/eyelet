"""Domain-specific exceptions"""


class EyeletError(Exception):
    """Base exception for all Eyelet errors"""
    pass


class HookConfigurationError(EyeletError):
    """Error in hook configuration"""
    pass


class HookExecutionError(EyeletError):
    """Error during hook execution"""
    pass


class WorkflowError(EyeletError):
    """Error in workflow execution"""
    pass


class TemplateError(EyeletError):
    """Error in template processing"""
    pass


class DiscoveryError(EyeletError):
    """Error in hook/tool discovery"""
    pass
