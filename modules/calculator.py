from datetime import datetime

def calculate_life_metrics(birth_date_str, expected_life=80):
    """Calculates all premium real-time metrics needed for the stats UI and the PDF grid."""
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    except ValueError:
        birth_date = datetime(2000, 1, 1)

    # Hardcoded current date context
    current_date = datetime(2026, 6, 26)
    
    # Calculate years lived
    age_years = current_date.year - birth_date.year
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age_years -= 1
        
    # Calculate exact current week within this birth year
    try:
        last_birthday = birth_date.replace(year=current_date.year)
        if last_birthday > current_date:
            last_birthday = birth_date.replace(year=current_date.year - 1)
    except ValueError: # Handle leap year babies (Feb 29) safely
        last_birthday = datetime(current_date.year, 2, 28)
        if last_birthday > current_date:
            last_birthday = datetime(current_date.year - 1, 2, 28)

    days_since_birthday = (current_date - last_birthday).days
    weeks_this_year = int(days_since_birthday / 7)
    
    total_weeks_lived = (age_years * 52) + weeks_this_year
    total_weeks_potential = expected_life * 52
    weeks_remaining = max(0, total_weeks_potential - total_weeks_lived)
    
    percentage_used = (total_weeks_lived / total_weeks_potential) * 100 if total_weeks_potential > 0 else 0
    
    return {
        "years_lived": age_years,
        "weeks_spent": total_weeks_lived,
        "weeks_future": weeks_remaining,
        "life_used_pct": round(percentage_used, 1)
    }