"""
Timezone utilities for La Casa de Todos NFL Fantasy League
Converts all times to AST (Atlantic Standard Time)
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

# AST timezone (UTC-4)
AST = timezone(timedelta(hours=-4))

def convert_to_ast(dt: datetime) -> datetime:
    """Convert any datetime to AST timezone"""
    if dt is None:
        return None
    
    # If datetime is naive, assume it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to AST
    return dt.astimezone(AST)

def format_ast_time(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S AST') -> str:
    """Format datetime in AST with custom format"""
    if dt is None:
        return 'TBD'
    
    ast_time = convert_to_ast(dt)
    return ast_time.strftime(format_str)

def format_game_time(dt: datetime) -> str:
    """Format game time for display in AST"""
    if dt is None:
        return 'TBD'
    
    ast_time = convert_to_ast(dt)
    return ast_time.strftime('%A, %B %d at %I:%M %p AST')

def format_game_time_short(dt: datetime) -> str:
    """Format game time short for display in AST"""
    if dt is None:
        return 'TBD'
    
    ast_time = convert_to_ast(dt)
    return ast_time.strftime('%I:%M %p AST')

def get_current_ast() -> datetime:
    """Get current time in AST"""
    return datetime.now(AST)

def is_game_started(game_date: datetime) -> bool:
    """Check if game has started based on AST time"""
    if game_date is None:
        return False
    
    current_ast = get_current_ast()
    game_ast = convert_to_ast(game_date)
    
    return current_ast >= game_ast
