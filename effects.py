"""
This module handles loading and processing effects data from a CSV file.
Place this file in the root directory of your Flask application.
"""

import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Effect:
    """Represents an effect with its properties."""
    name: str
    multiplier: str
    type: str
    description: str
    color: str = ""

class EffectsManager:
    """Manages loading and retrieving effects data."""
    
    def __init__(self):
        self.effects: Dict[str, Effect] = {}
        self.loaded = False
        self.initialize_default_effects()
    
    def initialize_default_effects(self):
        """Initialize default effects from hardcoded CSV data."""
        csv_data = """Name,Multiplier,Type,Description
Anti-Gravity,x0.54,Ability,Causes user to jump higher.
Athletic,x0.32,Ability,Causes user to run faster.
Balding,x0.30,Cosmetic,Causes user to be bald.
Bright-Eyed,x0.40,Ability,Causes user's eyes to shine flashlight beams.
Calming,x0.10,Cosmetic,Causes user to have chromatic aberration around screen
Calorie-Dense,x0.28,Cosmetic,Causes user to appear fat.
Cyclopean,x0.56,Cosmetic,Causes user to only have one eye.
Disorienting,x0.00,,
Electrifying,x0.50,Cosmetic,Causes lightning effect on user.
Energizing,x0.22,Ability,Causes user to run faster.
Euphoric,x0.18,,
Explosive,x0.00,Ability,"Causes user to explode after ticking countdown, killing the user and damaging NPCs in the vicinity"
Focused,x0.16,,
Foggy,x0.36,,
Gingeritis,x0.20,Cosmetic,Causes user to have red hair.
Glowing,x0.48,Cosmetic,Causes user to have a radioactive glow.
Jennerising,x0.42,Cosmetic,Causes user to appear female.
Laxative,x0.00,Cosmetic,Causes user to constantly soil themselves.
Lethal,,,
Long Faced,x0.52,Cosmetic,Causes user's neck and face to grow.
Munchies,x0.12,,
Paranoia,x0.00,,
Refreshing,x0.14,,
Schizophrenia,x0.00,,
Sedating,x0.26,Cosmetic,Causes user to have a vignette around screen and mouse smoothing
Seizure-Inducing,x0.00,Cosmetic,Causes user to have a seizure and shake on the ground.
Shrinking,x0.60,Cosmetic,Causes user to shrink.
Slippery,x0.34,Ability,"Causes user to have sluggish, slippery movement."
Smelly,x0.00,Cosmetic,Causes user to have a stinky cloud around them.
Sneaky,x0.24,,
Spicy,x0.38,Cosmetic,Causes user's head to light on fire.
Thought-Provoking,x0.44,Cosmetic,Causes user's head to grow in size.
Toxic,x0.00,Cosmetic,Causes user to vomit.
Tropic Thunder,x0.46,Cosmetic,Causes user to have black skin.
Zombifying,x0.58,Cosmetic,Causes user to have green skin and have a zombie-like voice."""
        
        try:
            # Parse the CSV data
            import io
            reader = csv.DictReader(io.StringIO(csv_data))
            
            for row in reader:
                # Normalize the effect name for consistent lookup
                normalized_name = row['Name'].lower().replace(' ', '').replace('-', '')
                
                self.effects[normalized_name] = Effect(
                    name=row['Name'],
                    multiplier=row['Multiplier'],
                    type=row['Type'] if row['Type'] else "Unknown",
                    description=row['Description'] if row['Description'] else "No description available",
                    # Use color from effects.js if available, otherwise empty string
                    color=""
                )
            
            self.loaded = True
            print(f"Successfully loaded {len(self.effects)} default effects")
        except Exception as e:
            print(f"Error loading default effects: {e}")
    
    def load_effects(self, csv_path: str = 'data/effects.csv') -> bool:
        """Alias for load_effects_from_file for backward compatibility."""
        return self.load_effects_from_file(csv_path)
        
    def load_effects_from_file(self, csv_path: str = 'data/effects.csv') -> bool:
        """Load effects from CSV file."""
        if not os.path.exists(csv_path):
            print(f"Warning: Effects CSV file not found at {csv_path}")
            return False
            
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Skip rows with missing name
                    if not row.get('Name'):
                        continue
                        
                    # Normalize the effect name for consistent lookup
                    normalized_name = row['Name'].lower().replace(' ', '').replace('-', '')
                    
                    self.effects[normalized_name] = Effect(
                        name=row['Name'],
                        multiplier=row.get('Multiplier', ''),
                        type=row.get('Type', 'Unknown'),
                        description=row.get('Description', 'No description available'),
                        # Keep existing color if already loaded
                        color=self.effects.get(normalized_name, Effect('', '', '', '')).color
                    )
                
            self.loaded = True
            print(f"Successfully loaded {len(self.effects)} effects from {csv_path}")
            return True
        except Exception as e:
            print(f"Error loading effects CSV: {e}")
            return False
    
    def get_effect(self, effect_name: str) -> Optional[Effect]:
        """Get effect by name."""
        # Effects are already loaded in the constructor, no need to check loaded flag
            
        # Normalize the input effect name for consistent lookup
        normalized_name = effect_name.lower().replace(' ', '').replace('-', '')
        
        # Try exact match
        if normalized_name in self.effects:
            return self.effects[normalized_name]
            
        # Try with some common name variations
        variations = [
            normalized_name,
            normalized_name.replace('-', ''),
            normalized_name.replace(' ', ''),
            'bright-eyed' if normalized_name == 'brighteyed' else normalized_name,
            'thought-provoking' if normalized_name == 'thoughtprovoking' else normalized_name,
            'tropic-thunder' if normalized_name == 'tropicthunder' else normalized_name,
            'long-faced' if normalized_name == 'longfaced' else normalized_name
        ]
        
        for variant in variations:
            if variant in self.effects:
                return self.effects[variant]
        
        # If still not found, try to find by prefix match
        for name, effect in self.effects.items():
            if name.startswith(normalized_name) or normalized_name.startswith(name):
                return effect
                
        return None
    
    def get_all_effects(self) -> List[Effect]:
        """Get all loaded effects."""
        # Effects are already loaded in the constructor
        return list(self.effects.values())

# Global instance for easy importing
effects_manager = EffectsManager()