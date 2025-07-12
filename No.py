from datetime import datetime

class No:
    def __init__(self, data, hora, localizacao, bateria, memoria_int, memoria_ext,
                 wifi, bluetooth, conexao, p2p, roteadores):
        self.timestamp = datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M:%S")
        self.latitude, self.longitude = map(float, localizacao.split(','))
        self.bateria = int(bateria)
        self.memoria_int = int(memoria_int)
        self.memoria_ext = int(memoria_ext)
        self.wifi = wifi.upper() == "ON"
        self.bluetooth = bluetooth.upper() == "ON"
        self.conexao = conexao.upper()  # "WIFI" ou "BLUETOOTH"
        self.p2p = p2p.upper() == "SUPORTE"
        self.roteadores = roteadores.split()

    def distancia_para(self, outro_no):
        # Fórmula de Haversine (em metros)
        from math import radians, sin, cos, sqrt, atan2
        R = 6371000  # Raio da Terra em metros
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(outro_no.latitude), radians(outro_no.longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def pode_comunicar(self, outro_no, raio=10):
        return self.distancia_para(outro_no) <= raio

    def __str__(self):
        return f"[{self.timestamp}] ({self.latitude}, {self.longitude}) | Bateria: {self.bateria}% | Roteadores: {len(self.roteadores)}"

