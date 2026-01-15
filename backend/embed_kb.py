import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.rag_service import build_knowledge_base, load_knowledge_base

def main():
    print("🚀 Starting Knowledge Base Embedding...")
    
    # Check API Key
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please export your key:")
        print("export OPENAI_API_KEY='sk-...'")
        return

    # Load raw articles (simulated loading from json for now)
    # In a real scenario, we might read from a raw_data.json
    # Here we will re-use the structure but pretend we are loading raw text
    try:
        from backend.core.knowledge_base import RAW_ARTICLES # We need to create this temporarily or read from file
        # Actually, let's just read the current json, strip embeddings if any, and re-embed.
        pass
    except ImportError:
        pass
        
    # For this script, I'll define the raw articles here to ensure clean slate
    # This matches the content we defined earlier
    articles = [
      {
        "id": "sleep-001",
        "title": "睡眠不足與情緒調節能力下降",
        "source": "Walker et al., Nature Reviews Neuroscience, 2017",
        "abstract": "研究顯示睡眠不足會導致杏仁核過度活化，前額葉皮質抑制功能降低，使情緒波動幅度增加 60%。每晚睡眠少於 6 小時與負面情緒顯著相關。",
        "category": "sleep"
      },
      {
        "id": "sleep-002",
        "title": "睡前藍光曝露與睡眠品質",
        "source": "Chang et al., PNAS, 2014",
        "abstract": "睡前使用發光螢幕會抑制褪黑激素分泌達 50%，延遲入睡時間，並減少 REM 睡眠。建議睡前 1-2 小時避免使用電子設備。",
        "category": "sleep"
      },
      {
        "id": "sleep-003",
        "title": "鎂補充與睡眠品質改善",
        "source": "Abbasi et al., Journal of Research in Medical Sciences, 2012",
        "abstract": "每日補充 500mg 鎂可顯著改善主觀睡眠品質評分、降低血清皮質醇、提升褪黑激素水平。鎂缺乏與失眠症狀相關。",
        "category": "sleep"
      },
      {
        "id": "sleep-004",
        "title": "咖啡因對睡眠的持續影響",
        "source": "Drake et al., Journal of Clinical Sleep Medicine, 2013",
        "abstract": "咖啡因半衰期約 5-6 小時，睡前 6 小時攝入咖啡因仍會減少總睡眠時間約 1 小時。建議中午後避免咖啡因攝取。",
        "category": "sleep"
      },
      {
        "id": "sleep-005",
        "title": "睡眠規律性比睡眠時長更重要",
        "source": "Phillips et al., Scientific Reports, 2017",
        "abstract": "睡眠時間變異性每增加 1 小時，GPA 下降 0.2。規律的睡眠時間對認知表現的影響甚至超過睡眠總時長。",
        "category": "sleep"
      },
      {
        "id": "energy-001",
        "title": "晨間陽光曝露與晝夜節律",
        "source": "Huberman, Stanford Neuroscience, 2021",
        "abstract": "早晨接受 10-30 分鐘自然光照可使皮質醇提前釋放，改善白天警覺性並促進夜間褪黑激素分泌。即使陰天也有效。",
        "category": "energy"
      },
      {
        "id": "energy-002",
        "title": "蛋白質早餐對能量水平的影響",
        "source": "Leidy et al., Nutrition Journal, 2014",
        "abstract": "含 30g 蛋白質的早餐相比低蛋白早餐，可減少上午飢餓感、穩定血糖，並提升持續精力至中午。",
        "category": "energy"
      },
      {
        "id": "energy-003",
        "title": "冷水接觸與多巴胺釋放",
        "source": "Šrámek et al., European Journal of Applied Physiology, 2000",
        "abstract": "冷水淋浴（14°C，2-3 分鐘）可使多巴胺水平上升 250%，效果持續數小時，改善警覺性和情緒。",
        "category": "energy"
      },
      {
        "id": "energy-004",
        "title": "輕度運動對午後疲勞的效果",
        "source": "Thayer, Psychological Bulletin, 1987",
        "abstract": "10-15 分鐘的輕度步行比休息或吃零食更能有效提升能量水平。效果可持續 1-2 小時。",
        "category": "energy"
      },
      {
        "id": "energy-005",
        "title": "脫水與認知疲勞",
        "source": "Ganio et al., British Journal of Nutrition, 2011",
        "abstract": "輕度脫水（體重減少 1-2%）即可導致注意力下降、疲勞感增加、頭痛。建議每日攝取體重(kg) x 30ml 水分。",
        "category": "energy"
      },
      {
        "id": "focus-001",
        "title": "番茄工作法與持續注意力",
        "source": "Cirillo, 2006; Ariga et al., Cognition, 2011",
        "abstract": "研究顯示注意力在 20-40 分鐘後開始下降。短暫休息可重置注意力資源，25分鐘工作+5分鐘休息為有效模式。",
        "category": "focus"
      },
      {
        "id": "focus-002",
        "title": "Omega-3 脂肪酸與認知功能",
        "source": "Stonehouse et al., American Journal of Clinical Nutrition, 2013",
        "abstract": "每日補充 1g DHA/EPA 可改善工作記憶和反應速度。Omega-3 對注意力和處理速度有正面影響。",
        "category": "focus"
      },
      {
        "id": "focus-003",
        "title": "冥想訓練對注意力的長期效果",
        "source": "Jha et al., Psychological Science, 2007",
        "abstract": "每日 20 分鐘正念冥想練習 8 週後，可顯著提升持續注意力和注意力切換能力。效果在停止練習後仍可維持。",
        "category": "focus"
      },
      {
        "id": "focus-004",
        "title": "手機通知對專注力的破壞",
        "source": "Stothart et al., Journal of Experimental Psychology, 2015",
        "abstract": "即使不查看手機，通知聲響就足以使錯誤率增加 28%，且需要 23 分鐘才能恢復深度專注。",
        "category": "focus"
      },
      {
        "id": "focus-005",
        "title": "咖啡因對認知表現的時間曲線",
        "source": "McLellan et al., Neuroscience & Biobehavioral Reviews, 2016",
        "abstract": "咖啡因在攝入後 30-60 分鐘達到血液濃度高峰。對注意力的最佳效果窗口為攝入後 1-3 小時。",
        "category": "focus"
      },
      {
        "id": "stress-001",
        "title": "深呼吸對自律神經系統的調節",
        "source": "Ma et al., Frontiers in Psychology, 2017",
        "abstract": "延長呼氣（如 4-7-8 呼吸法）可激活副交感神經，降低心率和皮質醇。每日練習 5 分鐘可顯著降低焦慮評分。",
        "category": "stress"
      },
      {
        "id": "stress-002",
        "title": "感恩日記對心理健康的影響",
        "source": "Emmons & McCullough, Journal of Personality and Social Psychology, 2003",
        "abstract": "每週記錄 5 件感恩事項持續 10 週，可提升整體生活滿意度 25%，減少身體症狀，增加積極情緒。",
        "category": "stress"
      },
      {
        "id": "stress-003",
        "title": "L-Theanine 對壓力反應的調節",
        "source": "Kimura et al., Biological Psychology, 2007",
        "abstract": "200mg L-Theanine 可在 40 分鐘內增加 α 腦波活動，降低心理和生理壓力反應，不引起嗜睡。",
        "category": "stress"
      },
      {
        "id": "stress-004",
        "title": "自然環境接觸對皮質醇的降低",
        "source": "Hunter et al., Frontiers in Psychology, 2019",
        "abstract": "在自然環境中停留 20-30 分鐘可使唾液皮質醇下降 21%。即使是城市公園也有效果。",
        "category": "stress"
      },
      {
        "id": "stress-005",
        "title": "社交連結對壓力緩衝的作用",
        "source": "Cohen et al., Psychological Science, 2015",
        "abstract": "擁有社交支持可減少壓力對免疫系統的負面影響。每日一次有意義的社交互動可降低壓力感受 20%。",
        "category": "stress"
      },
      {
        "id": "general-001",
        "title": "習慣形成的神經可塑性",
        "source": "Lally et al., European Journal of Social Psychology, 2010",
        "abstract": "新習慣平均需要 66 天才能自動化。初期順利完成對長期維持至關重要，漏一天不會重置進度。",
        "category": "general"
      },
      {
        "id": "general-002",
        "title": "目標公開承諾對達成率的影響",
        "source": "Hollenbeck et al., Organizational Behavior and Human Decision Processes, 1989",
        "abstract": "公開宣告目標並記錄進度可使達成率提升 33%。可視化進度是維持動機的關鍵因素。",
        "category": "general"
      },
      {
        "id": "general-003",
        "title": "睡眠對情緒記憶處理的作用",
        "source": "van der Helm et al., Current Biology, 2011",
        "abstract": "REM 睡眠幫助處理情緒記憶，降低杏仁核反應性。睡眠充足者次日對負面事件的情緒反應降低 40%。",
        "category": "general"
      },
      {
        "id": "general-004",
        "title": "運動對大腦 BDNF 的影響",
        "source": "Ratey, Spark: The Revolutionary New Science of Exercise and the Brain, 2008",
        "abstract": "有氧運動可使大腦 BDNF（腦源性神經營養因子）增加，促進神經新生，改善學習記憶和情緒調節。",
        "category": "general"
      },
      {
        "id": "general-005",
        "title": "飲食發炎指數與情緒健康",
        "source": "Adjibade et al., British Journal of Nutrition, 2017",
        "abstract": "高發炎飲食（加工食品、精緻糖）與抑鬱症狀增加相關。抗發炎飲食可改善情緒和能量水平。",
        "category": "general"
      }
    ]

    print(f"📚 Found {len(articles)} articles to embed.")
    build_knowledge_base(articles)
    print("✅ Done! Knowledge base is ready.")

if __name__ == "__main__":
    main()
