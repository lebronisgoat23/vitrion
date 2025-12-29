from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from backend.core.face_analyzer import FaceEdemaAnalyzer
from backend.core.agent import NutriAgent
import numpy as np
import cv2
import io

app = FastAPI(title="Vitrion Face Analysis API")
analyzer = FaceEdemaAnalyzer()

@app.get("/")
def read_root():
    return {"message": "Vitrion AI Service is Running"}

@app.post("/analyze")
async def analyze_face(
    file: UploadFile = File(...),
    mode: str = Form("AESTHETIC") 
):
    """
    Endpoint to upload an image and get edema metrics.
    """
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file format.")
            
        # [BRANCH] Mode Handling
        if mode == 'FOOD':
            # --- FOOD MODE (Mock Intelligence) ---
            # In production, this would use a CLIP/ResNet food classifier.
            # For MVP, we return a "High Calorie" warning simulation.
            return {
                "status": "success",
                "data": {
                    "scan_type": "FOOD",
                    "calories": 450,
                    "macros": {"protein": 12, "carbs": 55, "fat": 18},
                    "insulin_index": "HIGH",
                    "supply_drop": {
                        "item_name": "Apple Cider Vinegar",
                        "rarity": "RARE",
                        "description": "High Glycemic Load detected. Consuming ACV before eating reduces insulin spike by 30%.",
                        "buff": "-20% Insulin",
                        "icon": "Flame"
                    },
                    "bio_age": 0, # Not applicable
                    "aging_rate": 1.0,
                    "entropy_score": 0
                }
            }

        else:
            # --- FACE / VITAL MODE ---
            result = analyzer.analyze(img)
            
            if result['status'] == 'error':
                 return result
            
            # [NEW] Nutri-Agent Analysis
            if result.get('data'):
                result['data']['scan_type'] = "FACE"
                agent_result = NutriAgent.analyze(result['data'])
                # Flatten analysis into the main data object
                result['data']['supply_drop'] = agent_result['recommendation']
                result['data']['bio_age'] = agent_result['bio_age']
                result['data']['aging_rate'] = agent_result['aging_rate']
                result['data']['entropy_score'] = agent_result['entropy_score']
                 
            return result

    except Exception as e:
        return {"status": "error", "message": str(e), "data": None}
