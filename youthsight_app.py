import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import math
import random

# Streamlit sayfa yapılandırması
st.set_page_config(layout="centered", page_title="YouthSight", page_icon="✨")

# --- Session State Initializasyonu ---
# Uygulamanın hangi sayfasında olduğumuzu tutar
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'intro'
# Çocuğun kişisel bilgilerini saklar
if 'child_info' not in st.session_state:
    st.session_state.child_info = {}
# Aile bilgilerini saklar (ebeveyn ve büyük ebeveyn)
if 'family_info' not in st.session_state:
    st.session_state.family_info = {}
# Çocuğun yanıtlarını saklar
if 'child_answers' not in st.session_state:
    st.session_state.child_answers = {}
# Öğretmen bilgilerini saklar
if 'teacher_info' not in st.session_state:
    st.session_state.teacher_info = {}
# Öğretmen bölümünün gösterilip gösterilmeyeceğini kontrol eder
if 'show_teacher_section' not in st.session_state:
    st.session_state.show_teacher_section = False

# --- Sabitler ve Yardımcı Fonksiyonlar ---

# Göz Renkleri Seçenekleri listesi
EYE_COLORS = ["Mavi", "Yeşil", "Ela", "Kahverengi", "Siyah", "Diğer"]

# Dünya Olayları (Doğum yılına göre rapor girişi için pozitif ve gerçek bilgiler)
WORLD_EVENTS = {
    2007: "tüm dünyada 1 milyar ağaç dikilmesi hedefine ulaşılan",
    2008: "ilk iPhone'un piyasaya sürülmesiyle teknolojinin devrim yarattığı",
    2009: "ilk Bitcoin'in madenciliği ile dijital para çağının başladığı",
    2010: "Instagram'ın hayatımıza girmesiyle anları paylaşmanın dönüştüğü",
    2011: "Dünya nüfusunun 7 milyara ulaştığı",
    2012: "Londra Olimpiyatları'nın spor ve birliği kutladığı",
    2013: "ilk 3D yazıcıların evlere girmeye başladığı",
    2014: "insanlığın Mars'ta su olduğuna dair önemli ipuçları keşfettiği",
    2015: "evrenin ilk fotoğrafının çekildiği",
    2016: "yapay zeka teknolojilerinin hayatımıza daha çok girdiği",
    2017: "dünyanın en hızlı elektrikli otomobillerinin rekorlar kırdığı",
    2018: "uzay turizminin bir adım daha yaklaştığı",
    2019: "insanlığın Ay'a dönüş yolculuğuna dair büyük planlar yaptığı",
    2020: "uzaktan çalışmanın ve eğitimin yaygınlaştığı",
    2021: "James Webb Uzay Teleskobu'nun evrenin sırlarını aralamaya başladığı",
    2022: "yenilenebilir enerji kaynaklarının dünya çapında hızla yayıldığı",
    2023: "yapay zekanın yaratıcılıkta yeni ufuklar açtığı",
    2024: "Mars'a insanlı yolculuk planlarının hız kazandığı",
    2025: "daha yaşanabilir bir dünya için sürdürülebilirlik projelerinin arttığı"
}

# Ünlü Kişiler ve Boyları (Tahmini boy karşılaştırması için örnekler)
FAMOUS_PEOPLE = {
    "male": [
        {"name": "Tom Holland (Spider-Man)", "height_cm": 173},
        {"name": "Ryan Reynolds (Deadpool)", "height_cm": 188},
        {"name": "Chris Hemsworth (Thor)", "height_cm": 190},
        {"name": "Dwayne 'The Rock' Johnson", "height_cm": 196},
        {"name": "Lionel Messi", "height_cm": 170},
        {"name": "Cristiano Ronaldo", "height_cm": 187},
    ],
    "female": [
        {"name": "Zendaya", "height_cm": 178},
        {"name": "Gal Gadot (Wonder Woman)", "height_cm": 178},
        {"name": "Margot Robbie", "height_cm": 168},
        {"name": "Taylor Swift", "height_cm": 180},
        {"name": "Serena Williams", "height_cm": 175},
        {"name": "Emma Watson", "height_cm": 165},
    ]
}


def get_world_fact(year):
    """Belirtilen doğum yılına göre pozitif bir dünya olayı döndürür."""
    return WORLD_EVENTS.get(year, "teknolojinin hızla ilerlediği ve yeni keşiflerin yapıldığı")


def get_famous_person_height(height_cm, gender):
    """Tahmini boya en yakın ünlü kişiyi (belirtilen cinsiyette) döndürür."""
    people = FAMOUS_PEOPLE[gender]
    closest_person = None
    min_diff = float('inf')

    for person in people:
        diff = abs(person["height_cm"] - height_cm)
        if diff < min_diff:
            min_diff = diff
            closest_person = person

    if closest_person:
        return f"{closest_person['name']} ({closest_person['height_cm']} cm)"
    return "birçok ünlü isimle aynı boyda"  # Varsayılan mesaj


def predict_height(child_gender, mother_height, father_height, grand_parents_heights=None):
    """
    Çocuğun tahmini yetişkin boyunu Mid-Parental Height formülüyle hesaplar.
    Büyük ebeveyn verileri opsiyoneldir.
    """
    if not mother_height or not father_height:  # Ebeveyn boyları yoksa tahmin yapma
        return None

    avg_parent_height = (mother_height + father_height) / 2

    # Cinsiyete göre ortalama boya ekleme/çıkarma
    if child_gender == "Erkek":
        predicted_height = avg_parent_height + 6.5
    elif child_gender == "Kız":
        predicted_height = avg_parent_height - 6.5
    else:  # Belirtmek İstemiyorum veya Diğer
        predicted_height = avg_parent_height

    # Büyük ebeveyn boyları varsa ortalamaya dahil edilebilir (basit bir yaklaşım)
    if grand_parents_heights:
        valid_grand_heights = [h for h in grand_parents_heights if h is not None]
        if valid_grand_heights:
            # Büyük ebeveyn boylarının ortalamasını alıp genel ortalamayı etkileme
            predicted_height = (predicted_height * 2 + sum(valid_grand_heights) / len(valid_grand_heights)) / 3

    return round(predicted_height)


def predict_eye_color_chance(family_eye_colors):
    """
    Ailenin göz renklerine göre çocuğun potansiyel göz renklerini tahmin eder.
    Basit Mendel genetiği taklidi (Kahverengi > Yeşil > Mavi dominantlık sırası).
    """
    # Göz renklerinin basit dominantlık skorları (yüksek skor = daha dominant)
    dominant_scores = {"Kahverengi": 3, "Siyah": 3, "Ela": 2.5, "Yeşil": 2, "Mavi": 1, "Diğer": 0.5}

    color_scores_sum = {}
    for color in family_eye_colors:
        if color and color != "Seçiniz":
            score = dominant_scores.get(color, 0)
            color_scores_sum[color] = color_scores_sum.get(color, 0) + score

    total_score_sum = sum(color_scores_sum.values())

    if total_score_sum == 0:
        return {"Belirlenemedi": "Yetersiz bilgi (50% Mavi, 50% Kahverengi)"}  # Varsayılan

    predictions = {}
    for color, score_sum in color_scores_sum.items():
        percentage = (score_sum / total_score_sum) * 100
        predictions[color] = f"{round(percentage)}%"

    # En yüksek yüzdeye sahip renkleri başa getir
    sorted_predictions = sorted(predictions.items(), key=lambda item: int(item[1].strip('%')), reverse=True)
    return dict(sorted_predictions)


def predict_first_child_gender(mother_first_child, father_first_child):
    """
    Ebeveynlerin ilk çocuk cinsiyetlerine göre çocuğun gelecekteki ilk çocuk cinsiyetini tahmin eder.
    """
    genders = []
    if mother_first_child in ["Kız", "Erkek"]:
        genders.append(mother_first_child)
    if father_first_child in ["Kız", "Erkek"]:
        genders.append(father_first_child)

    if not genders:  # Eğer ebeveynlerden bilgi yoksa %50-%50
        return {"Kız": "50%", "Erkek": "50%"}

    girl_count = genders.count("Kız")
    boy_count = genders.count("Erkek")
    total_count = len(genders)

    girl_chance = round((girl_count / total_count) * 100)
    boy_chance = 100 - girl_chance
    return {"Kız": f"{girl_chance}%", "Erkek": f"{boy_chance}%"}


# --- Karakter Tipi, Enstrüman, Algılama, Spor ve Meslek Yatkınlığı Tahminleme Fonksiyonu ---

