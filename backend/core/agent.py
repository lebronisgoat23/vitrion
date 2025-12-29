from typing import Dict, Any

class NutriAgent:
    @staticmethod
    def analyze(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes facial metrics to recommend supplements and calculate Biological Age.
        Based on "FaceAge" (Harvard, 2024) - Reduced order model.
        """
        fwhr = metrics.get("face_width_height_ratio", 0)
        jawline = metrics.get("jawline_sharpness_deg", 0)
        
        # --- 1. Biological Age Calculation (Proprietary Algorithm) ---
        # Base Age (Defaulting to user input or statistical average 25 for MVP)
        chronological_age = 25 
        
        # Penalties (Aging Accelerators)
        edema_penalty = max(0, (fwhr - 1.6) * 10) # Puffiness adds age
        structure_penalty = max(0, (jawline - 120) * 0.2) # Sagging adds age
        
        bio_age = chronological_age + edema_penalty + structure_penalty
        
        # Aging Rate (Entropy)
        # Normal is 1.0. Higher is faster aging.
        aging_rate = bio_age / chronological_age
        
        # Entropy Score (0-100) - Higher is worse (Chaos)
        entropy_score = min(100, max(0, (aging_rate - 1) * 200 + 20))

        # --- 2. Recommendation Logic ---
        recommendation = {}
        
        # Rule 1: High Edema (FWHR > 1.6) -> Potassium
        if fwhr > 1.6:
            recommendation = {
                "item_name": "Potassium Elixir",
                "rarity": "RARE",
                "description": "High fluid retention detected. Increases sodium excretion to reduce bloat.",
                "buff": "-15% Edema",
                "icon": "Zap" 
            }
        
        # Rule 2: Round Jawline (Angle > 125) -> Caffeine 
        elif jawline > 125:
             recommendation = {
                "item_name": "Caffeine Solution",
                "rarity": "UNCOMMON",
                "description": "Soft jawline structure. Boosts metabolism and reduces facial fat.",
                "buff": "+10% Sharpness",
                "icon": "Activity"
            }
            
        # Default: Maintenance -> Collagen
        else:
            recommendation = {
                "item_name": "Hydrolyzed Collagen",
                "rarity": "EPIC",
                "description": "Optimal structure detected. Maintain elasticity and skin health.",
                "buff": "+5% Glow",
                "icon": "Shield"
            }
            
        return {
            "recommendation": recommendation,
            "bio_age": round(bio_age, 1),
            "aging_rate": round(aging_rate, 2),
            "entropy_score": int(entropy_score)
        }
