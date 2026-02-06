import re

def predict_zone_action(zone):
    """
    Predict what refinement is needed for this zone.
    Designed to handle common everyday writing patterns.
    """
    text = zone.text
    print(f"    [PREDICT DEBUG] Checking zone: '{text[:50]}...' | Last 5 chars: '{text[-5:]}' | Stripped last char: '{text.strip()[-1] if text.strip() else 'EMPTY'}'")

    # PHASE 0: End punctuation check - DO THIS FIRST!
    clean_text = text.strip()
    if clean_text and clean_text[-1] not in '.!?':
        print(f"    [PERIOD DEBUG] Text needs period! Last char is: '{clean_text[-1]}'")
        return "add period"

    # PHASE 1: Basic cleanup
    if "  " in text:
        return "fix spacing"

    # PHASE 2: Contractions (do early)
    if re.search(r'\b(im|dont|didnt|cant|wont|isnt|arent|wasnt|werent|havent|hasnt|wouldnt|couldnt|shouldnt)\b', text, re.IGNORECASE):
        return "fix contractions"

    # PHASE 3: First letter capitalization (HIGH PRIORITY for run-on text)
    if text and text[0].islower():
        return "capitalize first"

    # PHASE 4: Name capitalization (intro zones only)
    if zone.zone_type == "intro":
        if re.search(r'(name is|i am|i\'m|called)\s+([a-z]\w+)', text, re.IGNORECASE):
            return "capitalize name"

    # PHASE 5: Compound sentence commas (BEFORE sentence breaks)
    # "shopping but the" or "closed so i" need commas
    if re.search(r'\s+(but|so|yet)\s+', text, re.IGNORECASE):
        match = re.search(r'(\w+)(\s+)(but|so|yet)(\s+)', text, re.IGNORECASE)
        if match:
            before = text[:match.start(3)]
            # Check no recent comma
            if ',' not in before[-10:] and '.' not in before[-10:]:
                words = before.split()
                if len(words) >= 3:
                    return "add compound comma"
    
    # PHASE 7: Capitalization fixes
    if re.search(r'[.!?]\s+[a-z]', text):
        return "capitalize after period"

    # PHASE 8: End punctuation - CRITICAL CHECK
    clean_text = text.strip()
    if clean_text and clean_text[-1] not in '.!?':
        print(f"    DEBUG: Text needs period. Last char is: '{clean_text[-1]}'")
        return "add period"

    # Zone is complete
    return "no change"


def apply_zone_action(zone, action):
    """
    Apply refinement action to a specific zone.
    """
    text = zone.text
    original = text
    
    if action == "fix spacing":
        text = " ".join(text.split())
    
    elif action == "capitalize name":
        def cap_name(match):
            prefix = match.group(1)
            name = match.group(2)
            return f"{prefix} {name.capitalize()}"
        text = re.sub(r'(name is|i am|i\'m|called)\s+([a-z]\w+)', cap_name, text, count=1, flags=re.IGNORECASE)
    
    elif action == "fix contractions":
        contractions = {
            r'\bim\b': "I'm",
            r'\bdont\b': "don't",
            r'\bdidnt\b': "didn't",
            r'\bcant\b': "can't",
            r'\bwont\b': "won't",
            r'\bisnt\b': "isn't",
            r'\barent\b': "aren't",
            r'\bwasnt\b': "wasn't",
            r'\bwerent\b': "weren't",
            r'\bhavent\b': "haven't",
            r'\bhasnt\b': "hasn't",
            r'\bwouldnt\b': "wouldn't",
            r'\bcouldnt\b': "couldn't",
            r'\bshouldnt\b': "shouldn't"
        }
        for pattern, replacement in contractions.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    elif action == "add sentence break":
        # Find where to add the break - be smarter about placement
        
        # Pattern 1: Time word + rest (yesterday/today/tomorrow + content)
        match = re.search(r'^(yesterday|today|tomorrow)(\s+)([a-z])', text, re.IGNORECASE)
        if match and len(text.split()) > 3:
            # Don't break at start, this is fine
            pass
        
        # Pattern 2: "noun the/a" suggests new sentence
        match = re.search(r'(\w{4,})(\s+)(the|a)\s+\w+', text, re.IGNORECASE)
        if match:
            before = text[:match.start()]
            if len(before.split()) >= 3 and '.' not in before[-15:]:
                # Check it's not a conjunction that needs comma
                word_before = text[max(0, match.start()-10):match.start()].strip().split()
                if word_before and word_before[-1].lower() not in ['but', 'and', 'or', 'so']:
                    insert_pos = match.end(1)
                    text = text[:insert_pos] + '. ' + text[insert_pos+1].upper() + text[insert_pos+2:]
                    zone.mark_change()
                    zone.text = text
                    zone.tokens_processed += zone.count_tokens()
                    return True
        
        # Pattern 3: Pronoun after content (I/We/They/He/She after 4+ char word)
        match = re.search(r'([a-z]{4,})(\s+)(I|We|They|He|She|It)(\s+)([a-z])', text)
        if match:
            before = text[:match.start()]
            if len(before.split()) >= 3 and '.' not in before[-15:]:
                # Check if it's after "but" or "and" - those need commas not periods
                recent_words = before[-20:].lower() if len(before) > 20 else before.lower()
                if 'but' not in recent_words and 'and' not in recent_words:
                    insert_pos = match.end(1)
                    text = text[:insert_pos] + '.' + text[insert_pos:]
                    zone.mark_change()
                    zone.text = text
                    zone.tokens_processed += zone.count_tokens()
                    return True
    
    elif action == "add compound comma":
        # Add comma before conjunction
        match = re.search(r'(\w{4,})(\s+)(but|and|or|so|yet)(\s+)', text, re.IGNORECASE)
        if match:
            before = text[:match.start(3)]
            if ',' not in before[-15:]:
                text = text[:match.end(1)] + ',' + text[match.end(1):]
    
    elif action == "add period":
        print(f"    DEBUG: Adding period. Text before: '{text}' | Text after: '{text.strip() + '.'}'")
        text = text.strip() + "."
    
    elif action == "capitalize after period":
        def cap_after(match):
            return match.group(1) + match.group(2).upper()
        text = re.sub(r'([.!?]\s+)([a-z])', cap_after, text)
    
    elif action == "capitalize first":
        # Only capitalize if it's truly the start or after punctuation
        if text and text[0].islower() and not text.startswith(('but', 'and', 'or', 'so')):
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        elif text and text[0].islower():
            # If it starts with conjunction, capitalize anyway
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # Track changes
    if text != original:
        zone.mark_change()
    
    zone.text = text
    zone.tokens_processed += zone.count_tokens()
    return text != original


def polish_zone(zone):
    """
    Final polish pass for a zone.
    """
    text = zone.text
    original = text
    
    # Clean up spacing around punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    text = re.sub(r'([,.!?;:])([A-Za-z])', r'\1 \2', text)
    
    # Fix double spaces
    text = " ".join(text.split())
    
    # Capitalize standalone "I"
    text = re.sub(r'\bi\b', 'I', text)
    
    # Fix double punctuation
    text = re.sub(r'\.\.+', '.', text)
    text = re.sub(r',,+', ',', text)
    # Fix simple lists: "like a b and c" → "like a, b and c"
    text = re.sub(
        r'\blike\s+([a-z]+)\s+([a-z]+)\s+and\s+([a-z]+)',
        r'like \1, \2 and \3',
        text,
        flags=re.IGNORECASE
    )
    
    if text != original:
        zone.mark_change()
    
    zone.text = text
    return text != original