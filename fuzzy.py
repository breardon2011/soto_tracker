from fuzzywuzzy import process

def fuzzy_match_salary(player_name, salary_df, threshold=90):
    result = process.extractOne(player_name, salary_df['Name'])
    if result is None:
        return None
    match, score = result[:2]  
    if score >= threshold:
        matches = salary_df[salary_df['Name'] == match]['Salary'].values
        return matches[0] if len(matches) > 0 else None
    else:
        return None