def analyze_character_and_aptitude(parent_answers, child_answers, teacher_answers):
    """
    Ebeveyn, çocuk ve (varsa) öğretmen cevaplarını analiz ederek çeşitli yatkınlıkları tahmin eder.
    Her bir yanıt seçeneği belirli karakter/yetkinlik alanlarına puanlar ekler.
    """
    scores = {
        "creative": 0, "analytical": 0, "social": 0, "explorer": 0,
        "musical": 0, "athletic": 0, "artistic_visual": 0,
        "kinesthetic_learner": 0, "auditory_learner": 0, "visual_learner": 0
    }

    # Ebeveyn Cevaplarına Göre Puanlama
    # Parmak Yapısı (Enstrüman yatkınlığı için)
    finger_type = parent_answers.get("finger_type")
    if finger_type == "İnce ve Uzun":
        scores["musical"] += 3  # Yaylılar, piyano için elverişli olabilir
        scores["artistic_visual"] += 1
    elif finger_type == "Kısa ve Kalın":
        scores["musical"] += 2  # Davul, darbuka gibi ritmik enstrümanlar için elverişli olabilir
        scores["athletic"] += 1

    # Seslere Tepki (Müzikal yatkınlık için)
    sound_reactions = parent_answers.get("sound_reactions", [])
    if "Melodik Sesler (Şarkılar, Enstrümanlar)" in sound_reactions:
        scores["musical"] += 4
        scores["auditory_learner"] += 2
    if "Ritmik Sesler (Davul, Alkış)" in sound_reactions:
        scores["musical"] += 3
        scores["athletic"] += 1
        scores["kinesthetic_learner"] += 1
    if "Doğa Sesleri (Kuşlar, Su)" in sound_reactions:
        scores["explorer"] += 1
    if "İnsan Sesleri (Konuşma, Kahkaha)" in sound_reactions:
        scores["social"] += 1

    # Problemle Karşılaştığında Tepki (Karakter tipi için)
    problem_reaction = parent_answers.get("problem_reaction")
    if problem_reaction == "Sakin Kalır, Çözüm Arar":
        scores["analytical"] += 3
        scores["creative"] += 1
    elif problem_reaction == "Yardım İster":
        scores["social"] += 1
    elif problem_reaction == "Hızlıca Pes Eder":
        scores["analytical"] -= 1  # Negatif etki
    elif problem_reaction == "Yaratıcı Çözümler Bulmaya Çalışır":
        scores["creative"] += 3
        scores["analytical"] += 1

    # Yeni Ortamlara Tutum (Karakter tipi için)
    new_environment_attitude = parent_answers.get("new_environment_attitude")
    if new_environment_attitude == "Çabuk Uyum Sağlar, Sosyaldir":
        scores["social"] += 3
        scores["explorer"] += 1
    elif new_environment_attitude == "Gözlemlemeyi Sever, Yavaşça Açılır":
        scores["analytical"] += 1
    elif new_environment_attitude == "Çekingen Davranır":
        scores["social"] -= 1  # Negatif etki
    elif new_environment_attitude == "Liderlik Etmeye Çalışır":
        scores["social"] += 2
        scores["explorer"] += 1

    # En Sevdiği Oyun Türleri (Çeşitli yatkınlıklar için)
    favorite_game_types = parent_answers.get("favorite_game_types", [])
    if "Yapı İnşa Etme (Lego, Yapboz)" in favorite_game_types:
        scores["analytical"] += 2
        scores["creative"] += 1
        scores["kinesthetic_learner"] += 1
    if "Sanatsal Aktiviteler (Resim, Boyama)" in favorite_game_types:
        scores["artistic_visual"] += 3
        scores["creative"] += 2
        scores["visual_learner"] += 1
    if "Açık Hava Oyunları (Koşma, Zıplama)" in favorite_game_types:
        scores["athletic"] += 3
        scores["kinesthetic_learner"] += 2
        scores["explorer"] += 1
    if "Rol Yapma Oyunları" in favorite_game_types:
        scores["social"] += 2
        scores["creative"] += 1
    if "Zeka Oyunları (Satranç, Hafıza)" in favorite_game_types:
        scores["analytical"] += 3
        scores["visual_learner"] += 1
    if "Müzik Dinleme/Yapma" in favorite_game_types:
        scores["musical"] += 3
        scores["auditory_learner"] += 2

    # Çocuk Cevaplarına Göre Puanlama (Her sorunun yanıtına göre özel puanlama)
    # Q1: Ormanda kaybolsan ne alırsın?
    q1_ans = child_answers.get("q1")
    if q1_ans == "Boyama kalemi ve defter":
        scores["creative"] += 2
        scores["artistic_visual"] += 1
    elif q1_ans == "Bir pusula ve harita":
        scores["analytical"] += 2
        scores["explorer"] += 1
    elif q1_ans == "Bir müzik çalar ve kulaklık":
        scores["musical"] += 2
        scores["auditory_learner"] += 1
    elif q1_ans == "Bir kitap":
        scores["analytical"] += 1
        scores["visual_learner"] += 1
    elif q1_ans == "Bir fener ve uyku tulumu":
        scores["explorer"] += 2

    # Q2: Bir şarkı yazsan konusu ne olurdu?
    q2_ans = child_answers.get("q2")
    if q2_ans == "Kahramanlık ve macera dolu bir hikaye":
        scores["explorer"] += 2
        scores["creative"] += 1
    elif q2_ans == "Doğa ve hayvanlar hakkında":
        scores["creative"] += 1
    elif q2_ans == "Arkadaşlık ve paylaşım üzerine":
        scores["social"] += 2
    elif q2_ans == "Uzay ve bilinmeyenler hakkında":
        scores["analytical"] += 1
        scores["explorer"] += 1
    elif q2_ans == "Hayallerim ve dileklerim hakkında":
        scores["creative"] += 2

    # Q3: Hangi aktivite seni daha çok eğlendirir?
    q3_ans = child_answers.get("q3")
    if q3_ans == "Resim çizmek veya boyama yapmak":
        scores["artistic_visual"] += 3
        scores["creative"] += 1
        scores["visual_learner"] += 1
    elif q3_ans == "Şarkı söylemek veya enstrüman çalmak":
        scores["musical"] += 3
        scores["auditory_learner"] += 2
    elif q3_ans == "Hikaye anlatmak veya oyun kurmak":
        scores["creative"] += 2
        scores["social"] += 1
    elif q3_ans == "Yapboz yapmak veya bulmaca çözmek":
        scores["analytical"] += 2
        scores["visual_learner"] += 1
    elif q3_ans == "Açık havada oyun oynamak":
        scores["athletic"] += 2
        scores["kinesthetic_learner"] += 2

    # Q4: Yeni bir oyun öğrenirken nasıl hissedersin?
    q4_ans = child_answers.get("q4")
    if q4_ans == "Çok heyecanlanır ve hemen öğrenmek isterim!":
        scores["explorer"] += 2
        scores["kinesthetic_learner"] += 1
    elif q4_ans == "Biraz çekingen olurum, önce izlemeyi tercih ederim.":
        scores["analytical"] += 1
        scores["social"] -= 1  # Çekingenlik sosyal skoru düşürebilir
    elif q4_ans == "Herkesle birlikte eğlenmek için sabırsızlanırım.":
        scores["social"] += 2
    elif q4_ans == "Kuralları iyice öğrenene kadar biraz gergin olurum.":
        scores["analytical"] += 1
    elif q4_ans == "Kendi kurallarımı koymayı tercih ederim.":
        scores["creative"] += 1
        scores["explorer"] += 1

    # Q5: Bir bilmeceyi çözmek için ne kadar uğraşırsın?
    q5_ans = child_answers.get("q5")
    if q5_ans == "Cevabı bulana kadar asla pes etmem!":
        scores["analytical"] += 3
        scores["explorer"] += 1
    elif q5_ans == "Biraz uğraşır, bulamazsam yardım isterim.":
        scores["social"] += 1
    elif q5_ans == "Hızlıca sıkılır, başka bir şeye geçerim.":
        scores["analytical"] -= 1
    elif q5_ans == "Arkadaşlarımın yardımını isterim.":
        scores["social"] += 1
    elif q5_ans == "Farklı yollar denemeyi severim.":
        scores["creative"] += 2

    # Q6: Bir şeyi yapmanın en iyi yolunu bulmak için ne yaparsın?
    q6_ans = child_answers.get("q6")
    if q6_ans == "Önce kendi fikirlerimi denerim.":
        scores["creative"] += 2
        scores["explorer"] += 1
    elif q6_ans == "Bilen birine sorarım.":
        scores["social"] += 1
    elif q6_ans == "Kitaplardan veya internetten araştırırım.":
        scores["analytical"] += 2
        scores["visual_learner"] += 1
    elif q6_ans == "Arkadaşlarımla beyin fırtınası yaparım.":
        scores["social"] += 2
        scores["analytical"] += 1
    elif q6_ans == "Hemen denemeye başlarım.":
        scores["kinesthetic_learner"] += 1
        scores["explorer"] += 1

    # Q7: En sevdiğin süper kahraman hangisi ve neden?
    q7_ans = child_answers.get("q7")
    if q7_ans == "Örümcek Adam (Çünkü çevik ve zeki)":
        scores["athletic"] += 2
        scores["analytical"] += 1
    elif q7_ans == "Wonder Woman (Çünkü güçlü ve adaletli)":
        scores["athletic"] += 2
        scores["social"] += 1
    elif q7_ans == "Iron Man (Çünkü icatlar yapıyor)":
        scores["creative"] += 2
        scores["analytical"] += 2
    elif q7_ans == "Kaptan Amerika (Çünkü cesur ve lider)":
        scores["social"] += 2
        scores["explorer"] += 1
    elif q7_ans == "Hulk (Çünkü çok güçlü)":
        scores["athletic"] += 3

    # Q8: Sence hangisi daha eğlenceli?
    q8_ans = child_answers.get("q8")
    if q8_ans == "Bir ağaçta saklambaç oynamak":
        scores["kinesthetic_learner"] += 2
        scores["explorer"] += 1
    elif q8_ans == "Bir labirentte koşmak":
        scores["athletic"] += 2
        scores["kinesthetic_learner"] += 2
    elif q8_ans == "Bir kuş gibi uçmak":
        scores["explorer"] += 2
        scores["creative"] += 1
    elif q8_ans == "Bir balık gibi yüzmek":
        scores["athletic"] += 1
        scores["explorer"] += 1
    elif q8_ans == "Bir sincap gibi tırmanmak":
        scores["athletic"] += 2
        scores["kinesthetic_learner"] += 1

    # Q9: Yeni bir spor dalı denemek seni heyecanlandırır mı?
    q9_ans = child_answers.get("q9")
    if q9_ans == "Evet, her zaman yenilikleri denemeye açığım!":
        scores["athletic"] += 3
        scores["explorer"] += 2
    elif q9_ans == "Belki, duruma göre değişir.":
        pass
    elif q9_ans == "Hayır, bildiğim sporları yapmayı tercih ederim.":
        scores["explorer"] -= 1  # Yeniliğe kapalılık
    elif q9_ans == "Sadece arkadaşlarım deniyorsa denerim.":
        scores["social"] += 1
    elif q9_ans == "Sadece izlemeyi tercih ederim.":
        scores["athletic"] -= 1

    # Q10: Arkadaşlarınla oynarken en çok ne yapmayı seversin?
    q10_ans = child_answers.get("q10")
    if q10_ans == "Yeni oyunlar icat etmeyi":
        scores["creative"] += 2
        scores["social"] += 1
    elif q10_ans == "Kurallara uyarak oynamayı":
        scores["analytical"] += 1
        scores["social"] += 1
    elif q10_ans == "Sadece sohbet etmeyi ve gülmeyi":
        scores["social"] += 3
    elif q10_ans == "Lider olup oyunları yönetmeyi":
        scores["social"] += 2
        scores["explorer"] += 1
    elif q10_ans == "Herkesin iyi vakit geçirmesini sağlamayı":
        scores["social"] += 3
        scores["creative"] += 1

    # Öğretmen Cevaplarına Göre Puanlama (Opsiyonel)
    if teacher_answers and st.session_state.show_teacher_section:
        if teacher_answers.get("general_performance") == "Çok İyi":
            scores["analytical"] += 1
            scores["creative"] += 1
        if "sosyal" in teacher_answers.get("social_skills", "").lower() or "iletişim" in teacher_answers.get(
                "social_skills", "").lower():
            scores["social"] += 1
        if "sanat" in teacher_answers.get("artistic_aptitudes", "").lower() or "çizim" in teacher_answers.get(
                "artistic_aptitudes", "").lower():
            scores["artistic_visual"] += 1
        if "hareketli" in teacher_answers.get("physical_aptitude", "").lower() or "spor" in teacher_answers.get(
                "physical_aptitude", "").lower():
            scores["athletic"] += 1
        # Öğrenme stili metin alanından anahtar kelimelerle algılama becerilerini güçlendirme
        if "görsel" in teacher_answers.get("learning_style", "").lower():
            scores["visual_learner"] += 1
        if "işitsel" in teacher_answers.get("learning_style", "").lower():
            scores["auditory_learner"] += 1
        if "kinestetik" in teacher_answers.get("learning_style", "").lower() or "yaparak" in teacher_answers.get(
                "learning_style", "").lower():
            scores["kinesthetic_learner"] += 1

    # --- Karakter Tipi Tahmini ---
    character_types = {
        "creative": {"name": "Yaratıcı Mucit",
                     "description": "Hayal gücü çok geniş, yeni fikirler üretmeyi seven ve sanatla iç içe bir ruha sahipsin. Dünyaya farklı bir gözle bakarsın.",
                     "famous_example": "Leonardo da Vinci gibi büyük bir sanatçı veya Steve Jobs gibi bir vizyoner."},
        "analytical": {"name": "Akılcı Kaşif",
                       "description": "Mantık ve düzen senin için önemli. Problemleri çözmeyi, detayları incelemeyi ve yeni şeyler öğrenmeyi seversin. Bilim ve araştırmaya yatkınsın.",
                       "famous_example": "Albert Einstein gibi bir bilim insanı veya Sherlock Holmes gibi bir dedektif."},
        "social": {"name": "Sosyal Kelebek",
                   "description": "İnsanlarla iletişim kurmayı, yeni arkadaşlar edinmeyi ve grupla birlikte hareket etmeyi seversin. Liderlik etme veya başkalarına yardım etme potansiyelin yüksek.",
                   "famous_example": "Malala Yousafzai gibi bir aktivist veya Oprah Winfrey gibi bir iletişimci."},
        "explorer": {"name": "Maceracı Ruh",
                     "description": "Yeni yerler keşfetmek, bilinmeyene doğru yolculuk yapmak ve risk almaktan çekinmeyen bir yapın var. Heyecan ve öğrenme arayışın bitmez.",
                     "famous_example": "Kristof Kolomb gibi bir kaşif veya Indiana Jones gibi bir maceraperes t."},
    }

    # Ana karakter tipi skorları
    main_char_scores = {
        "creative": scores["creative"],
        "analytical": scores["analytical"],
        "social": scores["social"],
        "explorer": scores["explorer"]
    }

    max_score = -1
    predicted_character_key = None

    # En yüksek puanlı ana karakter tipini bul
    for char_key, score in main_char_scores.items():
        if score > max_score:
            max_score = score
            predicted_character_key = char_key

    # Eğer tüm skorlar sıfırsa veya eşitse varsayılan bir tip ata
    if max_score <= 0 or len(set(main_char_scores.values())) == 1:  # Tüm skorlar sıfır veya eşitse
        predicted_character_type = "Dengeli Ruh"
        predicted_character_description = "Henüz belirgin bir karakter özelliğin baskın değil, bu da senin her alana açık olduğun anlamına geliyor!"
        predicted_character_example = "Her alanda kendini geliştirebilen uyumlu bir karakter"
    else:
        predicted_character_type = character_types[predicted_character_key]["name"]
        predicted_character_description = character_types[predicted_character_key]["description"]
        predicted_character_example = character_types[predicted_character_key]["famous_example"]

    # Karakter yüzdeleri (Pasta grafik için)
    total_character_score_for_pie = sum(main_char_scores.values())
    character_percentages = {}
    if total_character_score_for_pie > 0:
        for char_key, score in main_char_scores.items():
            character_percentages[character_types[char_key]["name"]] = (score / total_character_score_for_pie) * 100
    else:  # Eğer skorlar sıfırsa eşit dağılım göster
        for char_key in main_char_scores.keys():
            character_percentages[character_types[char_key]["name"]] = 100 / len(main_char_scores)

    # --- Enstrüman Yatkınlığı ---
    instrument_aptitudes = []
    if scores["musical"] >= 6:
        instrument_aptitudes.append("Piyano (Hem melodi hem ritim uyumu için)")
        instrument_aptitudes.append("Gitar (Müzikal duyarlılık ve parmak becerisi için)")
    if scores["musical"] >= 3:
        instrument_aptitudes.append("Darbuka (Ritmik duygu için)")
        instrument_aptitudes.append("Bateri (Ritmik duygu ve enerji için)")
    if scores["artistic_visual"] >= 2 and parent_answers.get("finger_type") == "İnce ve Uzun":
        instrument_aptitudes.append("Keman (İnce motor beceri ve estetik duygu için)")
    if scores["musical"] >= 5 and "Melodik Sesler (Şarkılar, Enstrümanlar)" in parent_answers.get("sound_reactions",
                                                                                                  []):
        instrument_aptitudes.append("Saksafon/Flüt (Melodik yatkınlık ve nefes kontrolü için)")

    if not instrument_aptitudes:
        instrument_aptitudes.append(
            "Henüz belirgin bir enstrüman yatkınlığı gözlemlenmedi, ancak keşfetmeye açık olabilirsin! Farklı enstrümanları denemekten çekinme.")

    instrument_aptitudes = list(set(instrument_aptitudes))  # Tekrarları kaldır

    # --- Algılama Becerileri ---
    perception_skills = {}
    # Toplam puanlama öğrenme stilleri için. En az 1 puan verilmeli ki bölme hatası olmasın
    total_learner_score = scores["visual_learner"] + scores["auditory_learner"] + scores["kinesthetic_learner"] + 0.1

    perception_percentages = {
        "Görsel": (scores["visual_learner"] / total_learner_score) * 100,
        "İşitsel": (scores["auditory_learner"] / total_learner_score) * 100,
        "Kinestetik": (scores["kinesthetic_learner"] / total_learner_score) * 100,
    }

    # En yüksek yüzdeye sahip algılama becerisini bul
    max_perc_score = -1
    dominant_perception = "Dengeli Algılama"
    dominant_description = "Farklı algılama becerilerin dengeli bir şekilde gelişmiş. Bu da her türlü öğrenme ortamına kolayca adapte olabileceğin anlamına geliyor."

    if perception_percentages["Görsel"] > max_perc_score:
        max_perc_score = perception_percentages["Görsel"]
        dominant_perception = "Görsel Algılama"
        dominant_description = "Öğrenirken görselleri, şekilleri ve renkleri kullanarak daha kolay anlarsın. Kitaplar, haritalar ve çizimler senin için çok etkili öğrenme araçlarıdır."
    if perception_percentages["İşitsel"] > max_perc_score:  # Eşitlik durumunda sonrakini seçebilir
        max_perc_score = perception_percentages["İşitsel"]
        dominant_perception = "İşitsel Algılama"
        dominant_description = "Sesleri, konuşmaları ve müziği dinleyerek daha iyi öğrenirsin. Tartışmalar, dinleme alıştırmaları ve sesli okumalar senin için faydalı olabilir."
    if perception_percentages["Kinestetik"] > max_perc_score:
        max_perc_score = perception_percentages["Kinestetik"]
        dominant_perception = "Kinestetik (Hareket Temelli) Algılama"
        dominant_description = "Yaparak, dokunarak ve hareket ederek öğrenmeyi seversin. Deneyler, spor ve uygulamalı projeler senin için en verimli öğrenme yöntemleridir."

    perception_skills = {"dominant": dominant_perception, "description": dominant_description}

    # --- Spor Yatkınlığı ---
    sport_aptitude = []
    if scores["athletic"] >= 5:
        sport_aptitude.append("Takım Sporları (Futbol, Basketbol, Voleybol gibi)")
        sport_aptitude.append("Bireysel Sporlar (Koşu, Yüzme, Atletizm gibi)")
    elif scores["athletic"] >= 3:
        sport_aptitude.append("Açık Hava Sporları (Doğa yürüyüşü, Bisiklet gibi)")
    if scores["kinesthetic_learner"] >= 3 and scores["artistic_visual"] >= 1:
        sport_aptitude.append("Sanatsal Sporlar (Dans, Cimnastik, Artistik Buz Pateni gibi)")
    if not sport_aptitude:
        sport_aptitude.append(
            "Henüz belirgin bir spor yatkınlığı gözlemlenmedi, ama her deneme yeni bir keşif olabilir!")
    sport_aptitude = list(set(sport_aptitude))

    # --- Meslek Yatkınlığı ---
    profession_aptitude = []
    if scores["creative"] >= 4:
        profession_aptitude.append("Sanatçı (ressam, heykeltıraş)")
        profession_aptitude.append("Yazar/Hikaye Anlatıcısı")
        profession_aptitude.append("Tasarımcı (grafik, moda, iç mekan)")
    if scores["analytical"] >= 4:
        profession_aptitude.append("Bilim İnsanı (araştırmacı, fizikçi, kimyager)")
        profession_aptitude.append("Mühendis (yazılım, inşaat, makine)")
        profession_aptitude.append("Öğretmen/Akademisyen")
    if scores["social"] >= 4:
        profession_aptitude.append("Psikolog/Danışman")
        profession_aptitude.append("Sosyal Hizmet Uzmanı")
        profession_aptitude.append("Doktor/Sağlık Çalışanı")
        profession_aptitude.append("Lider/Yönetici")
    if scores["explorer"] >= 3:
        profession_aptitude.append("Kaşif/Coğrafyacı")
        profession_aptitude.append("Maceraperest/Rehber")
        profession_aptitude.append("Gazeteci/Muhabir")
    if scores["athletic"] >= 3:
        profession_aptitude.append("Sporcu/Antrenör")
    if scores["musical"] >= 3:
        profession_aptitude.append("Müzisyen/Besteci")
        profession_aptitude.append("Müzik Öğretmeni")
    if not profession_aptitude:
        profession_aptitude.append(
            "Henüz belirgin bir meslek yatkınlığı gözlemlenmedi, gelecekte birçok farklı alanı deneyimleyebilirsin!")
    profession_aptitude = list(set(profession_aptitude))

    return {
        "character_type": predicted_character_type,
        "character_description": predicted_character_description,
        "character_example": predicted_character_example,
        "character_percentages": character_percentages,
        "instrument_aptitudes": instrument_aptitudes,
        "perception_skills": perception_skills,
        "perception_percentages": perception_percentages,
        "sport_aptitude": sport_aptitude,
        "profession_aptitude": profession_aptitude,
        "weight_tendency": "Genetik yapın ve yaşam tarzın, ileride kilonu yönetme eğilimini belirleyecektir. Dengeli beslenme ve aktif bir yaşam her zaman önemlidir.",
        # Basit genel ifade
    }


