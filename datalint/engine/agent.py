"""
DataLint Agent - The autonomous entity that cleans your data.
"""

import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field

from .base import ValidationRunner, ValidationResult
from .fixers import BaseFixer

@dataclass
class AuditCode:
    """Record of an action taken by the agent."""
    step: int
    action: str
    description: str
    affected_rows: Optional[int] = None

class DataAgent:
    """
    Autonomous agent that iteratively validates and cleans data.
    """
    
    def __init__(self, runner: ValidationRunner, fixers: List[BaseFixer]):
        self.runner = runner
        self.fixers = fixers
        self.audit_log: List[AuditCode] = []
        
    def clean(self, df: pd.DataFrame, max_steps: int = 5) -> Tuple[pd.DataFrame, List[AuditCode]]:
        """
        Iteratively validate and fix data.
        """
        current_df = df.copy()
        self.audit_log = []
        
        for step in range(max_steps):
            print(f"--- Step {step + 1} ---")
            
            # 1. Observe (Validate)
            results = self.runner.run(current_df)
            failures = [r for r in results if not r.passed]
            
            if not failures:
                print("Data is clean!")
                break
                
            print(f"Found {len(failures)} issues.")
            
            # 2. Decide (Select Fixer)
            # Simple strategy: Just pick the first applicable fixer for the first failure
            # In a real agent, this would be an LLM or complex heuristic
            fix_applied = False
            
            for failure in failures:
                applicable_fixer = self._find_fixer(failure)
                
                if applicable_fixer:
                    # 3. Act (Apply Fix)
                    print(f"Applying fix: {applicable_fixer.name} for {failure.name}")
                    rows_before = len(current_df)
                    current_df = applicable_fixer.apply(current_df, failure)
                    rows_after = len(current_df)
                    
                    # Log action
                    self.audit_log.append(AuditCode(
                        step=step + 1,
                        action=applicable_fixer.name,
                        description=f"Fixed {failure.name}: {failure.message}",
                        affected_rows=rows_before - rows_after if rows_before != rows_after else None
                    ))
                    
                    fix_applied = True
                    break # Apply one fix at a time per step (safer to re-validate after each)
            
            if not fix_applied:
                print("No applicable fixers found for remaining issues.")
                break
                
        return current_df, self.audit_log

    def _find_fixer(self, result: ValidationResult) -> Optional[BaseFixer]:
        """Find the first fixer that can handle this result."""
        for fixer in self.fixers:
            if fixer.can_fix(result):
                return fixer
        return None
