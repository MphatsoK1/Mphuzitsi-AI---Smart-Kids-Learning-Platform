"""
Utility functions for age-based game filtering
"""
from datetime import date

def get_age_from_birthdate(birthdate):
    """Calculate age from date of birth"""
    if not birthdate:
        return None
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def get_difficulty_by_age(age):
    """
    Map user age to game difficulty level
    Returns: 'easy', 'medium', 'hard', or None if age is invalid
    """
    if age is None:
        return None  # Return None if age is not available
    
    if age <= 6:
        return 'easy'  # Ages 3-6: Easy
    elif age <= 9:
        return 'medium'  # Ages 7-9: Medium
    elif age <= 12:
        return 'hard'  # Ages 10-12: Hard
    else:
        # For ages 13+, default to hard but allow all difficulties
        return 'hard'

def get_age_range_for_difficulty(difficulty):
    """
    Get age range for a given difficulty level
    Returns: tuple of (min_age, max_age) or None
    """
    difficulty_map = {
        'easy': (3, 6),      # Ages 3-6
        'medium': (7, 9),    # Ages 7-9
        'hard': (10, 12),    # Ages 10-12
        'expert': (13, 100), # Ages 13+
    }
    return difficulty_map.get(difficulty, None)

def filter_by_age_appropriate(user, queryset, difficulty_field='difficulty'):
    """
    Filter a queryset by user's age-appropriate difficulty level
    Args:
        user: User instance
        queryset: Django queryset to filter
        difficulty_field: Name of the difficulty field in the model
    Returns:
        Filtered queryset
    """
    if not user or not hasattr(user, 'profile'):
        # If no user or profile, return all active items
        return queryset.filter(**{f'{difficulty_field}__isnull': False})
    
    profile = user.profile
    age = get_age_from_birthdate(profile.date_of_birth)
    
    if age is None:
        # If no age, return all difficulties
        return queryset.filter(**{f'{difficulty_field}__isnull': False})
    
    difficulty = get_difficulty_by_age(age)
    
    if difficulty is None:
        # If difficulty can't be determined, return all
        return queryset.filter(**{f'{difficulty_field}__isnull': False})
    
    # Filter by difficulty level and easier levels
    difficulty_ordering = ['easy', 'medium', 'hard', 'expert']
    allowed_difficulties = []
    
    for diff in difficulty_ordering:
        allowed_difficulties.append(diff)
        if diff == difficulty:
            break
    
    return queryset.filter(**{f'{difficulty_field}__in': allowed_difficulties})