# --- Sayfa Fonksiyonları ---

def page_intro():
    """Giriş sayfasını gösterir."""
    st.markdown(
        "<h1 style='text-align: center; color: #4CAF50;'>YouthSight <span style='font-size:0.7em;'>✨</span></h1>",
        unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Geleceğini Keşfet!</h3>", unsafe_allow_html=True)

    st.image("https://placehold.co/600x300/A8E6CE/3A3A3A?text=YouthSight+Logo+%26+İllüstrasyon",
             caption="YouthSight: Çocukların Gelecek Potansiyelini Keşfedin")

    st.markdown("""
    <div style="background-color:#e0ffe0; padding:15px; border-radius:10px; margin-top:20px;">
        <p style="font-size:1.1em; color:#333;">
            YouthSight, <span style="font-weight:bold;">9-12 yaş</span> arasındaki çocukların sanatsal, zihinsel ve fiziksel gelişim potansiyellerini
            eğlenceli bir envanter testiyle keşfetmeye yardımcı olur. Bu envanter sayesinde çocuğunuzun
            kişilik tipini, enstrüman yatkınlıklarını, algılama becerilerini, fiziksel gelişimini ve
            hatta olası meslek eğilimlerini tahmin edebileceğiz!
        </p>
        <p style="font-size:1.1em; color:#333;">
            Unutmayın, bu bir rehberdir ve her çocuğun eş eşsiz bir potansiyeli vardır. Keyifli keşifler!
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Başla", use_container_width=True, help="Envantere başlamak için tıklayın."):
            st.session_state.current_page = 'personal_info'
            st.rerun()


def page_personal_info():
    """Çocuğun kişisel bilgilerini topladığı sayfayı gösterir."""
    st.markdown("<h2 style='color: #4CAF50;'>1. Çocuğun Kişisel Bilgileri</h2>", unsafe_allow_html=True)
    st.markdown(
        "Lütfen çocuğunuzun bilgilerini giriniz. Bu bilgiler, size özel bir rapor oluşturmamız için kullanılacaktır.",
        unsafe_allow_html=True)

    with st.form("child_personal_info_form"):
        # Metin giriş alanları
        st.session_state.child_info['name'] = st.text_input("Adı", value=st.session_state.child_info.get('name', ''),
                                                            help="Çocuğunuzun adı.")
        st.session_state.child_info['surname'] = st.text_input("Soyadı",
                                                               value=st.session_state.child_info.get('surname', ''),
                                                               help="Çocuğunuzun soyadı.")

        # Cinsiyet seçimi
        gender_options = ["Seçiniz", "Kız", "Erkek", "Belirtmek İstemiyorum"]
        default_gender_index = gender_options.index(
            st.session_state.child_info.get('gender', 'Seçiniz')) if st.session_state.child_info.get('gender',
                                                                                                     'Seçiniz') in gender_options else 0
        st.session_state.child_info['gender'] = st.selectbox("Cinsiyet", gender_options,
                                                             index=default_gender_index, help="Çocuğunuzun cinsiyeti.")

        # Doğum tarihi seçimi (9-12 yaş aralığı için filtreli)
        today = datetime.date.today()
        # 12 yaş sınırı (Minimum doğum tarihi)
        min_dob = datetime.date(today.year - 12, 1, 1)
        # 9 yaş sınırı (Maksimum doğum tarihi)
        max_dob = datetime.date(today.year - 9, 12, 31)

        default_dob = st.session_state.child_info.get('dob', datetime.date(today.year - 10, 6,
                                                                           15))  # Varsayılan olarak 10 yaşında bir tarih

        # Eğer varsayılan tarih belirlenen aralıkta değilse, uygun bir başlangıç değeri ayarla
        if not (min_dob <= default_dob <= max_dob):
            default_dob = datetime.date(today.year - 10, today.month, today.day)  # Yeni bir varsayılan
            if default_dob < min_dob: default_dob = min_dob
            if default_dob > max_dob: default_dob = max_dob

        st.session_state.child_info['dob'] = st.date_input("Doğum Tarihi", value=default_dob, min_value=min_dob,
                                                           max_value=max_dob,
                                                           help="Çocuğunuzun doğum tarihi. (9-12 yaş arası)")

        # Göz rengi seçimi - DÜZELTME BAŞLANGICI
        eye_color_options = ["Seçiniz"] + EYE_COLORS
        default_eye_color = st.session_state.child_info.get('eye_color', 'Seçiniz')
        try:
            default_eye_color_index = eye_color_options.index(default_eye_color)
        except ValueError:
            default_eye_color_index = 0  # 'Seçiniz' veya bulunamazsa ilk seçenek

        st.session_state.child_info['eye_color'] = st.selectbox("Göz Rengi", eye_color_options,
                                                                index=default_eye_color_index,
                                                                help="Çocuğunuzun göz rengi.")
        # DÜZELTME SONUÇLANIYOR

        # Boy girişi
        st.session_state.child_info['height'] = st.number_input("Boy (cm)", min_value=50, max_value=200,
                                                                value=st.session_state.child_info.get('height', 130),
                                                                step=1, help="Çocuğunuzun güncel boyu (santimetre).")

        # Ülke ve şehir bilgileri
        st.session_state.child_info['country'] = st.text_input("Doğduğu Ülke",
                                                               value=st.session_state.child_info.get('country',
                                                                                                     'Türkiye'),
                                                               help="Çocuğunuzun doğduğu ülke.")
        st.session_state.child_info['city'] = st.text_input("Doğduğu Şehir",
                                                            value=st.session_state.child_info.get('city', ''),
                                                            help="Çocuğunuzun doğduğu şehir.")

        # Resim yükleyici (isteğe bağlı)
        uploaded_file = st.file_uploader("Çocuğun Resmi (Opsiyonel)", type=["png", "jpg", "jpeg"],
                                         help="Çocuğunuzun bir fotoğrafını yükleyebilirsiniz. Bu raporunuza dahil edilmeyecektir.")
        if uploaded_file is not None:
            st.session_state.child_info['photo'] = uploaded_file.read()
            st.image(uploaded_file, caption="Yüklenen Resim", width=150)
        elif 'photo' in st.session_state.child_info and st.session_state.child_info['photo']:
            # Eğer daha önce bir resim yüklendiyse onu göster
            st.image(st.session_state.child_info['photo'], caption="Yüklenen Resim", width=150)

        submitted = st.form_submit_button("Sonraki Adım")
        if submitted:
            # Zorunlu alanların doldurulup doldurulmadığını kontrol et
            required_fields = ['name', 'surname', 'gender', 'dob', 'eye_color', 'height', 'country', 'city']
            missing_fields = [field for field in required_fields if
                              not st.session_state.child_info.get(field) or st.session_state.child_info.get(
                                  field) == "Seçiniz"]

            if missing_fields:
                st.error(f"Lütfen tüm zorunlu alanları doldurunuz: {', '.join(missing_fields)}")
            else:
                st.session_state.current_page = 'family_info'
                st.rerun()


def page_family_info():
    """Ailenin genetik ve erken gelişim bilgilerini topladığı sayfayı gösterir."""
    st.markdown("<h2 style='color: #4CAF50;'>2. Aile Bilgileri (Ebeveynler İçin)</h2>", unsafe_allow_html=True)
    st.markdown("Çocuğunuzun genetik ve erken gelişimine dair bilgiler için lütfen aşağıdaki formu doldurunuz.",
                unsafe_allow_html=True)

    with st.form("family_info_form"):
        st.markdown("### Annenin Bilgileri")
        st.session_state.family_info['mother_height'] = st.number_input("Boy (cm)", min_value=120, max_value=220,
                                                                        value=st.session_state.family_info.get(
                                                                            'mother_height', 165), step=1, key="m_h",
                                                                        help="Annenin boyu.")

        # Göz rengi seçimi - DÜZELTME BAŞLANGICI
        eye_color_options = ["Seçiniz"] + EYE_COLORS
        default_mother_eye_color = st.session_state.family_info.get('mother_eye_color', 'Seçiniz')
        try:
            default_mother_eye_color_index = eye_color_options.index(default_mother_eye_color)
        except ValueError:
            default_mother_eye_color_index = 0
        st.session_state.family_info['mother_eye_color'] = st.selectbox("Göz Rengi", eye_color_options,
                                                                        index=default_mother_eye_color_index,
                                                                        key="m_ec", help="Annenin göz rengi.")
        # DÜZELTME SONUÇLANIYOR

        gender_first_child_options = ["Seçiniz", "Kız", "Erkek", "Henüz Çocuk Sahibi Olmadı",
                                      "Hatırlamıyorum / Bilmiyorum"]
        default_mother_first_child_gender_index = gender_first_child_options.index(
            st.session_state.family_info.get('mother_first_child_gender',
                                             'Seçiniz')) if st.session_state.family_info.get(
            'mother_first_child_gender', 'Seçiniz') in gender_first_child_options else 0
        st.session_state.family_info['mother_first_child_gender'] = st.selectbox("İlk Çocuğu Kız mıydı Erkek miydi?",
                                                                                 gender_first_child_options,
                                                                                 index=default_mother_first_child_gender_index,
                                                                                 key="m_fcg",
                                                                                 help="Annenin varsa ilk çocuğunun cinsiyeti.")
        st.session_state.family_info['mother_occupation'] = st.text_input("Mesleği (Opsiyonel)",
                                                                          value=st.session_state.family_info.get(
                                                                              'mother_occupation', ''), key="m_occ",
                                                                          help="Annenin mesleği (opsiyonel).")

        st.markdown("### Babanın Bilgileri")
        st.session_state.family_info['father_height'] = st.number_input("Boy (cm)", min_value=120, max_value=220,
                                                                        value=st.session_state.family_info.get(
                                                                            'father_height', 175), step=1, key="f_h",
                                                                        help="Babanın boyu.")

        # Göz rengi seçimi - DÜZELTME BAŞLANGICI
        default_father_eye_color = st.session_state.family_info.get('father_eye_color', 'Seçiniz')
        try:
            default_father_eye_color_index = eye_color_options.index(default_father_eye_color)
        except ValueError:
            default_father_eye_color_index = 0
        st.session_state.family_info['father_eye_color'] = st.selectbox("Göz Rengi", eye_color_options,
                                                                        index=default_father_eye_color_index,
                                                                        key="f_ec", help="Babanın göz rengi.")
        # DÜZELTME SONUÇLANIYOR

        default_father_first_child_gender_index = gender_first_child_options.index(
            st.session_state.family_info.get('father_first_child_gender',
                                             'Seçiniz')) if st.session_state.family_info.get(
            'father_first_child_gender', 'Seçiniz') in gender_first_child_options else 0
        st.session_state.family_info['father_first_child_gender'] = st.selectbox("İlk Çocuğu Kız mıydı Erkek miydi?",
                                                                                 gender_first_child_options,
                                                                                 index=default_father_first_child_gender_index,
                                                                                 key="f_fcg",
                                                                                 help="Babanın varsa ilk çocuğunun cinsiyeti.")
        st.session_state.family_info['father_occupation'] = st.text_input("Mesleği (Opsiyonel)",
                                                                          value=st.session_state.family_info.get(
                                                                              'father_occupation', ''), key="f_occ",
                                                                          help="Babanın mesleği (opsiyonel).")

        st.markdown("### Opsiyonel: Büyük Ebeveyn Bilgileri")
        st.markdown(
            "Çocuğunuzun genetik potansiyelini daha iyi anlamak için büyük ebeveyn bilgilerini girebilirsiniz. (Opsiyonel)",
            help="Bu bilgiler, çocuğun tahmini boyu ve göz rengi gibi genetik özelliklerin daha doğru tahmin edilmesine yardımcı olur.")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.session_state.family_info['grandpa_m_height'] = st.number_input("Anne Tarafı Dede Boyu (cm)",
                                                                               min_value=120, max_value=220,
                                                                               value=st.session_state.family_info.get(
                                                                                   'grandpa_m_height', None), step=1,
                                                                               help="Bilmiyorsanız boş bırakın.",
                                                                               key="gpm_h", format="%d")
            # Göz rengi seçimi - DÜZELTME BAŞLANGICI
            default_gpm_eye_color = st.session_state.family_info.get('grandpa_m_eye_color', 'Seçiniz')
            try:
                default_gpm_eye_color_index = eye_color_options.index(default_gpm_eye_color)
            except ValueError:
                default_gpm_eye_color_index = 0
            st.session_state.family_info['grandpa_m_eye_color'] = st.selectbox("Anne Tarafı Dede Göz Rengi",
                                                                               eye_color_options,
                                                                               index=default_gpm_eye_color_index,
                                                                               key="gpm_ec",
                                                                               help="Anne tarafından dedenin göz rengi.")
            # DÜZELTME SONUÇLANIYOR
        with col_m2:
            st.session_state.family_info['grandma_m_height'] = st.number_input("Anne Tarafı Anneanne Boyu (cm)",
                                                                               min_value=120, max_value=220,
                                                                               value=st.session_state.family_info.get(
                                                                                   'grandma_m_height', None), step=1,
                                                                               help="Bilmiyorsanız boş bırakın.",
                                                                               key="gmm_h", format="%d")
            # Göz rengi seçimi - DÜZELTME BAŞLANGICI
            default_gmm_eye_color = st.session_state.family_info.get('grandma_m_eye_color', 'Seçiniz')
            try:
                default_gmm_eye_color_index = eye_color_options.index(default_gmm_eye_color)
            except ValueError:
                default_gmm_eye_color_index = 0
            st.session_state.family_info['grandma_m_eye_color'] = st.selectbox("Anne Tarafı Anneanne Göz Rengi",
                                                                               eye_color_options,
                                                                               index=default_gmm_eye_color_index,
                                                                               key="gmm_ec",
                                                                               help="Anne tarafından anneannenin göz rengi.")
            # DÜZELTME SONUÇLANIYOR

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.session_state.family_info['grandpa_f_height'] = st.number_input("Baba Tarafı Dede Boyu (cm)",
                                                                               min_value=120, max_value=220,
                                                                               value=st.session_state.family_info.get(
                                                                                   'grandpa_f_height', None), step=1,
                                                                               help="Bilmiyorsanız boş bırakın.",
                                                                               key="gpf_h", format="%d")
            # Göz rengi seçimi - DÜZELTME BAŞLANGICI
            default_gpf_eye_color = st.session_state.family_info.get('grandpa_f_eye_color', 'Seçiniz')
            try:
                default_gpf_eye_color_index = eye_color_options.index(default_gpf_eye_color)
            except ValueError:
                default_gpf_eye_color_index = 0
            st.session_state.family_info['grandpa_f_eye_color'] = st.selectbox("Baba Tarafı Dede Göz Rengi",
                                                                               eye_color_options,
                                                                               index=default_gpf_eye_color_index,
                                                                               key="gpf_ec",
                                                                               help="Baba tarafından dedenin göz rengi.")
            # DÜZELTME SONUÇLANIYOR
        with col_f2:
            st.session_state.family_info['grandma_f_height'] = st.number_input("Baba Tarafı Babaanne Boyu (cm)",
                                                                               min_value=120, max_value=220,
                                                                               value=st.session_state.family_info.get(
                                                                                   'grandma_f_height', None), step=1,
                                                                               help="Bilmiyorsanız boş bırakın.",
                                                                               key="gmf_h", format="%d")
            # Göz rengi seçimi - DÜZELTME BAŞLANGICI
            default_gmf_eye_color = st.session_state.family_info.get('grandma_f_eye_color', 'Seçiniz')
            try:
                default_gmf_eye_color_index = eye_color_options.index(default_gmf_eye_color)
            except ValueError:
                default_gmf_eye_color_index = 0
            st.session_state.family_info['grandma_f_eye_color'] = st.selectbox("Baba Tarafı Babaanne Göz Rengi",
                                                                               eye_color_options,
                                                                               index=default_gmf_eye_color_index,
                                                                               key="gmf_ec",
                                                                               help="Baba tarafından babaannenin göz rengi.")
            # DÜZELTME SONUÇLANIYOR

        st.markdown("### Çocuğunuzun Erken Gelişimi ve Yatkınlıkları")
        st.session_state.family_info['sound_reactions'] = st.multiselect(
            "Çocuğunuz Hangi Seslere Daha Çok Tepki Veriyor?",
            ["Melodik Sesler (Şarkılar, Enstrümanlar)", "Ritmik Sesler (Davul, Alkış)", "Doğa Sesleri (Kuşlar, Su)",
             "İnsan Sesleri (Konuşma, Kahkaha)", "Yüksek Sesler", "Düşük Sesler", "Diğer"],
            default=st.session_state.family_info.get('sound_reactions', []),
            help="Çocuğunuzun hangi tür seslere daha duyarlı olduğunu seçin.")

        finger_type_options = ["İnce ve Uzun", "Kısa ve Kalın", "Ortalama", "Bilemiyorum"]
        default_finger_type_index = finger_type_options.index(
            st.session_state.family_info.get('finger_type', 'Ortalama')) if st.session_state.family_info.get(
            'finger_type', 'Ortalama') in finger_type_options else 0
        st.session_state.family_info['finger_type'] = st.radio(
            "Çocuğunuzun Parmak Yapısı Genel Olarak Nasıl?",
            finger_type_options,
            index=default_finger_type_index, help="Çocuğunuzun parmak yapısını tanımlayın.")

        # Hata düzeltme: problem_reaction radio butonunun index listesi güncellendi
        problem_reaction_options = ["Sakin Kalır, Çözüm Arar", "Yardım İster", "Hızlıca Pes Eder", "Sinirlenir/Üzülür",
                                    "Yaratıcı Çözümler Bulmaya Çalışır"]
        default_problem_reaction = st.session_state.family_info.get('problem_reaction', 'Sakin Kalır, Çözüm Arar')
        try:
            problem_reaction_index = problem_reaction_options.index(default_problem_reaction)
        except ValueError:
            problem_reaction_index = 0  # Default değeri seçeneklerde bulunamazsa ilk seçeneği kullan

        st.session_state.family_info['problem_reaction'] = st.radio(
            "Çocuğunuz Bir Problemle Karşılaştığında İlk Tepkisi Ne Olur?",
            problem_reaction_options,
            index=problem_reaction_index, help="Çocuğunuzun problem çözme yaklaşımını seçin.")

        new_environment_attitude_options = ["Çabuk Uyum Sağlar, Sosyaldir", "Gözlemlemeyi Sever, Yavaşça Açılır",
                                            "Çekingen Davranır", "Liderlik Etmeye Çalışır"]
        default_new_environment_attitude_index = new_environment_attitude_options.index(
            st.session_state.family_info.get('new_environment_attitude',
                                             'Çabuk Uyum Sağlar, Sosyaldir')) if st.session_state.family_info.get(
            'new_environment_attitude', 'Çabuk Uyum Sağlar, Sosyaldir') in new_environment_attitude_options else 0
        st.session_state.family_info['new_environment_attitude'] = st.radio(
            "Çocuğunuz Yeni Ortamlara/İnsanlara Karşı Nasıl Bir Tutum Sergiler?",
            new_environment_attitude_options,
            index=default_new_environment_attitude_index, help="Çocuğunuzun sosyal ortamlardaki tutumunu seçin.")

        st.session_state.family_info['favorite_game_types'] = st.multiselect(
            "Çocuğunuzun En Sevdiği Oyun Türleri Nelerdir?",
            ["Yapı İnşa Etme (Lego, Yapboz)", "Sanatsal Aktiviteler (Resim, Boyama)",
             "Açık Hava Oyunları (Koşma, Zıplama)", "Rol Yapma Oyunları", "Zeka Oyunları (Satranç, Hafıza)",
             "Müzik Dinleme/Yapma"],
            default=st.session_state.family_info.get('favorite_game_types', []),
            help="Çocuğunuzun en sevdiği oyun türlerini seçin.")

        submitted = st.form_submit_button("Sonraki Adım")
        if submitted:
            # Zorunlu alan kontrolü (Ebeveyn boy ve göz renkleri)
            required_family_fields = ['mother_height', 'mother_eye_color', 'father_height', 'father_eye_color']
            missing_family_fields = [field for field in required_family_fields if
                                     not st.session_state.family_info.get(field) or st.session_state.family_info.get(
                                         field) == "Seçiniz" or st.session_state.family_info.get(field) == None]

            if missing_family_fields:
                st.error(
                    f"Lütfen anne ve babanın boy ve göz rengi bilgilerini doldurunuz: {', '.join(missing_family_fields)}")
            else:
                st.session_state.current_page = 'child_questions'
                st.rerun()


def page_child_questions():
    """Çocuğun kendi dolduracağı eğlenceli soruları gösterir."""
    st.markdown("<h2 style='color: #4CAF50;'>3. Şimdi Sıra Sende, Sevgili Çocuğum!</h2>", unsafe_allow_html=True)
    st.markdown(
        "Hazır ol! Şimdi senin hakkındaki eğlenceli sorularla dolu bu bölüme geldik. En samimi ve eğlenceli cevaplarını bekliyoruz!",
        unsafe_allow_html=True)
    st.image("https://placehold.co/600x200/ADD8E6/000000?text=Eğlenceli+Çocuk+İllüstrasyonu",
             caption="Hadi Başlayalım!")

    # Çocuğa özel sorular listesi
    questions = [
        {"id": "q1", "text": "Bir ormanda kaybolsan ve yanına sadece 3 şey alabilseydin, bunlar ne olurdu?",
         "options": ["Boyama kalemi ve defter", "Bir pusula ve harita", "Bir müzik çalar ve kulaklık", "Bir kitap",
                     "Bir fener ve uyku tulumu"]},
        {"id": "q2", "text": "Bir şarkı yazsan, konusu ne olurdu?",
         "options": ["Kahramanlık ve macera dolu bir hikaye", "Doğa ve hayvanlar hakkında",
                     "Arkadaşlık ve paylaşım üzerine", "Uzay ve bilinmeyenler hakkında",
                     "Hayallerim ve dileklerim hakkında"]},
        {"id": "q3", "text": "Hangi aktivite seni daha çok eğlendirir?",
         "options": ["Resim çizmek veya boyama yapmak", "Şarkı söylemek veya enstrüman çalmak",
                     "Hikaye anlatmak veya oyun kurmak", "Yapboz yapmak veya bulmaca çözmek",
                     "Açık havada oyun oynamak"]},
        {"id": "q4", "text": "Yeni bir oyun öğrenirken nasıl hissedersin?",
         "options": ["Çok heyecanlanır ve hemen öğrenmek isterim!",
                     "Biraz çekingen olurum, önce izlemeyi tercih ederim.",
                     "Herkesle birlikte eğlenmek için sabırsızlanırım.",
                     "Kuralları iyice öğrenene kadar biraz gergin olurum.",
                     "Kendi kurallarımı koymayı tercih ederim."]},
        {"id": "q5", "text": "Bir bilmeceyi çözmek için ne kadar uğraşırsın?",
         "options": ["Cevabı bulana kadar asla pes etmem!", "Biraz uğraşır, bulamazsam yardım isterim.",
                     "Hızlıca sıkılır, başka bir şeye geçerim.", "Arkadaşlarımın yardımını isterim.",
                     "Farklı yollar denemeyi severim."]},
        {"id": "q6", "text": "Bir şeyi yapmanın en iyi yolunu bulmak için ne yaparsın?",
         "options": ["Önce kendi fikirlerimi denerim.", "Bilen birine sorarım.",
                     "Kitaplardan veya internetten araştırırım.", "Arkadaşlarımla beyin fırtınası yaparım.",
                     "Hemen denemeye başlarım."]},
        {"id": "q7", "text": "En sevdiğin süper kahraman hangisi ve neden?",
         "options": ["Örümcek Adam (Çünkü çevik ve zeki)", "Wonder Woman (Çünkü güçlü ve adaletli)",
                     "Iron Man (Çünkü icatlar yapıyor)", "Kaptan Amerika (Çünkü cesur ve lider)",
                     "Hulk (Çünkü çok güçlü)"]},
        {"id": "q8", "text": "Sence hangisi daha eğlenceli?",
         "options": ["Bir ağaçta saklambaç oynamak", "Bir labirentte koşmak", "Bir kuş gibi uçmak",
                     "Bir balık gibi yüzmek", "Bir sincap gibi tırmanmak"]},
        {"id": "q9", "text": "Yeni bir spor dalı denemek seni heyecanlandırır mı?",
         "options": ["Evet, her zaman yenilikleri denemeye açığım!", "Belki, duruma göre değişir.",
                     "Hayır, bildiğim sporları yapmayı tercih ederim.", "Sadece arkadaşlarım deniyorsa denerim.",
                     "Sadece izlemeyi tercih ederim."]},
        {"id": "q10", "text": "Arkadaşlarınla oynarken en çok ne yapmayı seversin?",
         "options": ["Yeni oyunlar icat etmeyi", "Kurallara uyarak oynamayı", "Sadece sohbet etmeyi ve gülmeyi",
                     "Lider olup oyunları yönetmeyi", "Herkesin iyi vakit geçirmesini sağlamayı"]}
    ]

    with st.form("child_questions_form"):
        # Her bir soruyu döngü ile ekle
        for q in questions:
            # Her bir radyo butonunun varsayılan değerini session_state'ten al
            current_value = st.session_state.child_answers.get(q["id"])
            try:
                # `q["options"]` zaten doğru listeyi içerdiği için direkt onu kullan
                default_index = q["options"].index(current_value) if current_value in q["options"] else 0
            except ValueError:  # Eğer kaydedilen değer seçeneklerde yoksa ilk seçeneği varsayılan yap
                default_index = 0

            st.session_state.child_answers[q["id"]] = st.radio(
                q["text"], q["options"],
                index=default_index,
                key=q["id"], help=f"Lütfen '{q['text']}' sorusuna cevap verin."
            )

        col_prev, col_next = st.columns(2)
        with col_prev:
            # DÜZELTME: st.form_submit_button içinde key parametresi kullanılmaz.
            if st.form_submit_button("Geri"):  # key="child_prev" kaldırıldı
                st.session_state.current_page = 'family_info'
                st.rerun()
        with col_next:
            # DÜZELTME: st.form_submit_button içinde key parametresi kullanılmaz.
            if st.form_submit_button("Bitir ve Raporu Oluştur"):  # key="child_next" kaldırıldı
                # Tüm soruların cevaplandığını kontrol et
                all_questions_answered = True
                for q in questions:
                    if not st.session_state.child_answers.get(q["id"]):
                        all_questions_answered = False
                        break

                if not all_questions_answered:
                    st.error("Lütfen tüm soruları cevaplayınız.")
                else:
                    st.session_state.current_page = 'report'
                    st.rerun()


def plot_to_base64(fig):
    """Matplotlib grafiğini PNG formatında base64 string'e dönüştürür."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)  # Bellek sızıntısını önlemek için figürü kapat
    return base64.b64encode(buf.getvalue()).decode()


def generate_report_html(child_info, family_info, child_answers, teacher_info, analysis_results):
    """
    Tüm toplanan veriler ve analiz sonuçlarını kullanarak indirilebilir HTML rapor içeriğini oluşturur.
    """
    child_name = child_info.get("name", "Küçük Kaşif")
    child_surname = child_info.get("surname", "")
    child_dob = child_info.get("dob")
    child_city = child_info.get("city", "bilinmeyen bir şehir")
    child_gender = child_info.get("gender", "Belirtmek İstemiyorum")

    birth_year = child_dob.year if child_dob else "bilinmeyen"
    world_fact = get_world_fact(birth_year)

    # Rapor içindeki grafikler için görsel oluşturma ve base64'e dönüştürme
    # Karakter Tipi Grafiği
    char_labels = list(analysis_results["character_percentages"].keys())
    char_sizes = list(analysis_results["character_percentages"].values())
    fig_char, ax_char = plt.subplots(figsize=(6, 6))
    # Yüzdeleri de etiketlerde göster
    ax_char.pie(char_sizes, labels=[f"{l} ({s:.1f}%)" for l, s in zip(char_labels, char_sizes)],
                autopct='', startangle=90, colors=plt.cm.Paired.colors, textprops={'fontsize': 10})
    ax_char.axis('equal')  # Oranların eşit olmasını sağlar
    ax_char.set_title('Karakter Özellikleri Dağılımı', color='#333', fontsize=14)
    char_img_base64 = plot_to_base64(fig_char)

    # Algılama Becerileri Grafiği
    perc_labels = list(analysis_results["perception_percentages"].keys())
    perc_values = list(analysis_results["perception_percentages"].values())
    fig_perc, ax_perc = plt.subplots(figsize=(8, 4))
    ax_perc.bar(perc_labels, perc_values, color=['#FF9999', '#66B2FF', '#99FF99'])
    ax_perc.set_ylabel('Yüzde (%)', color='#333', fontsize=12)
    ax_perc.set_title('Algılama Becerileri Yoğunluğu', color='#333', fontsize=14)
    for i, v in enumerate(perc_values):
        ax_perc.text(i, v + 0.5, f"{v:.1f}%", ha='center', va='bottom', fontsize=10)
    perc_img_base64 = plot_to_base64(fig_perc)

    # Tahmini boy ve ünlü karşılaştırması
    predicted_height = predict_height(child_gender, family_info['mother_height'], family_info['father_height'],
                                      [family_info.get('grandpa_m_height'), family_info.get('grandma_m_height'),
                                       family_info.get('grandpa_f_height'), family_info.get('grandma_f_height')])

    famous_person_info = "senin gibi harika potansiyele sahip bir birey"  # Varsayılan
    if predicted_height:
        famous_person_info = get_famous_person_height(predicted_height, 'male' if child_gender == 'Erkek' else 'female')

    # HTML rapor yapısı
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouthSight Gelecek Raporu - {child_name} {child_surname}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 20px;
                background-color: #f4f7f6;
            }}
            .container {{
                max-width: 900px;
                margin: 20px auto;
                background: #fff;
                padding: 30px 40px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            }}
            h1, h2, h3 {{
                color: #2e8b57; /* Koyu yeşil */
                border-bottom: 2px solid #e0ffe0;
                padding-bottom: 10px;
                margin-top: 30px;
            }}
            h1 {{
                text-align: center;
                color: #1a5e37;
                font-size: 2.5em;
                margin-bottom: 20px;
            }}
            h2 {{
                font-size: 1.8em;
            }}
            h3 {{
                font-size: 1.4em;
            }}
            p {{
                margin-bottom: 10px;
            }}
            .intro-section {{
                background-color: #e0ffe0;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                font-style: italic;
                font-size: 1.1em;
                border-left: 5px solid #4CAF50;
            }}
            .section {{
                margin-bottom: 25px;
                padding: 15px;
                background-color: #f9fdf9;
                border-radius: 8px;
                border: 1px solid #eefae1;
            }}
            .highlight {{
                font-weight: 600;
                color: #4CAF50;
            }}
            ul {{
                list-style-type: disc;
                margin-left: 20px;
                padding: 0;
            }}
            li {{
                margin-bottom: 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px dashed #ccc;
                color: #777;
                font-size: 0.9em;
            }}
            .chart-img {{
                display: block;
                max-width: 100%;
                height: auto;
                margin: 20px auto;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>YouthSight Gelecek Raporu</h1>
            <p style="text-align: center; font-size: 1.2em; color: #555;">Sevgili {child_name} {child_surname} için özel olarak hazırlandı.</p>

            <div class="intro-section">
                <p>
                    {world_fact} {birth_year} yılında, efelerin harman olduğu <span class="highlight">{child_city}</span>'de doğdun sevgili <span class="highlight">{child_name}</span>!
                    Senin gibi eş eşsiz bir bireyin potansiyelini keşfetmek için çıktığımız bu yolculukta edindiğimiz
                    bilgilerle, sana özel bir gelecek haritası oluşturduk. Unutma, bu bir rehberdir ve senin
                    geleceğin, kararların ve tutkunla şekillenecektir!
                </p>
            </div>

            <div class="section">
                <h2>Karakter Tipin: <span class="highlight">{analysis_results["character_type"]}</span></h2>
                <p>{analysis_results["character_description"]}</p>
                <p>Örneğin, <span class="highlight">{analysis_results["character_example"]}</span> gibi bir kişilikle benzer özellikler taşıyor olabilirsin.</p>
                <img src="data:image/png;base64,{char_img_base64}" alt="Karakter Özellikleri Dağılımı" class="chart-img">
            </div>

            <div class="section">
                <h2>Müzik Enstrümanı Yatkınlıkların</h2>
                <p>Seslere olan duyarlılığın ve parmak yapın incelendiğinde, aşağıdaki enstrümanlara karşı doğal bir yatkınlığın olduğu görülüyor:</p>
                <ul>
                    {''.join([f'<li>{inst}</li>' for inst in analysis_results["instrument_aptitudes"]])}
                </ul>
            </div>

            <div class="section">
                <h2>Algılama Becerilerin</h2>
                <p>Öğrenme stilin ve dünyayı algılama şeklin, özellikle <span class="highlight">{analysis_results["perception_skills"]["dominant"]}</span> alanında güçlü olabilir. {analysis_results["perception_skills"]["description"]}</p>
                <img src="data:image/png;base64,{perc_img_base64}" alt="Algılama Becerileri Yoğunluğu" class="chart-img">
            </div>

            <div class="section">
                <h2>Fiziksel Gelişim Tahminleri</h2>
                <p>
                    Genetik mirasın ve güncel verilerin ışığında, yetişkin boyunun tahmini olarak
                    <span class="highlight">{predicted_height} cm</span>
                    civarında olması bekleniyor. Bu, seni
                    <span class="highlight">{famous_person_info}</span>
                    gibi birçok ünlü isimle aynı boyda yapabilir!
                </p>
                <p>
                    <span class="highlight">Kilo Yatkınlığı:</span> {analysis_results["weight_tendency"]}
                </p>
                <p>
                    <span class="highlight">Spor Yatkınlığı:</span> Enerjini ve fiziksel yeteneklerini kullanabileceğin sporlar arasında:
                    <ul>
                        {''.join([f'<li>{sport}</li>' for sport in analysis_results["sport_aptitude"]])}
                    </ul>
                </p>
            </div>

            <div class="section">
                <h2>Mesleki Yatkınlık Tahminleri</h2>
                <p>İlgi alanların ve yeteneklerin doğrultusunda, gelecekte aşağıdaki meslek dallarında mutlu ve başarılı olabilirsin:</p>
                <ul>
                    {''.join([f'<li>{prof}</li>' for prof in analysis_results["profession_aptitude"]])}
                </ul>
            </div>

            <div class="section">
                <h2>Gelecekteki Çocuğun (Eğer Olursa)</h2>
                <p>Genetik bilgilerine göre, ilk çocuğunun cinsiyeti ve göz rengi için bazı tahminlerimiz var:</p>
                <ul>
                    <li><span class="highlight">İlk Çocuğunun Cinsiyeti:</span>
                        {''.join([f'{gender}: {chance} ' for gender, chance in predict_first_child_gender(family_info.get('mother_first_child_gender'), family_info.get('father_first_child_gender')).items()])}
                    </li>
                    <li><span class="highlight">Muhtemel Göz Rengi:</span>
                        {''.join([f'{color}: {chance} ' for color, chance in predict_eye_color_chance(
        [child_info.get('eye_color'), family_info.get('mother_eye_color'), family_info.get('father_eye_color'),
         family_info.get('grandpa_m_eye_color'), family_info.get('grandma_m_eye_color'),
         family_info.get('grandpa_f_eye_color'), family_info.get('grandma_f_eye_color')]
    ).items()])}
                    </li>
                </ul>
                <p style="font-size:0.9em; color:#777;">*Bu tahminler, genetik kalıtımın basitleştirilmiş bir modeline dayanmaktadır ve kesinlik içermez.</p>
            </div>

            {f'''
            <div class="section">
                <h2>Öğretmen Görüşleri (Eklenmiştir)</h2>
                <p><span class="highlight">Öğretmenin Adı:</span> {teacher_info.get("teacher_name", "Belirtilmemiş")}</p>
                <p><span class="highlight">Genel Performans:</span> {teacher_info.get("general_performance", "Belirtilmemiş")}</p>
                <p><span class="highlight">Sosyal Beceriler:</span> {teacher_info.get("social_skills", "Belirtilmemiş")}</p>
                <p><span class="highlight">Öğrenme Stili:</span> {teacher_info.get("learning_style", "Belirtilmemiş")}</p>
                <p><span class="highlight">Sanatsal Yatkınlıklar:</span> {teacher_info.get("artistic_aptitudes", "Belirtilmemiş")}</p>
                <p><span class="highlight">Fiziksel Yatkınlıklar:</span> {teacher_info.get("physical_aptitude", "Belirtilmemiş")}</p>
            </div>
            ''' if st.session_state.show_teacher_section else ''}

            <div class="footer">
                <p>Bu rapor YouthSight tarafından tüm çocukların geleceği için gönüllü geliştirilmiştir. 💙</p>
                <p>&copy; {datetime.date.today().year} YouthSight. Tüm Hakları Saklıdır.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


def page_report():
    """Raporun görüntülenip indirileceği sayfayı gösterir."""
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🎉 YouthSight Gelecek Raporu 🎉</h1>",
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Potansiyelini Keşfetmenin Tam Zamanı!</h3>",
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tüm verileri kullanarak analiz sonuçlarını al
    analysis_results = analyze_character_and_aptitude(
        st.session_state.family_info,
        st.session_state.child_answers,
        st.session_state.teacher_info if st.session_state.show_teacher_section else {}
        # Öğretmen bölümü aktifse bilgiyi gönder
    )

    child_name = st.session_state.child_info.get("name", "Sevgili Çocuk")
    child_surname = st.session_state.child_info.get("surname", "")
    child_dob = st.session_state.child_info.get("dob")
    child_city = st.session_state.child_info.get("city", "bir şehir")
    child_gender = st.session_state.child_info.get("gender", "Belirtmek İstemiyorum")

    # Raporu oluşturmak için gerekli temel bilgilerin kontrolü
    # Bu kontrol, "Raporu Göster" butonunda da yapıldığı için burada sadece
    # hata durumunda kullanıcıyı yönlendirmek için bir uyarı gösterebiliriz.
    if not (child_name and st.session_state.family_info.get(
            'mother_height') is not None and st.session_state.child_answers):
        st.error(
            "Raporu görüntülemek için lütfen tüm 'Çocuğun Bilgileri', 'Aile Bilgileri' ve 'Çocuğun Soruları' bölümlerini eksiksiz doldurunuz. Anasayfaya dönmek için soldaki menüyü kullanabilirsiniz.")
        return  # Hatalı durumda raporu oluşturmayı durdur.

    birth_year = child_dob.year if child_dob else "bilinmeyen"
    world_fact = get_world_fact(birth_year)

    st.markdown(f"""
    <div style="background-color:#e0ffe0; padding:15px; border-radius:10px; margin-top:20px; text-align: center;">
        <p style="font-size:1.2em; color:#333; font-weight:bold;">
            {world_fact} {birth_year} yılında, efelerin harman olduğu <span style="color:#4CAF50; font-weight:bolder;">{child_city}</span>'de doğdun sevgili <span style="color:#4CAF50; font-weight:bolder;">{child_name}</span>!
            Senin gibi eş eşsiz bir bireyin potansiyelini keşfetmek için çıktığımız bu yolculukta edindiğimiz
            bilgilerle, sana özel bir gelecek haritası oluşturduk.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # st.info ve st.success için unsafe_allow_html parametresi kaldırıldı.
    # İçerik markdown formatına dönüştürüldü.
    st.info(
        f"Sen bir **{analysis_results['character_type']}**'sın! {analysis_results['character_description']} Örneğin, **{analysis_results['character_example']}** gibi bir kişilikle benzer özellikler taşıyor olabilirsin.",
        icon="💡"
    )

    # Karakter Tipi Grafiği
    st.subheader("Karakter Özellikleri Dağılımın")
    df_char = pd.DataFrame(analysis_results["character_percentages"].items(), columns=['Özellik', 'Yüzde'])
    fig_char, ax_char = plt.subplots(figsize=(6, 6))
    ax_char.pie(df_char['Yüzde'], labels=[f"{l} ({s:.1f}%)" for l, s in zip(df_char['Özellik'], df_char['Yüzde'])],
                autopct='', startangle=90, colors=plt.cm.viridis.colors, textprops={'fontsize': 10})
    ax_char.axis('equal')
    st.pyplot(fig_char)

    st.markdown("### Müzik Enstrümanı Yatkınlıkların")
    for inst in analysis_results["instrument_aptitudes"]:
        st.success(f"- {inst}", icon="🎵")

    st.markdown("### Algılama Becerilerin")
    st.info(
        f"Öğrenme stilin ve dünyayı algılama şeklin, özellikle **{analysis_results['perception_skills']['dominant']}** alanında güçlü olabilir. {analysis_results['perception_skills']['description']}",
        icon="🧠"
    )

    # Algılama Becerileri Grafiği
    st.subheader("Algılama Becerileri Yoğunluğun")
    df_perc = pd.DataFrame(analysis_results["perception_percentages"].items(), columns=['Beceriler', 'Yüzde'])
    fig_perc, ax_perc = plt.subplots(figsize=(8, 4))
    ax_perc.bar(df_perc['Beceriler'], df_perc['Yüzde'], color=['#FFD700', '#ADD8E6', '#98FB98'])
    ax_perc.set_ylabel('Yüzde (%)')
    for i, v in enumerate(df_perc['Yüzde']):
        ax_perc.text(i, v + 0.5, f"{v:.1f}%", ha='center', va='bottom', fontsize=10)
    st.pyplot(fig_perc)

    st.markdown("### Fiziksel Gelişim Tahminleri")
    predicted_height = predict_height(child_gender, st.session_state.family_info['mother_height'],
                                      st.session_state.family_info['father_height'],
                                      [st.session_state.family_info.get('grandpa_m_height'),
                                       st.session_state.family_info.get('grandma_m_height'),
                                       st.session_state.family_info.get('grandpa_f_height'),
                                       st.session_state.family_info.get('grandma_f_height')])

    famous_person_info = "senin gibi harika potansiyele sahip bir birey"  # Varsayılan
    if predicted_height:
        famous_person_info = get_famous_person_height(predicted_height, 'male' if child_gender == 'Erkek' else 'female')

    st.info(
        f"Tahmini yetişkin boyun **{predicted_height} cm** civarında olması bekleniyor. Bu, seni **{famous_person_info}** gibi birçok ünlü isimle aynı boyda yapabilir!",
        icon="📏"
    )
    st.info(
        f"**Kilo Yatkınlığı:** {analysis_results['weight_tendency']}",
        icon="⚖️"
    )

    st.subheader("Spor Yatkınlıkların")
    for sport in analysis_results["sport_aptitude"]:
        st.success(f"- {sport}", icon="⚽")

    st.markdown("### Mesleki Yatkınlık Tahminleri")
    for prof in analysis_results["profession_aptitude"]:
        st.success(f"- {prof}", icon="💼")

    st.markdown("### Gelecekteki Çocuğun (Eğer Olursa)")
    st.info(
        f"**İlk Çocuğunun Cinsiyeti:** {', '.join([f'{gender}: {chance}' for gender, chance in predict_first_child_gender(st.session_state.family_info.get('mother_first_child_gender'), st.session_state.family_info.get('father_first_child_gender')).items()])}",
        icon="👶"
    )
    st.info(
        f"**Muhtemel Göz Rengi:** {', '.join([f'{color}: {chance}' for color, chance in predict_eye_color_chance(
            [st.session_state.child_info.get('eye_color'), st.session_state.family_info.get('mother_eye_color'), st.session_state.family_info.get('father_eye_color'),
             st.session_state.family_info.get('grandpa_m_eye_color'), st.session_state.family_info.get('grandma_m_eye_color'),
             st.session_state.family_info.get('grandpa_f_eye_color'), st.session_state.family_info.get('grandma_f_eye_color')]
        ).items()])}",
        icon="👁️"
    )
    st.markdown(
        "<p style='font-size:0.8em; color:#777;'>*Bu tahminler, genetik kalıtımın basitleştirilmiş bir modeline dayanmaktadır ve kesinlik içermez.</p>",
        unsafe_allow_html=True)

    if st.session_state.show_teacher_section:
        st.markdown("### Öğretmen Görüşleri (Eklenmiştir)")
        st.write(f"**Öğretmenin Adı:** {st.session_state.teacher_info.get('teacher_name', 'Belirtilmemiş')}")
        st.write(f"**Genel Performans:** {st.session_state.teacher_info.get('general_performance', 'Belirtilmemiş')}")
        st.write(f"**Sosyal Becerileri:** {st.session_state.teacher_info.get('social_skills', 'Belirtilmemiş')}")
        st.write(f"**Öğrenme Stili:** {st.session_state.teacher_info.get('learning_style', 'Belirtilmemiş')}")
        st.write(
            f"**Sanatsal Yatkınlıkları:** {st.session_state.teacher_info.get('artistic_aptitudes', 'Belirtilmemiş')}")
        st.write(
            f"**Fiziksel Yatkınlıkları:** {st.session_state.teacher_info.get('physical_aptitude', 'Belirtilmemiş')}")

    st.markdown("---")
    st.markdown(
        "<h3 style='text-align: center; color: #4CAF50;'>Bu rapor YouthSight tarafından tüm çocukların geleceği için gönüllü geliştirilmiştir. 💙</h3>",
        unsafe_allow_html=True)

    # Raporu HTML olarak indirme butonu
    report_html = generate_report_html(
        st.session_state.child_info,
        st.session_state.family_info,
        st.session_state.child_answers,
        st.session_state.teacher_info,
        analysis_results
    )

    st.download_button(
        label="Raporu HTML Olarak İndir",
        data=report_html,
        file_name=f"YouthSight_Rapor_{child_name}_{child_surname}.html",
        mime="text/html",
        help="Bu raporu bilgisayarınıza HTML dosyası olarak indirin."
    )

    # Uygulamayı yeniden başlatma butonu
    if st.button("Yeniden Başla", help="Yeni bir rapor oluşturmak için uygulamayı yeniden başlatın."):
        st.session_state.clear()  # Tüm session state verilerini temizle
        st.rerun()  # Uygulamayı yeniden başlat


# --- Ana Uygulama Akışı ---
# Sidebar menüsü
with st.sidebar:
    st.markdown("## YouthSight Menü")
    if st.button("Anasayfa", key="nav_intro"):
        st.session_state.current_page = 'intro'
        st.rerun()
    if st.button("Çocuğun Bilgileri", key="nav_personal"):
        st.session_state.current_page = 'personal_info'
        st.rerun()
    if st.button("Aile Bilgileri", key="nav_family"):
        st.session_state.current_page = 'family_info'
        st.rerun()
    if st.button("Çocuğun Soruları", key="nav_child_q"):
        st.session_state.current_page = 'child_questions'
        st.rerun()

    st.markdown("---")
    # Öğretmen görüşleri bölümünü aktif etme/kapatma checkbox'ı
    st.session_state.show_teacher_section = st.checkbox("Öğretmen Görüşlerini Ekle",
                                                        value=st.session_state.show_teacher_section,
                                                        help="İsteğe bağlı olarak öğretmen görüşlerini raporunuza dahil edebilirsiniz.")
    if st.session_state.show_teacher_section:
        st.markdown("### Öğretmen Bilgileri")
        with st.form("teacher_info_form_sidebar", clear_on_submit=False):
            # Öğretmen bilgileri giriş alanları
            st.session_state.teacher_info['teacher_name'] = st.text_input("Öğretmenin Adı Soyadı",
                                                                          value=st.session_state.teacher_info.get(
                                                                              'teacher_name', ''),
                                                                          help="Öğretmenin adı ve soyadı.")

            # DÜZELTME: selectbox için index hesabı
            general_performance_options = ["Seçiniz", "Çok İyi", "İyi", "Orta", "Geliştirilmeli"]
            default_general_performance = st.session_state.teacher_info.get('general_performance', 'Seçiniz')
            try:
                default_general_performance_index = general_performance_options.index(default_general_performance)
            except ValueError:
                default_general_performance_index = 0

            st.session_state.teacher_info['general_performance'] = st.selectbox("Okuldaki Genel Performans",
                                                                                general_performance_options,
                                                                                index=default_general_performance_index,
                                                                                help="Çocuğun okuldaki genel akademik performansı.")

            st.session_state.teacher_info['social_skills'] = st.text_area("Sosyal Becerileri Hakkında",
                                                                          value=st.session_state.teacher_info.get(
                                                                              'social_skills', ''), height=70,
                                                                          help="Çocuğun sosyal etkileşimleri ve arkadaşlık ilişkileri hakkında gözlemler.")
            st.session_state.teacher_info['learning_style'] = st.text_area("Öğrenme Stili Hakkında",
                                                                           value=st.session_state.teacher_info.get(
                                                                               'learning_style', ''), height=70,
                                                                           help="Çocuğun öğrenmeyi tercih ettiği yöntemler (görsel, işitsel, kinestetik).")
            st.session_state.teacher_info['artistic_aptitudes'] = st.text_area("Sanatsal Yatkınlıkları Hakkında",
                                                                               value=st.session_state.teacher_info.get(
                                                                                   'artistic_aptitudes', ''), height=70,
                                                                               help="Çocuğun sanatsal faaliyetlere ilgisi ve yetenekleri.")
            st.session_state.teacher_info['physical_aptitude'] = st.text_area("Fiziksel Yatkınlıkları Hakkında",
                                                                              value=st.session_state.teacher_info.get(
                                                                                  'physical_aptitude', ''), height=70,
                                                                              help="Çocuğun fiziksel aktivitelere ve sporlara olan yatkınlığı.")

            # Öğretmen bilgilerini kaydetme butonu - DÜZELTME: key kaldırıldı
            if st.form_submit_button("Öğretmen Bilgilerini Kaydet"):
                st.success("Öğretmen bilgileri kaydedildi!")

    st.markdown("---")
    # Raporu göster butonu (Tüm zorunlu alanlar doldurulmuşsa aktif olur)
    if st.session_state.current_page != 'report':  # Rapor sayfasında zaten bu butona gerek yok
        if st.button("Raporu Göster", key="nav_report"):
            # Rapor oluşturmadan önce temel zorunlu bilgilerin kontrolü
            if st.session_state.child_info.get('name') and st.session_state.family_info.get(
                    'mother_height') is not None and st.session_state.child_answers:  # st.session_state.child_answers boş dictionary ise false döner
                st.session_state.current_page = 'report'
                st.rerun()
            else:
                st.warning(
                    "Raporu oluşturmak için 'Çocuğun Bilgileri', 'Aile Bilgileri' ve 'Çocuğun Soruları' bölümlerini tamamlayınız!")

# Sayfa yönlendirme mantığı
if st.session_state.current_page == 'intro':
    page_intro()
elif st.session_state.current_page == 'personal_info':
    page_personal_info()
elif st.session_state.current_page == 'family_info':
    page_family_info()
elif st.session_state.current_page == 'child_questions':
    page_child_questions()
elif st.session_state.current_page == 'report':
    page_report()