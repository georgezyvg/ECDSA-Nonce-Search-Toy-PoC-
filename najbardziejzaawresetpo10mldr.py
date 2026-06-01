import random
import hashlib
from multiprocessing import Pool

# Ustal zmienną n i G (stałe używane w generowaniu podpisów)
n = 1000000000000  # Przyklad wartości, zaktualizuj odpowiednio
G = (1, 2)  # Przykładowa wartość G (można ustawić odpowiednią stałą)

MAX_HISTORY = 5000  # Maksymalna liczba przechowywanych wartości w historii
CHANGE_STRATEGY_AFTER = 10000  # Liczba prób po której zmieniamy strategię
TARGET_ADDRESS = "1Pzaqw98PeRfyHypfqyEgg5yycJRsENrE7"  # Adres docelowy, zmień na odpowiedni

def mod_inv(k, n):
    """Zwraca odwrotność modulo n dla liczby k."""
    return pow(k, -1, n)

def generate_public_key(d):
    """Generuje klucz publiczny z prywatnego klucza."""
    # Zastąp odpowiednią metodą generowania klucza publicznego
    return (d * G[0], d * G[1])

def public_key_to_address(pub_key):
    """Generuje adres z klucza publicznego."""
    pub_key_hash = hashlib.sha256(f"{pub_key[0]}{pub_key[1]}".encode()).hexdigest()
    return pub_key_hash[:34]  # Skracamy do 34 znaków (przykład)

def log_message(message):
    """Loguje komunikaty do konsoli."""
    print(message)

def generate_signature(z, k, priv_key):
    """Generuje podpis na podstawie z, k i prywatnego klucza."""
    try:
        z = int(z, 16)  # Konwertujemy z na int z podstawą 16, jeśli jest w formacie heksadecymalnym
    except ValueError:
        z = int(z)  # Jeśli nie w formacie heksadecymalnym, konwertujemy na int
    priv_key = int(priv_key)  # Konwertujemy priv_key na int, jeśli jest w innym typie
    
    R = k * G
    r = R[0] % n  # Możesz dostosować ten kod do właściwego przekształcenia
    if r == 0:
        return None
    k_inv = mod_inv(k, n)
    s = (k_inv * (z + priv_key * r)) % n
    return r, s

def find_matching_dk(target_r, target_s, target_z, max_attempts=10_000_000_000):
    """Funkcja do wyszukiwania pasujących kluczy prywatnych i k."""
    last_k_values = []
    last_r_values = []
    last_s_values = []
    last_successful_attempt = 0  # 🟢 Licznik udanych prób

    try:
        target_z = int(target_z, 16)  # Jeśli 'target_z' jest w formacie heksadecymalnym
    except ValueError:
        target_z = int(target_z)  # Jeśli jest w innym formacie, np. dziesiętnym

    for attempt in range(max_attempts):  
        k = predict_k(last_k_values, last_r_values, last_s_values)  # 🧠 Inteligentna predykcja k
        d = random.randint(1, n - 1)  # 🔄 Losowe d
        
        r, s = generate_signature(target_z, k, d)

        if r is not None:
            last_k_values.append(k)
            last_r_values.append(r)
            last_s_values.append(s)  

            # 🛠 **Ogranicz historię do ostatnich 5000 wartości**
            if len(last_k_values) > MAX_HISTORY:
                last_k_values.pop(0)
                last_r_values.pop(0)
                last_s_values.pop(0)

            # 🔹 Generowanie klucza publicznego i adresu
            pub_key = generate_public_key(d)
            btc_address = public_key_to_address(pub_key)

            # ✅ Jeśli znaleziono `d` i `k`, lub adres pasuje → natychmiast kończymy
            if r == target_r and s == target_s:
                log_message(f"🎯 ZNALEZIONO KLUCZ! d={d}, k={k}, Adres: {btc_address} 🔥")
                return d, k
            if btc_address == TARGET_ADDRESS:
                log_message(f"🚀 ODNALEZIONO ADRES BTC! Klucz prywatny: {d}")
                return d, k

        # 🔥 Wyświetlanie postępu na CMD
        print(f"🔍 Próba: {attempt} | r={r} | s={s} | k={k} | d={d} | Adres BTC: {btc_address}", flush=True)

        # 🔥 **Co 10 000 prób sprawdzamy, czy nie zmienić podejścia**
        if attempt - last_successful_attempt >= CHANGE_STRATEGY_AFTER:
            log_message("⚠️ Brak postępu przez 10 tys. prób. Resetujemy historię `k`!")
            last_k_values.clear()
            last_r_values.clear()
            last_s_values.clear()
            last_successful_attempt = attempt  # Resetujemy licznik

    log_message("❌ Nie znaleziono poprawnego d i k po 10 miliardach prób.")
    return None

def predict_k(last_k_values, last_r_values, last_s_values):
    """Funkcja predykcji wartości k. Można ją dostosować do własnych potrzeb."""
    # Możesz dodać logikę predykcji dla wartości k
    return random.randint(1, n - 1)  # Przykład: Zwracamy losową wartość k

def parallel_test(transactions):
    """Funkcja uruchamiająca testy w trybie równoległym (wielowątkowym)."""
    with Pool(2) as pool:  # Używamy 2 rdzeni CPU
        results = pool.starmap(find_matching_dk, transactions)
    return results

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()

    # Przykład transakcji do przetestowania (dostosuj odpowiednio)
    transactions = [
        {'r': 48259776657482972121863282466509055391675982679826884801798922453868026069996, 
         's': 53422607810948748305532674833994360795165858803566993820393912929887181393701, 
         'z': 41391649967855740095700478609281123688204997485532650944128529845722245907827},
        {'r': 48265422635030361957275252738222519330664496583487536488632604074884250041205, 
         's': 47471887450888063686920101581846566648958956497361646921214909643586524848004, 
         'z': 109956901347953313945622426596048482259482512422053973719472349892406755586857}
    ]

    # Uruchamiamy testy równoległe
    results = parallel_test(transactions)
