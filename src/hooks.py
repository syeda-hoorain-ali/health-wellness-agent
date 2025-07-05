import time
import json
from typing import Any, Dict, List, NotRequired, Optional, TypedDict
from datetime import datetime
from agents import Agent, RunContextWrapper, RunHooks, Tool
from colorama import Fore, Style

from src.context import UserSessionContext


class AgentPerformanceEntry(TypedDict):
    start_count: int
    total_tokens: int
    last_used: Optional[str]

class HandoffRecord(TypedDict):
    timestamp: str
    from_agent: str
    to_agent: str
    user_name: str
    total_tokens: int

class ErrorRecord(TypedDict):
    method: str
    error: str
    timestamp: str
    context: dict

class SessionSummary(TypedDict):
    session_duration_seconds: float
    total_events: int
    agent_performance:  Dict[str, AgentPerformanceEntry]
    tool_usage: Dict[str, int]
    handoff_history: List[HandoffRecord]
    error_count: int
    errors: Optional[List[ErrorRecord]]
    

class HealthWellnessHooks(RunHooks[UserSessionContext]):
    def __init__(self):
        self.event_counter = 0
        self.name = "HealthWellnessHooks"
        self.session_start_time = time.time()
        self.agent_performance: Dict[str, AgentPerformanceEntry] = {}
        self.tool_usage: Dict[str, int] = {}
        self.handoff_history: List[HandoffRecord] = []
        self.errors: List[ErrorRecord] = []


    
    def _log_event(self, event_type: str, details: Dict[str, Any]):
        """Centralized logging with timestamp and structured data"""
        timestamp = datetime.now().isoformat()
        self.event_counter += 1
        
        log_entry = {
            "event_id": self.event_counter,
            "timestamp": timestamp,
            "event_type": event_type,
            "session_duration": round(time.time() - self.session_start_time, 2),
            **details
        }
        
        print(Fore.YELLOW, f"\n> {self.name} #{self.event_counter} [{timestamp}] {event_type}", Style.RESET_ALL)
        print(f"   Details: {json.dumps(log_entry, indent=2, default=str)}")
        print()
        
        return log_entry
    
    
        
    def _log_error(self, method_name: str, error_message: str, context: Dict[str, Any]):
        """Log errors with context for debugging"""
        error_record: ErrorRecord = {
            "method": method_name,
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "context": context, 
        }
        self.errors.append(error_record)
        
        print(Fore.RED, f"\n⚠ {self.name} ERROR in {method_name}: {error_message}", Style.RESET_ALL)
        print(f"   Context: {json.dumps(context, indent=2)}")
        print()
    
    #  ----------------------------- Hooks -----------------------------

    async def on_agent_start(self, context: RunContextWrapper[UserSessionContext], agent: Agent):
        """Track agent start with performance metrics"""
        try:
            agent_name = agent.name
            user_name = context.context.name
            user_uid = context.context.uid
            
            # Initialize agent performance tracking
            if agent_name not in self.agent_performance:
                self.agent_performance[agent_name] = {
                    "start_count": 0,
                    "total_tokens": 0,
                    "last_used": None
                } 
            
            self.agent_performance[agent_name]["start_count"] += 1
            self.agent_performance[agent_name]["last_used"] = datetime.now().isoformat()
            
            details = {
                "agent_name": agent_name,
                "user_name": user_name,
                "user_uid": user_uid,
                "current_tokens": context.usage.total_tokens,
                "progress_entries": len(context.context.progress_logs),
                "handoff_count": len(context.context.handoff_logs)
            }
            
            self._log_event("AGENT_START", details)
            
        except Exception as e:
            self._log_error(
                method_name="on_agent_start", 
                error_message=str(e), 
                context={"agent_name": getattr(agent, 'name', 'Unknown')}
            )

    
    async def on_agent_end(self, context: RunContextWrapper[UserSessionContext], agent: Agent, output: Any):
        """Track agent completion with results and performance"""
        try:
            agent_name = agent.name
            user_name = context.context.name
            
            # Update performance metrics
            if agent_name in self.agent_performance:
                self.agent_performance[agent_name]["total_tokens"] = context.usage.total_tokens 
            
            details = {
                "agent_name": agent_name,
                "user_name": user_name,
                "final_tokens": context.usage.total_tokens,
                "output_length": len(str(output)) if output else 0,
                "output_type": type(output).__name__, # Class name if it is stuructured output else str
            }
            
            self._log_event("AGENT_END", details)
            
        except Exception as e:
            self._log_error(
                method_name="on_agent_end", 
                error_message=str(e), 
                context={"agent_name": getattr(agent, 'name', 'Unknown')}
            )


    async def on_tool_start(self, context: RunContextWrapper[UserSessionContext], agent: Agent, tool: Tool):
        """Track tool execution start with parameters"""
        try:
            agent_name = agent.name
            tool_name = tool.name
            user_name = context.context.name
            
            # Track tool usage
            if tool_name not in self.tool_usage:
                self.tool_usage[tool_name] = 0
            self.tool_usage[tool_name] += 1
            
            details = {
                "agent_name": agent_name,
                "tool_name": tool_name,
                "user_name": user_name,
                "tool_usage_count": self.tool_usage[tool_name],
                "current_tokens": context.usage.total_tokens
            }
            
            self._log_event("TOOL_START", details)
            
        except Exception as e:
            self._log_error(
                method_name="on_tool_start", 
                error_message=str(e), 
                context={
                    "agent_name": getattr(agent, 'name', 'Unknown'),
                    "tool_name": getattr(tool, 'name', 'Unknown')
                }
            )


    async def on_tool_end(self, context: RunContextWrapper[UserSessionContext], agent: Agent, tool: Tool, result: str):
        """Track tool completion with results and performance"""
        try:
            agent_name = agent.name
            tool_name = tool.name
            user_name = context.context.name
            
            details = {
                "agent_name": agent_name,
                "tool_name": tool_name,
                "user_name": user_name,
                "result_length": len(str(result)) if result else 0,
                "result_type": type(result).__name__,
                "final_tokens": context.usage.total_tokens,
            }
            
            self._log_event("TOOL_END", details)
            
        except Exception as e:
            self._log_error(
                method_name="on_tool_end", 
                error_message=str(e), 
                context={
                "agent_name": getattr(agent, 'name', 'Unknown'),
                "tool_name": getattr(tool, 'name', 'Unknown'),
            })


    async def on_handoff(self, context: RunContextWrapper[UserSessionContext], from_agent: Agent, to_agent: Agent):
        """Track agent handoffs with detailed context"""
        try:
            from_agent_name = from_agent.name
            to_agent_name = to_agent.name
            user_name = context.context.name
            
            # Record handoff in history
            handoff_record: HandoffRecord = {
                "timestamp": datetime.now().isoformat(),
                "from_agent": from_agent_name,
                "to_agent": to_agent_name,
                "user_name": user_name,
                "total_tokens": context.usage.total_tokens if hasattr(context, 'usage') else 0
            }
            self.handoff_history.append(handoff_record)
            
            # Update context handoff logs
            context.context.handoff_logs.append(f"{from_agent_name} → {to_agent_name}")
            
            details = {
                "from_agent": from_agent_name,
                "to_agent": to_agent_name,
                "user_name": user_name,
                "handoff_reason": f"Specialized expertise needed: {to_agent_name}",
                "total_handoffs": len(self.handoff_history),
                "current_tokens": context.usage.total_tokens if hasattr(context, 'usage') else 0
            }
            
            self._log_event("HANDOFF", details)
            
        except Exception as e:
            self._log_error(
                method_name="on_handoff", 
                error_message=str(e), 
                context={
                "from_agent": getattr(from_agent, 'name', 'Unknown'),
                "to_agent": getattr(to_agent, 'name', 'Unknown'),
            })


    # -------------------------------------------------
    
    def get_session_summary(self) -> SessionSummary:
        """Generate comprehensive session summary"""
        session_duration = round(time.time() - self.session_start_time, 2)
        
        return {
            "session_duration_seconds": session_duration,
            "total_events": self.event_counter,
            "agent_performance": self.agent_performance,
            "tool_usage": self.tool_usage,
            "handoff_history": self.handoff_history,
            "error_count": len(self.errors),
            "errors": self.errors if self.errors else None
        }
    

    def print_session_summary(self):
        """Print a formatted session summary"""
        summary = self.get_session_summary()
        duration = time.strftime("%H:%M:%S", time.gmtime(summary['session_duration_seconds']))
        
        print("\n" + "="*60)
        print(Fore.CYAN, Style.BRIGHT, " "*21, "SESSION SUMMARY", " "*21, Style.RESET_ALL)
        print("="*60)
        print(f"Duration: {duration}")
        print(f"Total Events: {summary['total_events']}")
        print(f"Errors: {summary['error_count']}")
        
        if summary['agent_performance']:
            print("\nAgent Performance:")
            for agent_name, stats in summary['agent_performance'].items():
                print(f"  {agent_name}: {stats['start_count']} starts, {stats['total_tokens']} tokens")
        
        if summary['tool_usage']:
            print("\nTool Usage:")
            for tool, count in summary['tool_usage'].items():
                print(f"  {tool}: {count} times")
        
        if summary['handoff_history']:
            print(f"\nHandoffs: {len(summary['handoff_history'])}")
            for handoff in summary['handoff_history']:
                print(f"  {handoff['from_agent']} → {handoff['to_agent']}")
        
        print("="*60)
